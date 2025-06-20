from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import json
import os
from auth_routes import auth
from transformers import pipeline
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from collections import Counter

app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = "your-secret-key"
jwt = JWTManager(app)

# 🔐 Users
users = [
    {"username": "student1", "password": "pass", "role": "student"},
    {"username": "teacher1", "password": "pass", "role": "teacher"},
    {"username": "shailesh", "password": "123", "role": "common"}
]

# 💡 In-memory storage
educational_content = []
quizzes = []
gamification = {"badges": [], "points": 0}

# 🤖 Load QA Model
try:
    qa_pipeline = pipeline("question-answering")
except Exception as e:
    qa_pipeline = None
    print(f"Failed to load QA model: {e}")

# 🌐 Gemini API Config
API_KEY = "AIzaSyBy8rbj_Y5shHSBTyCFvJj_xuzGJbx8wdE"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# 🔐 Auth Blueprint
app.register_blueprint(auth, url_prefix='/api/auth')

# --- ROUTES ---

@app.route('/')
def home():
    return 'Welcome to the AI Tutor Backend!', 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = next((u for u in users if u["username"] == data["username"] and u["password"] == data["password"]), None)
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity={"username": user["username"], "role": user["role"]})
    return jsonify(access_token=access_token, role=user["role"])

@app.route('/api/ai-tutor', methods=['POST'])
def ai_tutor():
    data = request.json
    question = data.get('question')
    context = data.get('context', '')
    if not question or not context:
        return jsonify({'error': 'Missing question or context'}), 400
    if not qa_pipeline:
        return jsonify({'error': 'AI model not available'}), 500
    result = qa_pipeline(question=question, context=context)
    return jsonify({'answer': result['answer']})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    action = data.get("action", "default")

    prompt_map = {
        "code": f"Explain this with code: {user_input}",
        "diagram": f"Describe this topic with a visual diagram: {user_input}",
        "quiz": f"Generate 5 multiple choice quiz questions based on: {user_input}"
    }
    prompt = prompt_map.get(action, user_input)

    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, data=json.dumps(body))
        result = response.json()
        if "candidates" in result:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            reply = f"Error: {result.get('error', {}).get('message', 'Unknown error')}"
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Exception occurred: {str(e)}"})

@app.route('/api/content', methods=['GET'])
def get_content():
    # Always use the correct path relative to this file
    data_path = os.path.join(os.path.dirname(__file__), 'course_data.json')
    if os.path.exists(data_path):
        with open(data_path) as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/content', methods=['POST'])
@jwt_required()
def add_content():
    user = get_jwt_identity()
    if user["role"] not in ["teacher", "common"]:
        return jsonify({"msg": "Only teachers or common users can add content."}), 403
    data = request.json
    new_id = len(educational_content) + 1
    item = {"id": new_id, "title": data.get('title'), "body": data.get('body')}
    educational_content.append(item)
    return jsonify(item), 201

@app.route('/api/progress', methods=['POST'])
def log_progress():
    entry = request.get_json()
    file = 'progress.json'
    data = []
    if os.path.exists(file):
        with open(file) as f:
            data = json.load(f)
    data.append(entry)
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)
    return jsonify({'status': 'ok'})

@app.route('/api/analytics')
def analytics():
    if not os.path.exists('progress.json'):
        return jsonify({"views_by_subject": {}, "views_by_topic": {}, "total_views": 0})
    with open('progress.json') as f:
        logs = json.load(f)
    subj_counts = Counter(e['subject'] for e in logs)
    topic_counts = Counter(e['title'] for e in logs)
    return jsonify({
        'total_views': len(logs),
        'views_by_subject': subj_counts,
        'views_by_topic': topic_counts
    })

@app.route('/api/quiz', methods=['GET'])
def get_quizzes():
    return jsonify(quizzes)

@app.route('/api/quiz', methods=['POST'])
@jwt_required()
def add_quiz():
    user = get_jwt_identity()
    if user["role"] not in ["teacher", "common"]:
        return jsonify({"msg": "Only teachers or common users can add quizzes."}), 403
    data = request.json
    new_id = len(quizzes) + 1
    item = {"id": new_id, "question": data.get('question'), "answer": data.get('answer')}
    quizzes.append(item)
    return jsonify(item), 201

@app.route('/api/gamification', methods=['GET'])
def get_gamification():
    return jsonify(gamification)

@app.route('/api/gamification', methods=['POST'])
def update_gamification():
    data = request.json
    if 'points' in data:
        gamification['points'] += int(data['points'])
    if 'badge' in data:
        gamification['badges'].append(data['badge'])
    return jsonify(gamification)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    confirm_password = data.get("confirmPassword")
    role = data.get("role")
    if not username or not password or not role or confirm_password is None:
        return jsonify({"msg": "Missing fields"}), 400
    if password != confirm_password:
        return jsonify({"msg": "Passwords do not match"}), 400
    if any(u["username"] == username for u in users):
        return jsonify({"msg": "Username already exists"}), 409
    users.append({"username": username, "password": password, "role": role})
    return jsonify({"msg": "User registered successfully"}), 201

@app.route('/admin')
def admin_page():
    stats = {
        "users": len(users),
        "content": len(educational_content),
        "quizzes": len(quizzes)
    }
    return render_template_string("""
    <html>
    <head><title>AI Tutor Admin</title></head>
    <body>
    <h1>Admin Panel</h1>
    <p>Users: {{ stats['users'] }}</p>
    <p>Content: {{ stats['content'] }}</p>
    <p>Quizzes: {{ stats['quizzes'] }}</p>
    </body></html>""", stats=stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
