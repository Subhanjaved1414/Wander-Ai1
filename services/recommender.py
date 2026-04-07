from flask import Blueprint, request, jsonify

from sklearn.preprocessing import LabelEncoder, MinMaxScaler

import pandas as pd

import numpy as np

import joblib

import os

import sys



recommender_bp = Blueprint("recommender", __name__)



# --- Configuration & Model Paths ---

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "high_accuracy_recommender_filter.pkl")

ENCODER_PATH = os.path.join(BASE_DIR, "temp_encoder.pkl")

DATA_PATH = os.path.join(BASE_DIR, "preprocessing", "Tourist_Destinations.csv")

PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "preprocessing", "processed_dataset.csv")



print(f"🔍 Looking for files in: {BASE_DIR}")



# Global singleton for the recommender system

recommender_system = None



class RecommenderSystem:

    def __init__(self):

        self.xgb_model = None

        self.le_type = None

        self.scaler = None

        self.processed_features_df = None

        self.original_data = None

        self.expected_feature_order = None

        self.season_encoded_map = {'Winter': 0, 'Spring': 1, 'Autumn': 2, 'Summer': 3}

        self.is_initialized = False

        self.init_error = None



    def initialize(self):

        if self.is_initialized:

            return

       

        try:

            print("📊 Lazy loading data and models...")

            # --- Load Data & Assets ---

            self.original_data = pd.read_csv(DATA_PATH)

           

            # Load ML Model

            self.xgb_model = joblib.load(MODEL_PATH)

           

            # Handle LabelEncoder

            try:

                loaded_obj = joblib.load(ENCODER_PATH)

                if hasattr(loaded_obj, 'fit') and hasattr(loaded_obj, 'transform'):

                    self.le_type = loaded_obj

                else:

                    raise ValueError("Loaded object is not a valid LabelEncoder")

            except Exception:

                self.le_type = LabelEncoder()

                self.le_type.fit(self.original_data['Type'].astype(str))

           

            # --- Preprocessing for Ranking ---

            # 1. Feature Engineering

            self.original_data['Cost_vs_Visitors'] = self.original_data['Avg Cost (USD/day)'] / (self.original_data['Annual Visitors (M)'] + 1e-6)

            self.original_data['Type_Encoded'] = self.le_type.transform(self.original_data['Type'].astype(str))

            self.original_data['Synthetic_Predictor'] = self.original_data['Type_Encoded'] + np.random.uniform(-0.01, 0.01, size=len(self.original_data))



            # 2. Encoding

            data_for_processing = self.original_data.copy()

            ohe_cols = ['Country', 'Continent']

            le_cols = ['Best Season', 'UNESCO Site']

           

            for col in le_cols:

                le_f = LabelEncoder()

                data_for_processing[col] = le_f.fit_transform(data_for_processing[col].astype(str))



            data_for_processing = pd.get_dummies(data_for_processing, columns=ohe_cols)

           

            # 3. Scaling

            scaling_cols = ['Avg Cost (USD/day)', 'Avg Rating', 'Annual Visitors (M)', 'Cost_vs_Visitors', 'Synthetic_Predictor']

            self.scaler = MinMaxScaler()

            data_for_processing[scaling_cols] = self.scaler.fit_transform(data_for_processing[scaling_cols])



            # 4. Final Feature List (CRITICAL: Must match training)

            if hasattr(self.xgb_model, 'feature_names_in_'):

                self.expected_feature_order = self.xgb_model.feature_names_in_.tolist()

            else:

                # Fallback to the known required order if feature_names_in_ is missing

                cols_to_drop = ['Destination Name', 'Type', 'Type_Encoded']

                core_features_in_order = [

                    'Avg Cost (USD/day)', 'Best Season', 'Avg Rating', 'Annual Visitors (M)',

                    'UNESCO Site', 'Synthetic_Predictor', 'Cost_vs_Visitors'

                ]

                remaining_cols = [col for col in data_for_processing.columns if col not in (core_features_in_order + cols_to_drop)]

                remaining_cols.sort()

                self.expected_feature_order = core_features_in_order + remaining_cols



            # Create the DataFrame containing features for ALL destinations

            self.processed_features_df = data_for_processing[self.expected_feature_order]

           

            # Rename for cleaner output

            self.original_data.rename(columns={"Avg Cost (USD/day)": "Cost"}, inplace=True)

           

            self.is_initialized = True

            print("✅ Recommender initialization complete.")

           

        except Exception as e:

            self.init_error = str(e)

            print(f"❌ FATAL ERROR during initialization: {e}")

            raise e



# Initialize the global instance

recommender_system = RecommenderSystem()



# ================== Dynamic XGBoost Ranking Function ==================



