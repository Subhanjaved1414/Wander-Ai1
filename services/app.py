from flask import Flask, jsonify, send_from_directory
import os
import sys
import traceback

# -------- Paths --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

sys.path.append(BASE_DIR)

app = Flask(__name__, static_folder=FRONTEND_DIR)

# -------- CORS (Manual – Safe & Simple) --------
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

# -------- Register Blueprints --------
try:
    from chatbot import chatbot_bp
    from recommender import recommender_bp

    app.register_blueprint(chatbot_bp, url_prefix="/chat")
    app.register_blueprint(recommender_bp, url_prefix="/recommend")

    print("✅ Blueprints registered successfully")

except Exception:
    print("❌ Blueprint import failed")
    traceback.print_exc()

# -------- Frontend Routes --------
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/recommendation.html")
def recommendation_page():
    return send_from_directory(FRONTEND_DIR, "recommendation.html")

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "Wander AI Backend",
        "port": 5000
    })

@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(FRONTEND_DIR, path)

# -------- Run Server --------
if __name__ == "__main__":
    print("🚀 Wander AI Server Running")
    print("📡 http://127.0.0.1:5000")
    app.run(
        host="127.0.0.1",   # IMPORTANT (fixes connection refused)
        port=5000,
        debug=True,
        threaded=True
    )
