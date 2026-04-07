from flask import Blueprint, request, jsonify
from flask_cors import CORS
import requests

# Reuse the same API token as the main chatbot service
from chatbot import GITHUB_TOKEN

support_bp = Blueprint('support_bot', __name__)
CORS(support_bp)

@support_bp.route('/support_bot', methods=['POST'])
def support_chat():
    try:
        data = request.get_json(force=True)
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({
                'reply': (
                    "Welcome to the Wander AI Support Center. I am your dedicated Support Specialist. "
                    "I can help with account issues, technical difficulties, or general inquiries about our platform. "
                    "How can I assist you today?"
                )
            })

        if not GITHUB_TOKEN or not GITHUB_TOKEN.startswith("github_pat_"):
             return jsonify({"error": "Server configuration error: Invalid API Token"}), 500

        system_prompt = (
                "You are the dedicated Customer Support Specialist for Wander AI. "
                "Your role is to assist users with TECHNICAL ISSUES, ACCOUNT PROBLEMS, and WEBSITE NAVIGATION. "
                "Scope includes password resets, login issues, bug reports, performance problems, and general usage questions. "
                "If a user asks for travel recommendations, politely redirect them to the main travel planner. "
                "Formatting: plain text, no markdown. Tone: empathetic, professional, concise."
            )
        
        # GitHub Models (Azure AI Inference) Endpoint
        url = "https://models.inference.ai.azure.com/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GITHUB_TOKEN}"
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "model": "gpt-4o",
            "temperature": 0.5, # Lower temperature for support
            "max_tokens": 500
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            try:
                response_text = result['choices'][0]['message']['content']
                # Clean any markdown remnants
                response_text = response_text.replace('**', '').replace('### ', '').replace('## ', '').replace('# ', '')
                return jsonify({'reply': response_text.strip()})
            except (KeyError, IndexError):
                return jsonify({'error': "AI Service Error: Unexpected response format"}), 502
        elif response.status_code == 429:
             return jsonify({'reply': "I'm currently receiving too many requests. Please try again in a moment."})
        elif response.status_code == 401:
             return jsonify({"error": "AI Service Error: Unauthorized. Invalid Token."}), 401
        else:
            return jsonify({'error': f"AI Service Error: {response.status_code}"}), 502

    except Exception as e:
        return jsonify({'error': str(e)}), 500