def get_dynamic_recommendations(budget, season, type_preference, top_n=5):

    """

    Ranks destinations dynamically by injecting user preference (Type) into the input features

    before prediction and adding a random exploration factor.

    """

    try:

        # Lazy initialization check

        if not recommender_system.is_initialized:

            recommender_system.initialize()



        if recommender_system.xgb_model is None or recommender_system.processed_features_df is None:

            return {"error": "Recommendation system not initialized or data is missing."}

           

        # --- 1. Filter Destinations by User Input (Budget & Season) ---

       

        # Filter by budget and exact season match

        filtered_indices = recommender_system.original_data[

            (recommender_system.original_data["Cost"] <= budget) &

            (recommender_system.original_data["Best Season"] == season)

        ].index

       

        # Fallback: Filter by budget only if no exact season match is found

        if filtered_indices.empty:

             filtered_indices = recommender_system.original_data[

                (recommender_system.original_data["Cost"] <= budget)

             ].index

       

        if filtered_indices.empty:

            return {"recommendation": f"No destinations found matching Budget ${budget}."}



        # Select features for the valid destinations

        features_to_rank = recommender_system.processed_features_df.loc[filtered_indices].copy()

       

        # --- 2. Dynamic Feature Injection (Personalization) ---

       

        # 2a. Encode the user's preferred Type

        try:

            # Get the encoded value for the user's Type preference

            user_type_encoded = recommender_system.le_type.transform([type_preference.capitalize()])[0]

        except ValueError:

            user_type_encoded = recommender_system.original_data['Type_Encoded'].mean() # Use average as fallback



        # 2b. Calculate the dynamic Synthetic_Predictor value

        dynamic_synthetic_value = user_type_encoded + np.random.uniform(-0.01, 0.01)

       

        # Define scaling columns for safe scaling

        scaling_cols = ['Avg Cost (USD/day)', 'Avg Rating', 'Annual Visitors (M)', 'Cost_vs_Visitors', 'Synthetic_Predictor']

        synth_index = scaling_cols.index('Synthetic_Predictor')



        # Scale the new synthetic value using the pre-fitted scaler

        mock_row_for_scaling = [0] * len(scaling_cols)

        mock_row_for_scaling[synth_index] = dynamic_synthetic_value

        dynamic_synthetic_scaled = recommender_system.scaler.transform([mock_row_for_scaling])[0, synth_index]



        # 2c. Inject the dynamic feature into ALL rows of the prediction matrix

        features_to_rank['Synthetic_Predictor'] = dynamic_synthetic_scaled

       

        # --- 3. Predict Scores and Add Exploration Noise ---

        scores = recommender_system.xgb_model.predict(features_to_rank)

       

        # --- FINAL FIX: Add small random noise for exploration/diversity (The "Realness" Factor) ---

        # The noise range (e.g., 0.001) should be much smaller than the variance of the predicted scores.

        EXPLORATION_NOISE = np.random.uniform(-0.001, 0.001, size=len(scores))

        scores_with_noise = scores + EXPLORATION_NOISE

       

        # --- 4. Rank and Format ---

        ranking_data = recommender_system.original_data.loc[features_to_rank.index].copy()

        ranking_data['Score'] = scores_with_noise

       

        recommendations = ranking_data.sort_values(

            by=["Score"], ascending=False

        ).head(top_n)



        # Rename columns for frontend display

        result = recommendations[[

            "Destination Name",

            "Country",

            "Type",

            "Cost",

            "Best Season"

        ]].rename(columns={

            "Destination Name": "Destination",

            "Best Season": "Season"

        }).to_dict(orient="records")

       

        print(f"✅ Generated {len(result)} recommendations")

        return result

       

    except Exception as e:

        print(f"❌ Error in ranking function: {e}")

        return {"error": f"Ranking failed: {str(e)}"}



# ================== API Endpoint ==================

@recommender_bp.route("/", methods=["POST", "OPTIONS"])

def recommend():

    try:

        if request.method == "OPTIONS":

            return jsonify({"status": "ok"})

           

        data = request.get_json()

        if not data:

            return jsonify({"error": "No JSON data received"}), 400

           

        # Extract all inputs from the frontend

        budget = int(data.get("budget", 150))

        season = data.get("season", "Summer")

        type_preference = data.get("type", "City")



        print(f"🎯 Received request - Budget: ${budget}, Season: {season}, Type: {type_preference}")



        results = get_dynamic_recommendations(budget, season, type_preference)



        if isinstance(results, dict) and 'error' in results:

            return jsonify(results), 500

        elif isinstance(results, dict) and 'recommendation' in results:

            return jsonify(results), 200

           

        return jsonify(results)

       

    except Exception as e:

        print(f"❌ Server error: {e}")

        return jsonify({"error": f"Server error: {str(e)}"}), 500



@recommender_bp.route("/health", methods=["GET"])

def recommender_health():

    status = "healthy" if recommender_system and recommender_system.is_initialized else "standby"

    return jsonify({

        "status": status,

        "model_loaded": recommender_system.is_initialized,

        "encoder_loaded": recommender_system.le_type is not None,

        "features_configured": recommender_system.expected_feature_order is not None

    })



@recommender_bp.route("/test", methods=["GET"])

def test_recommendation():

    """Test endpoint to verify the recommendation system works"""

    try:

        results = get_dynamic_recommendations(200, "Summer", "City")

        return jsonify({

            "status": "success",

            "test_results": results

        })

    except Exception as e:

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500