from flask import Blueprint, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file (do NOT push .env to GitHub)
load_dotenv()

# ⚠️ Get GitHub Personal Access Token from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/", methods=["POST"])
def chat():
    try:
        # Validate Token
        if not GITHUB_TOKEN or not GITHUB_TOKEN.startswith("github_pat_"):
            return jsonify({"error": "Server configuration error: Invalid API Token"}), 500

        data = request.get_json(force=True)
        user_message = data.get("message", "").strip()

        # Auto Greeting if message is empty
        if not user_message:
            return jsonify({
                "reply": (
                    "Hello! I am WanderAI, your professional virtual travel assistant. "
                    "I am here to assist you with destination discovery, travel planning, "
                    "and VR-based tour recommendations. How may I assist you with your travel inquiries today?"
                )
            })

        # System prompt for AI
        system_prompt = (
            "You are WanderAI, a highly professional virtual travel assistant. "
            "Your role is to strictly assist with tourism, travel planning, destinations, "
            "and Wander AI's VR tours. "
            "If a user asks about anything unrelated to travel, politely decline and state that you only answer travel-related queries. "
            "Formatting rules: Write in clear, professional paragraphs. "
            "Do not use markdown symbols or emojis unless necessary. Structure logically."
        )

        # API Endpoint
        url = "https://models.inference.ai.azure.com/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {GITHUB_TOKEN}"}
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 800,
            "top_p": 1.0
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            try:
                response_text = result['choices'][0]['message']['content']
                # Clean any markdown artifacts
                response_text = response_text.replace("**", "").replace("### ", "").replace("## ", "").replace("# ", "")
                return jsonify({"reply": response_text.strip()})
            except (KeyError, IndexError) as e:
                return jsonify({"error": "AI Service Error: Unexpected response format"}), 502
        elif response.status_code == 429:
            return jsonify({"reply": "Too many requests. Please try again in 60 seconds."})
        elif response.status_code == 401:
            return jsonify({"error": "Unauthorized. Invalid Token."}), 401
        else:
            return jsonify({"error": f"AI Service Error: {response.status_code}"}), 502

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500