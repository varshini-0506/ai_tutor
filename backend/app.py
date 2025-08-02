from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
import requests
import json
import os

# Set matplotlib backend before importing matplotlib.pyplot to avoid Tkinter issues
import matplotlib
matplotlib.use('Agg')

from auth_routes import auth, set_users
from transformers import pipeline
from auth_routes import auth
from collaboration import collaboration
from transformers.pipelines import pipeline
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from collections import Counter
from youtube_transcript_api import YouTubeTranscriptApi
import re
from PIL import Image
import base64
import io
import pytesseract
from report_db import ReportDatabase
from pdf_generator import PDFReportGenerator
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Define this at the top level so all routes can access it
COURSE_DATA_PATH = os.path.join(os.path.dirname(__file__), 'course_data.json')
from datetime import datetime, timedelta

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Authorization", "Content-Type"])
app.config["JWT_SECRET_KEY"] = "your-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)  # Set 24 hour expiration
app.config["JWT_ERROR_MESSAGE_KEY"] = "msg"
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
jwt = JWTManager(app)

# JWT Error Handlers for debugging
@jwt.unauthorized_loader
def unauthorized_callback(callback):
    print("JWT unauthorized:", callback)
    return jsonify({"msg": "Missing or invalid JWT"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    print("JWT invalid:", callback)
    return jsonify({"msg": "Invalid JWT"}), 422

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print("JWT expired")
    return jsonify({"msg": "Expired JWT"}), 401
# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"Debug - JWT token expired: {jwt_payload}")
    return jsonify({"msg": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print(f"Debug - Invalid JWT token: {error}")
    print(f"Debug - Request headers: {dict(request.headers)}")
    print(f"Debug - Authorization header: {request.headers.get('Authorization')}")
    print(f"Debug - Error type: {type(error)}")
    print(f"Debug - Error details: {str(error)}")
    return jsonify({"msg": "Invalid token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    print(f"Debug - Missing JWT token: {error}")
    print(f"Debug - Request headers: {dict(request.headers)}")
    print(f"Debug - Authorization header: {request.headers.get('Authorization')}")
    return jsonify({"msg": "Missing token"}), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    print(f"Debug - Token not fresh: {jwt_payload}")
    return jsonify({"msg": "Token not fresh"}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    print(f"Debug - Token revoked: {jwt_payload}")
    return jsonify({"msg": "Token has been revoked"}), 401

# 🔐 Users
API_KEY = "AIzaSyBy8rbj_Y5shHSBTyCFvJj_xuzGJbx8wdE"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

educational_content = []
quizzes = []
gamification = {"badges": [], "points": 0}
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

# 📊 Initialize Report Database and PDF Generator
report_db = ReportDatabase()
pdf_generator = PDFReportGenerator()

# Create reports directory if it doesn't exist
if not os.path.exists('reports'):
    os.makedirs('reports')

# 🔐 Auth Blueprint
app.register_blueprint(auth, url_prefix='/api/auth')
set_users(users)  # Set the users list in auth_routes
app.register_blueprint(collaboration, url_prefix='/api/collaboration')

@app.route('/api/test-jwt', methods=['GET'])
@jwt_required()
def test_jwt():
    """Test route to verify JWT is working"""
    user = get_jwt_identity()
    print(f"Debug - JWT test successful, user: {user}")
    return jsonify({"msg": "JWT is working", "user": user})

@app.route('/api/test-jwt-main', methods=['GET'])
@jwt_required()
def test_jwt_main():
    """Test route to verify JWT is working in main app"""
    try:
        user = get_jwt_identity()
        print(f"Debug - Main app JWT test successful, user: {user}")
        print(f"Debug - Request headers: {dict(request.headers)}")
        print(f"Debug - Authorization header: {request.headers.get('Authorization')}")
        return jsonify({"msg": "JWT is working in main app", "user": user})
    except Exception as e:
        print(f"Debug - Main app JWT test failed: {str(e)}")
        return jsonify({"error": f"JWT test failed: {str(e)}"}), 401

@app.route('/api/test-jwt-create', methods=['GET'])
def test_jwt_create():
    """Test route to create a new JWT token"""
    try:
        test_user = {"username": "testuser", "role": "test"}
        token = create_access_token(identity=test_user)
        print(f"Debug - Created test token: {token}")
        return jsonify({"msg": "Test token created", "token": token})
    except Exception as e:
        print(f"Debug - Token creation failed: {str(e)}")
        return jsonify({"error": f"Token creation failed: {str(e)}"}), 500

@app.route('/api/test-jwt-validate', methods=['POST'])
def test_jwt_validate():
    """Test route to validate a JWT token"""
    try:
        data = request.get_json()
        token = data.get('token')
        print(f"Debug - Testing token validation for: {token}")
        
        # Try to decode the token manually to see what's happening
        import jwt as pyjwt
        try:
            decoded = pyjwt.decode(token, "your-secret-key", algorithms=["HS256"])
            print(f"Debug - Token decoded successfully: {decoded}")
            return jsonify({"msg": "Token decoded successfully", "payload": decoded})
        except Exception as e:
            print(f"Debug - Token decode failed: {str(e)}")
            return jsonify({"error": f"Token decode failed: {str(e)}"}), 400
            
    except Exception as e:
        print(f"Debug - Token validation test failed: {str(e)}")
        return jsonify({"error": f"Token validation test failed: {str(e)}"}), 500

@app.route('/api/test-server', methods=['GET'])
def test_server():
    """Simple test route to verify server is working"""
    print("Debug - Test server route called")
    return jsonify({"msg": "Server is working"})

@app.route('/api/test-headers', methods=['GET'])
def test_headers():
    """Test route to check request headers"""
    print("Debug - Test headers route called")
    print(f"Debug - All headers: {dict(request.headers)}")
    print(f"Debug - Authorization header: {request.headers.get('Authorization')}")
    return jsonify({
        "msg": "Headers received",
        "headers": dict(request.headers),
        "authorization": request.headers.get('Authorization')
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    action = data.get("action", "default")

    def extract_video_id(url):
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        return match.group(1) if match else None

    if action == "code":
        prompt = f"Explain this with code: {user_input}"

    elif action == "diagram":
        prompt = f"Describe this topic with a visual diagram: {user_input}"

    elif action == "quiz":
        prompt = f"Generate 5 multiple choice quiz questions with options and correct answers based on: {user_input}"

    elif action == "summarize":
        video_id = extract_video_id(user_input)
        if not video_id:
            return jsonify({"reply": "Invalid YouTube URL."})
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_transcript = " ".join([entry["text"] for entry in transcript_list][:50])
            prompt = f"Summarize the key learning points of this video:\n\n{full_transcript}"
        except Exception as e:
            return jsonify({"reply": f"Error fetching transcript: {str(e)}"})

    elif action == "image":
        try:
            image_data = base64.b64decode(user_input.split(",")[-1])
            image = Image.open(io.BytesIO(image_data))
            extracted_text = pytesseract.image_to_string(image)
            if not extracted_text.strip():
                return jsonify({"reply": "Could not extract any readable text from the image."})
            prompt = f"This question was extracted from an image. Help solve or explain it:\n\n{extracted_text}"
        except Exception as e:
            return jsonify({"reply": f"Error processing image: {str(e)}"})

    else:
        prompt = user_input

    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
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

@app.route("/upload-image", methods=["POST"])
def upload_image():
    try:
        data = request.get_json()
        image_data = data.get("image", "")

        if not image_data:
            return jsonify({"reply": "No image received"})

        image_bytes = base64.b64decode(image_data.split(",")[1])
        image = Image.open(io.BytesIO(image_bytes))

        extracted_text = pytesseract.image_to_string(image)
        prompt = f"Explain this question step-by-step:\n{extracted_text}"

        headers = {"Content-Type": "application/json"}
        body = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        response = requests.post(GEMINI_URL, headers=headers, data=json.dumps(body))
        result = response.json()
        if "candidates" in result:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            reply = f"Error: {result.get('error', {}).get('message', 'Unknown error')}"

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

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
    
    # Use username as identity (string) and role as additional claims
    access_token = create_access_token(
        identity=user["username"],
        additional_claims={"role": user["role"]}
    )
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

@app.route('/api/content', methods=['GET'])
def get_content():
    # Always use the correct path relative to this file
    data_path = os.path.join(os.path.dirname(__file__), 'course_data.json')
    if os.path.exists(data_path):
        with open(data_path) as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Get all available subjects from course data"""
    data_path = os.path.join(os.path.dirname(__file__), 'course_data.json')
    if os.path.exists(data_path):
        with open(data_path) as f:
            content = json.load(f)
            subjects = [item['subject'] for item in content]
            return jsonify(subjects)
    return jsonify([])

@app.route('/api/topics/<subject>', methods=['GET'])
def get_topics_by_subject(subject):
    """Get all topics for a specific subject"""
    data_path = os.path.join(os.path.dirname(__file__), 'course_data.json')
    if os.path.exists(data_path):
        with open(data_path) as f:
            content = json.load(f)
            for item in content:
                if item['subject'] == subject:
                    return jsonify(item['topics'])
    return jsonify([])

@app.route('/api/generate-quiz/<subject>', methods=['GET'])
def generate_quiz(subject):
    """Generate quiz questions for a specific subject using Gemini API"""
    try:
        # Get topics for the subject
        data_path = os.path.join(os.path.dirname(__file__), 'course_data.json')
        topics = []
        if os.path.exists(data_path):
            with open(data_path) as f:
                content = json.load(f)
                for item in content:
                    if item['subject'] == subject:
                        topics = [topic['title'] for topic in item['topics']]
                        break
        
        if not topics:
            return jsonify({"error": "No topics found for this subject"}), 404
        
        # Create prompt for Gemini
        topics_text = ", ".join(topics)
        prompt = f"""Generate 5 multiple choice quiz questions for the subject "{subject}" covering these topics: {topics_text}.

Please format the response as a JSON array with this structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Brief explanation of the correct answer"
  }}
]

Make sure:
- Questions are relevant to the subject and topics
- All options are plausible but only one is correct
- correct_answer is the index (0-3) of the correct option
- Questions test understanding, not just memorization
- Difficulty level is appropriate for students learning this subject"""

        headers = {
            "Content-Type": "application/json"
        }

        body = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        # Add retry logic and better error handling
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    GEMINI_URL, 
                    headers=headers, 
                    data=json.dumps(body),
                    timeout=30,  # Add timeout
                    verify=True   # Ensure SSL verification
                )
                response.raise_for_status()  # Raise exception for bad status codes
                break
            except requests.exceptions.SSLError as e:
                print(f"SSL Error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    return jsonify({"error": f"SSL connection error: {str(e)}"}), 500
                continue
            except requests.exceptions.RequestException as e:
                print(f"Request error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    return jsonify({"error": f"Network error: {str(e)}"}), 500
                continue
        
        result = response.json()

        if "candidates" in result:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # Try to extract JSON from the response
            try:
                # Find JSON array in the response
                import re
                json_match = re.search(r'\[.*\]', reply, re.DOTALL)
                if json_match:
                    quiz_data = json.loads(json_match.group())
                    return jsonify({
                        "success": True,
                        "questions": quiz_data,
                        "subject": subject
                    })
                else:
                    return jsonify({
                        "error": "Could not parse quiz data from AI response",
                        "raw_response": reply
                    }), 500
            except json.JSONDecodeError as e:
                return jsonify({
                    "error": f"Failed to parse quiz data: {str(e)}",
                    "raw_response": reply
                }), 500
        else:
            return jsonify({
                "error": f"AI API error: {result.get('error', {}).get('message', 'Unknown error')}"
            }), 500

    except Exception as e:
        print(f"Error generating quiz: {str(e)}")
        # Fallback: Generate sample questions locally
        try:
            sample_questions = generate_sample_questions(subject, topics)
            return jsonify({
                "success": True,
                "questions": sample_questions,
                "subject": subject,
                "note": "Using sample questions due to API connectivity issues"
            })
        except Exception as fallback_error:
            return jsonify({"error": f"Failed to generate quiz: {str(e)}"}), 500

def generate_sample_questions(subject, topics):
    """Generate sample quiz questions locally as fallback"""
    sample_questions = []
    
    # Create sample questions based on subject
    if subject == "Data Structures":
        sample_questions = [
            {
                "question": "Which data structure follows the LIFO principle?",
                "options": ["Queue", "Stack", "Linked List", "Tree"],
                "correct_answer": 1,
                "explanation": "Stack follows Last In First Out (LIFO) principle where the last element added is the first one to be removed."
            },
            {
                "question": "What is the time complexity of searching in a binary search tree?",
                "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                "correct_answer": 1,
                "explanation": "Binary search tree has O(log n) time complexity for search operations in the average case."
            },
            {
                "question": "Which of the following is a linear data structure?",
                "options": ["Tree", "Graph", "Array", "Heap"],
                "correct_answer": 2,
                "explanation": "Array is a linear data structure where elements are stored in contiguous memory locations."
            },
            {
                "question": "What operation is used to add an element to a stack?",
                "options": ["Enqueue", "Dequeue", "Push", "Pop"],
                "correct_answer": 2,
                "explanation": "Push operation is used to add an element to the top of a stack."
            },
            {
                "question": "Which data structure is best for implementing a priority queue?",
                "options": ["Array", "Linked List", "Heap", "Stack"],
                "correct_answer": 2,
                "explanation": "Heap is the most efficient data structure for implementing a priority queue."
            }
        ]
    elif subject == "Machine Learning":
        sample_questions = [
            {
                "question": "What type of learning uses labeled training data?",
                "options": ["Unsupervised Learning", "Supervised Learning", "Reinforcement Learning", "Deep Learning"],
                "correct_answer": 1,
                "explanation": "Supervised learning uses labeled training data to learn the mapping from inputs to outputs."
            },
            {
                "question": "Which algorithm is commonly used for classification problems?",
                "options": ["Linear Regression", "Logistic Regression", "K-means", "Random Forest"],
                "correct_answer": 1,
                "explanation": "Logistic Regression is commonly used for binary classification problems."
            },
            {
                "question": "What is overfitting in machine learning?",
                "options": ["Model performs well on training data but poorly on new data", "Model performs poorly on all data", "Model is too simple", "Model has too few parameters"],
                "correct_answer": 0,
                "explanation": "Overfitting occurs when a model learns the training data too well but fails to generalize to new, unseen data."
            },
            {
                "question": "Which evaluation metric is used for classification problems?",
                "options": ["Mean Squared Error", "Accuracy", "R-squared", "Mean Absolute Error"],
                "correct_answer": 1,
                "explanation": "Accuracy is a common evaluation metric for classification problems, measuring the proportion of correct predictions."
            },
            {
                "question": "What is the purpose of cross-validation?",
                "options": ["To increase model complexity", "To reduce training time", "To assess model performance", "To increase data size"],
                "correct_answer": 2,
                "explanation": "Cross-validation is used to assess how well a model will generalize to new, unseen data."
            }
        ]
    else:
        # Generic questions for other subjects
        sample_questions = [
            {
                "question": f"What is the main focus of {subject}?",
                "options": ["Theory only", "Practical applications", "Both theory and practice", "None of the above"],
                "correct_answer": 2,
                "explanation": f"{subject} typically involves both theoretical concepts and practical applications."
            },
            {
                "question": f"Which of the following is important in {subject}?",
                "options": ["Memorization", "Understanding concepts", "Guessing", "Avoiding practice"],
                "correct_answer": 1,
                "explanation": f"Understanding concepts is crucial for mastering {subject}."
            },
            {
                "question": f"What is a key skill needed for {subject}?",
                "options": ["Problem solving", "Avoiding challenges", "Memorizing everything", "Working alone"],
                "correct_answer": 0,
                "explanation": f"Problem solving is a fundamental skill required in {subject}."
            },
            {
                "question": f"How should you approach learning {subject}?",
                "options": ["Cramming before exams", "Regular practice and study", "Avoiding difficult topics", "Relying only on lectures"],
                "correct_answer": 1,
                "explanation": f"Regular practice and study is the most effective approach for learning {subject}."
            },
            {
                "question": f"What is the best way to master {subject}?",
                "options": ["Reading only", "Practice and application", "Avoiding questions", "Memorizing formulas"],
                "correct_answer": 1,
                "explanation": f"Practice and application of concepts is the best way to master {subject}."
            }
        ]
    
    return sample_questions

@app.route('/api/content', methods=['POST'])
@jwt_required()
def add_content():
    username = get_jwt_identity()
    role = get_jwt()["role"]  # Get role from additional claims
    if role not in ["teacher", "common"]:
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
    username = get_jwt_identity()
    role = get_jwt()["role"]  # Get role from additional claims
    if role not in ["teacher", "common"]:
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

# 📊 PDF Report Generation and Management Endpoints

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate a PDF report for the current user"""
    try:
        print("=== Generate Report Debug ===")
        print("Headers:", dict(request.headers))
        print("Method:", request.method)
        
        data = request.get_json()
        print("Request JSON data:", data)
        
        # Get username from request data or use default
        student_name = data.get('student_name', 'Student') if data else 'Student'
        print("Student name:", student_name)
        
        # Get chart images from request
        charts = data.get('charts', {})
        
        # Get analytics data
        analytics_data = get_analytics_data()
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{student_name.replace(' ', '_')}_{timestamp}.pdf"
        pdf_path = os.path.join('reports', filename)
        
        # Get remarks if they exist
        remarks = None
        if data and data.get('student_name'):
            # Try to get existing remarks for this student
            student_reports = report_db.get_reports_by_student(data.get('student_name'))
            if student_reports and len(student_reports) > 0:
                remarks = student_reports[0][8] if len(student_reports[0]) > 8 else None
        
        # Generate PDF
        pdf_generator.generate_report_pdf(student_name, analytics_data, pdf_path, charts=charts, remarks=remarks)
        
        # Store in database
        report_id = report_db.save_report(
            student_name=student_name,
            report_data=json.dumps(analytics_data),
            pdf_path=pdf_path,
            subject_scores=json.dumps(analytics_data.get('subject_scores', {})),
            topic_completion=json.dumps(analytics_data.get('topic_completion', {})),
            activity_data=json.dumps(analytics_data.get('activity_data', {}))
        )
        
        print("Report generated successfully with ID:", report_id)
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'pdf_path': pdf_path,
            'message': f'Report generated successfully for {student_name}'
        })
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-report/<int:report_id>', methods=['GET'])
def download_report(report_id):
    """Download a specific PDF report"""
    try:
        report = report_db.get_report_by_id(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        pdf_path = report[3]  # pdf_path is at index 3
        
        if not os.path.exists(pdf_path):
            return jsonify({'error': 'PDF file not found'}), 404
        
        return send_file(pdf_path, as_attachment=True, download_name=f"report_{report[1]}_{report_id}.pdf")
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """Get reports based on user role (teacher or student)."""
    try:
        username = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')

        print(f"Fetching reports for user: {username}, role: {user_role}")

        if user_role == 'teacher':
            reports = report_db.get_all_reports()
            formatted_reports = []
            for report in reports:
                formatted_reports.append({
                    'id': report[0],
                    'student_name': report[1],
                    'created_at': report[4],
                    'pdf_path': report[3],
                    'remarks': report[8] if len(report) > 8 else None
                })
        else:
            # For students, always return a default report
            # First check if there's already a default report for this student
            student_reports = report_db.get_reports_by_student(username)
            
            if student_reports:
                # Use existing report
                report = student_reports[0]
                formatted_reports = [{
                    'id': report[0],
                    'student_name': report[1],
                    'created_at': report[4],
                    'pdf_path': report[3],
                    'remarks': report[8] if len(report) > 8 else None
                }]
            else:
                # Create a default report for this student
                if not os.path.exists('reports'):
                    os.makedirs('reports')
                
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"report_{username}_{timestamp}.pdf"
                pdf_path = os.path.join('reports', filename)
                
                # Generate charts and rich data for the PDF
                charts = create_dummy_charts()
                report_data = {
                    "subject_scores": {"Math": 85, "Science": 78, "History": 92, "English": 88},
                    "topic_completion": {"Algebra": 8, "Biology": 6, "World War II": 9, "Shakespeare": 7},
                    "activity_data": {"Mon": 3, "Tue": 5, "Wed": 4, "Thu": 6, "Fri": 7, "Sat": 2, "Sun": 1},
                    "total_views": 28
                }
                
                pdf_generator.generate_report_pdf(username, report_data, pdf_path, charts=charts, remarks=None)
                
                report_id = report_db.save_report(
                    student_name=username,
                    report_data=json.dumps(report_data),
                    pdf_path=pdf_path,
                    subject_scores=json.dumps(report_data["subject_scores"]),
                    topic_completion=json.dumps(report_data["topic_completion"]),
                    activity_data=json.dumps(report_data["activity_data"])
                )
                
                formatted_reports = [{
                    'id': report_id,
                    'student_name': username,
                    'created_at': datetime.now().isoformat(),
                    'pdf_path': pdf_path,
                    'remarks': None
                }]
        
        return jsonify(formatted_reports)
        
    except Exception as e:
        print(f"Error getting reports: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<int:report_id>/remark', methods=['POST'])
@jwt_required()
def add_remark(report_id):
    """Add a remark to a specific report (teacher only)"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        if user_role != 'teacher':
            return jsonify({'error': 'Only teachers can add remarks'}), 403

        data = request.get_json()
        remark = data.get('remark')

        if remark is None:
            return jsonify({'error': 'Remark is required'}), 400

        report_db.add_remark(report_id, remark)
        
        # Regenerate PDF with the new remark
        try:
            report = report_db.get_report_by_id(report_id)
            if report:
                # Parse the report data
                report_data = json.loads(report[2]) if isinstance(report[2], str) else report[2]
                
                # Regenerate PDF with remarks
                pdf_generator.generate_report_pdf(
                    report[1],  # student_name
                    report_data,
                    report[3],  # pdf_path
                    charts=None,
                    remarks=remark
                )
        except Exception as e:
            print(f"Warning: Could not regenerate PDF with remarks: {e}")
        
        return jsonify({'message': 'Remark added successfully'})

    except Exception as e:
        print(f"Error adding remark: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Delete a specific report"""
    try:
        report = report_db.get_report_by_id(report_id)
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Delete PDF file
        pdf_path = report[3]
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        
        # Delete from database
        report_db.delete_report(report_id)
        
        return jsonify({'message': 'Report deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_analytics_data():
    """Get analytics data for report generation"""
    if not os.path.exists('progress.json'):
        return {
            "views_by_subject": {},
            "views_by_topic": {},
            "total_views": 0,
            "subject_scores": {},
            "topic_completion": {},
            "activity_data": {}
        }
    
    with open('progress.json') as f:
        logs = json.load(f)
    
    subj_counts = Counter(e['subject'] for e in logs)
    topic_counts = Counter(e['title'] for e in logs)
    
    # Generate mock subject scores based on activity
    subject_scores = {}
    for subject, count in subj_counts.items():
        # Generate a score between 60-95 based on activity
        score = min(95, max(60, 60 + (count * 5)))
        subject_scores[subject] = score
    
    # Generate topic completion data
    topic_completion = {}
    for subject, count in subj_counts.items():
        # Mock completion: 70-90% of total topics
        total_topics = count * 2  # Assume 2x the viewed topics as total
        completed = min(total_topics, int(count * 1.5))
        topic_completion[subject] = completed
    
    # Generate weekly activity data
    activity_data = {}
    for i, day in enumerate(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']):
        activity_data[day] = len([log for log in logs if i < len(logs) // 7])
    
    return {
        'total_views': len(logs),
        'views_by_subject': dict(subj_counts),
        'views_by_topic': dict(topic_counts),
        'subject_scores': subject_scores,
        'topic_completion': topic_completion,
        'activity_data': activity_data
    }

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

# Helper function to create and encode charts
def create_dummy_charts():
    charts = {}
    
    # Bar Chart
    subjects = ['Math', 'Science', 'History', 'English']
    scores = np.random.randint(60, 100, size=len(subjects))
    plt.figure(figsize=(6, 3))
    plt.bar(subjects, scores, color=['#4e79a7', '#f28e2b', '#e15759', '#76b7b2'])
    plt.title('Subject Mastery')
    plt.ylabel('Scores (%)')
    plt.ylim(0, 100)
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    charts['bar'] = "data:image/png;base64," + base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()

    # Pie Chart
    completed = np.random.randint(5, 15)
    remaining = np.random.randint(1, 5)
    plt.figure(figsize=(4, 4))
    plt.pie([completed, remaining], labels=['Completed', 'Remaining'], autopct='%1.1f%%', colors=['#59a14f', '#edc948'])
    plt.title('Overall Topic Completion')

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    charts['doughnut'] = "data:image/png;base64," + base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    # Line Chart
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    activity = np.random.randint(0, 8, size=len(days))
    plt.figure(figsize=(6, 3))
    plt.plot(days, activity, marker='o', linestyle='-', color='#bab0ab')
    plt.title('Weekly Learning Activity')
    plt.ylabel('Activities')
    plt.ylim(0, 10)

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    charts['line'] = "data:image/png;base64," + base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()
    
    return charts

@app.route('/api/seed-reports', methods=['GET'])
def seed_reports():
    """A temporary endpoint to seed the database with rich dummy reports, including charts."""
    try:
        if not os.path.exists('reports'):
            os.makedirs('reports')

        dummy_students = ["Alice", "Bob", "Charlie"]
        count = 0

        for student_name in dummy_students:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"report_{student_name}_{timestamp}.pdf"
            pdf_path = os.path.join('reports', filename)

            # Generate charts and rich data for the PDF
            charts = create_dummy_charts()
            report_data = {
                "subject_scores": {"Math": 92, "Science": 85, "History": 78, "English": 88},
                "topic_completion": {"Algebra": 10, "Biology": 8, "World War II": 7, "Shakespeare": 9},
                "activity_data": {"Mon": 2, "Tue": 4, "Wed": 3, "Thu": 5, "Fri": 6, "Sat": 2, "Sun": 1},
                "total_views": 23
            }
            
            pdf_generator.generate_report_pdf(student_name, report_data, pdf_path, charts=charts, remarks=None)
            
            report_db.save_report(
                student_name=student_name,
                report_data=json.dumps(report_data),
                pdf_path=pdf_path,
                subject_scores=json.dumps(report_data["subject_scores"]),
                topic_completion=json.dumps(report_data["topic_completion"]),
                activity_data=json.dumps(report_data["activity_data"])
            )
            count += 1
        
        return jsonify({'message': f'Successfully seeded {count} rich dummy reports with charts.'}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/view-report/<int:report_id>', methods=['GET'])
@jwt_required()
def view_report(report_id):
    """Sends a specific PDF report for inline viewing."""
    try:
        report = report_db.get_report_by_id(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        pdf_path = report[3]
        
        if not os.path.exists(pdf_path):
            return jsonify({'error': 'PDF file not found on server.'}), 404
        
        # Use as_attachment=False to allow inline viewing
        return send_file(pdf_path, as_attachment=False)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/course-data', methods=['GET'])
def get_course_data():
    try:
        with open(COURSE_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        print("Error in /api/course-data:", e)  # Debug print
        return jsonify({'error': str(e)}), 500

@app.route('/api/course-data/add-topic', methods=['POST'])
def add_topic():
    try:
        req = request.json
        subject = req.get('subject')
        title = req.get('title')
        videoUrl = req.get('videoUrl')
        if not (subject and title and videoUrl):
            return jsonify({'error': 'Missing subject, title, or videoUrl'}), 400
        with open(COURSE_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for subj in data:
            if subj['subject'] == subject:
                subj['topics'].append({'title': title, 'videoUrl': videoUrl})
                break
        else:
            return jsonify({'error': 'Subject not found'}), 404
        with open(COURSE_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/course-data/delete-topic', methods=['POST'])
def delete_topic():
    try:
        req = request.json
        subject = req.get('subject')
        title = req.get('title')
        if not (subject and title):
            return jsonify({'error': 'Missing subject or title'}), 400
        with open(COURSE_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for subj in data:
            if subj['subject'] == subject:
                subj['topics'] = [t for t in subj['topics'] if t['title'] != title]
                break
        else:
            return jsonify({'error': 'Subject not found'}), 404
        with open(COURSE_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    code = getattr(e, 'code', 500)
    return jsonify({"reply": f"Server error: {str(e)}"}), code

if __name__ == '__main__':
    app.run(debug=True, port=5000)
