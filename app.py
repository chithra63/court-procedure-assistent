import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types
import chatbot_config

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-secret-key")

# Initialize Gemini Client using google-genai SDK
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if not client:
        return jsonify({"error": "Gemini API key is missing. Please configure your .env file."}), 500

    user_data = request.get_json()
    user_message = user_data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message."}), 400

    try:
        config = types.GenerateContentConfig(
            system_instruction=chatbot_config.SYSTEM_PROMPT,
            temperature=0.2
        )

        response = client.models.generate_content(
            model=chatbot_config.MODEL_NAME,
            contents=user_message,
            config=config
        )

        bot_reply = response.text if response.text else "No response generated."
        return jsonify({"response": bot_reply})

    except Exception as e:
        return jsonify({"error": f"An error occurred while communicating with Gemini API: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
