from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

API_KEY = "AIzaSyBy8rbj_Y5shHSBTyCFvJj_xuzGJbx8wdE"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    action = data.get("action", "default")

    # 🧠 Modify prompt based on action
    if action == "code":
        prompt = f"Explain this with code: {user_input}"
    elif action == "diagram":
        prompt = f"Describe this topic with a visual diagram : {user_input}"
    elif action == "quiz":
        prompt = f"Generate 5 multiple choice quiz questions with options and correct answers based on: {user_input}"
    else:
        prompt = user_input

    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, data=json.dumps(body))
        result = response.json()

        if "candidates" in result:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            reply = f"Error: {result.get('error', {}).get('message', 'Unknown error')}"

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Exception occurred: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
