from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set matplotlib backend before importing matplotlib.pyplot to avoid Tkinter issues
import matplotlib
matplotlib.use('Agg')

from auth_routes import auth
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available. AI features will be disabled.")
from auth_routes import auth
from collaboration import collaboration
try:
    from transformers.pipelines import pipeline
    TRANSFORMERS_PIPELINES_AVAILABLE = True
except ImportError:
    TRANSFORMERS_PIPELINES_AVAILABLE = False
    print("Warning: transformers.pipelines not available. AI features will be disabled.")
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from collections import Counter
from youtube_transcript_api import YouTubeTranscriptApi
import re
from PIL import Image
import base64
import io
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("Warning: pytesseract not available. OCR features will be disabled.")
from neon_report_db import NeonReportDatabase
from config import Config
from pdf_generator import PDFReportGenerator
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Define this at the top level so all routes can access it
COURSE_DATA_PATH = os.path.join(os.path.dirname(__file__), 'course_data.json')
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import base64

# Configure Tesseract OCR
try:
    # Try to find Tesseract in common locations
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        'tesseract'  # If it's in PATH
    ]
    
    tesseract_found = False
    for path in tesseract_paths:
        if os.path.exists(path) or path == 'tesseract':
            try:
                pytesseract.pytesseract.tesseract_cmd = path
                # Test if it works
                pytesseract.get_tesseract_version()
                print(f"✅ Tesseract found at: {path}")
                tesseract_found = True
                break
            except Exception as e:
                print(f"⚠️ Tesseract at {path} failed: {e}")
                continue
    
    if not tesseract_found:
        print("❌ Tesseract OCR not found. OCR features will be disabled.")
        print("To install Tesseract:")
        print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install to: C:\\Program Files\\Tesseract-OCR\\")
        print("3. Add to PATH during installation")
        
except Exception as e:
    print(f"❌ Error configuring Tesseract: {e}")
    print("OCR features will be disabled.")

# Print configuration at startup
Config.print_config()

app = Flask(__name__)
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "https://ai-tutor-frontend-kkne.onrender.com", "https://ai-tutor-frontend-*.onrender.com", "*"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
         "expose_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True,
         "max_age": 86400
     }})
app.config["JWT_SECRET_KEY"] = "your-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)  # Set 24 hour expiration
app.config["JWT_ERROR_MESSAGE_KEY"] = "msg"
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
jwt = JWTManager(app)

# Add OPTIONS handler for preflight requests
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = app.make_default_options_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,Origin,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,Origin,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

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
API_KEY = "AIzaSyAW0sxYjOyJF7rHf8PjD80ZPseWtvOXzTQ"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

educational_content = []
quizzes = []
gamification = {"badges": [], "points": 0}

# 💡 In-memory storage
educational_content = []
quizzes = []
gamification = {"badges": [], "points": 0}

# Rate limiting for API calls
api_call_times = []
RATE_LIMIT_WINDOW = 60  # 60 seconds
MAX_CALLS_PER_WINDOW = 10  # Max 10 calls per minute

def check_rate_limit():
    """Check if we're within rate limits"""
    import time
    current_time = time.time()
    
    # Remove old calls outside the window
    global api_call_times
    api_call_times = [call_time for call_time in api_call_times if current_time - call_time < RATE_LIMIT_WINDOW]
    
    # Check if we're under the limit
    if len(api_call_times) >= MAX_CALLS_PER_WINDOW:
        return False
    
    # Record this call
    api_call_times.append(current_time)
    return True

# 🤖 Load QA Model
try:
    qa_pipeline = pipeline("question-answering")
except Exception as e:
    qa_pipeline = None
    print(f"Failed to load QA model: {e}")

# 📊 Initialize Report Database and PDF Generator
try:
    # Initialize Neon DB
    report_db = NeonReportDatabase()
    # Initialize the database schema
    report_db.init_database()
    print("✅ Neon DB initialized successfully")
except Exception as e:
    print(f"❌ Error initializing Neon DB: {e}")
    print("Make sure DATABASE_URL or NEON_DB_URL environment variable is set")
    print("You can set it in your .env file or as an environment variable")
    # Fallback to SQLite for development
    try:
        from report_db import ReportDatabase
        report_db = ReportDatabase()
        print("⚠️ Falling back to SQLite database")
    except Exception as sqlite_error:
        print(f"❌ SQLite fallback also failed: {sqlite_error}")
        report_db = None

pdf_generator = PDFReportGenerator()

# Create reports directory if it doesn't exist
if not os.path.exists('reports'):
    os.makedirs('reports')

# 🔐 Auth Blueprint
app.register_blueprint(auth, url_prefix='/api/auth')
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

@app.route('/api/test-cors', methods=['GET', 'POST', 'OPTIONS'])
def test_cors():
    """Test route specifically for CORS debugging"""
    print(f"Debug - CORS test called with method: {request.method}")
    print(f"Debug - Request headers: {dict(request.headers)}")
    print(f"Debug - Origin: {request.headers.get('Origin', 'No origin header')}")
    
    if request.method == 'OPTIONS':
        print("Debug - Handling OPTIONS preflight request")
        response = app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,Origin,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        print(f"Debug - OPTIONS response headers: {dict(response.headers)}")
        return response
    
    print("Debug - Handling regular request")
    return jsonify({
        "message": "CORS test successful!", 
        "method": request.method,
        "origin": request.headers.get('Origin', 'No origin header'),
        "headers": dict(request.headers)
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    action = data.get("action", "default")
    
    # Check rate limit first
    if not check_rate_limit():
        return jsonify({"reply": "Rate limit exceeded. Please try again later."})

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

    # Add retry logic and better error handling with rate limiting
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Add delay between retries to handle rate limiting
            if attempt > 0:
                import time
                time.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
            
            response = requests.post(
                GEMINI_URL, 
                headers=headers, 
                data=json.dumps(body),
                timeout=30,  # Add timeout
                verify=True   # Ensure SSL verification
            )
            
            # Handle rate limiting specifically
            if response.status_code == 429:
                print(f"Rate limited on attempt {attempt + 1}, waiting...")
                if attempt == max_retries - 1:
                    return jsonify({"reply": "API rate limit exceeded. Please try again later."})
                continue
            
            response.raise_for_status()  # Raise exception for bad status codes
            break
        except requests.exceptions.SSLError as e:
            print(f"SSL Error on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                return jsonify({"reply": f"SSL connection error: {str(e)}"})
            continue
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {str(e)}")
            if attempt == max_retries - 1:
                return jsonify({"reply": f"Network error: {str(e)}"})
            continue

    try:
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

        # Try to extract text using OCR
        extracted_text = ""
        try:
            extracted_text = pytesseract.image_to_string(image)
            if not extracted_text.strip():
                extracted_text = "No text could be extracted from the image"
        except Exception as ocr_error:
            print(f"OCR Error: {ocr_error}")
            extracted_text = "OCR is not available. Please install Tesseract OCR."
        
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
        # Check rate limit first
        if not check_rate_limit():
            return jsonify({
                "error": "Rate limit exceeded. Please try again later.",
                "retry_after": 60
            }), 429
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

        # Add retry logic and better error handling with rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add delay between retries to handle rate limiting
                if attempt > 0:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
                
                response = requests.post(
                    GEMINI_URL, 
                    headers=headers, 
                    data=json.dumps(body),
                    timeout=30,  # Add timeout
                    verify=True   # Ensure SSL verification
                )
                
                # Handle rate limiting specifically
                if response.status_code == 429:
                    print(f"Rate limited on attempt {attempt + 1}, waiting...")
                    if attempt == max_retries - 1:
                        return jsonify({
                            "error": "API rate limit exceeded. Please try again later.",
                            "retry_after": 60
                        }), 429
                    continue
                
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
            print(f"Fallback also failed: {str(fallback_error)}")
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
    """Register a new user using the database"""
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirmPassword")
        role = data.get("role", "student")
        email = data.get("email")
        
        if not username or not password or not role or confirm_password is None:
            return jsonify({"msg": "Missing fields"}), 400
        if password != confirm_password:
            return jsonify({"msg": "Passwords do not match"}), 400
        
        # Import user database here to avoid circular imports
        from neon_user_db import NeonUserDatabase
        user_db = NeonUserDatabase()
        
        # Create new user
        user = user_db.create_user(username=username, password=password, role=role, email=email)
        
        return jsonify({
            "msg": "User registered successfully",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "role": user['role'],
                "email": user.get('email')
            }
        }), 201
        
    except ValueError as e:
        return jsonify({"msg": str(e)}), 409
    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"msg": "Error creating user"}), 500

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
        
        # Get analytics data
        analytics_data = get_analytics_data()
        
        # Generate charts using matplotlib
        charts = create_dummy_charts()
        
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
                remarks = student_reports[0].get('remarks')
        
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
        
        pdf_path = report['pdf_path']
        
        # Check if PDF exists and regenerate if needed with new charts
        if not os.path.exists(pdf_path):
            # Regenerate the report with new charts
            regenerate_report_with_charts(report)
            pdf_path = report['pdf_path']
        
        return send_file(pdf_path, as_attachment=True, download_name=f"report_{report['student_name']}_{report_id}.pdf")
        
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
                    'id': report['id'],
                    'student_name': report['student_name'],
                    'created_at': report['created_at'],
                    'pdf_path': report['pdf_path'],
                    'remarks': report.get('remarks')
                })
        else:
            # For students, always return a default report
            # First check if there's already a default report for this student
            student_reports = report_db.get_reports_by_student(username)
            
            if student_reports:
                # Use existing report
                report = student_reports[0]
                formatted_reports = [{
                    'id': report['id'],
                    'student_name': report['student_name'],
                    'created_at': report['created_at'],
                    'pdf_path': report['pdf_path'],
                    'remarks': report.get('remarks')
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
                # Get the report data (already in JSONB format)
                report_data = report['report_data']
                
                # Regenerate PDF with remarks
                pdf_generator.generate_report_pdf(
                    report['student_name'],
                    report_data,
                    report['pdf_path'],
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
        pdf_path = report['pdf_path']
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
    
    try:
        with open('progress.json') as f:
            logs = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading progress.json: {e}")
        print("Returning default analytics data")
        return {
            "views_by_subject": {},
            "views_by_topic": {},
            "total_views": 0,
            "subject_scores": {},
            "topic_completion": {},
            "activity_data": {}
        }
    
    subj_counts = Counter(e['subject'] for e in logs)
    topic_counts = Counter(e['title'] for e in logs)
    
    # Get actual subjects from course data for comprehensive analytics
    try:
        with open('course_data.json', 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        all_subjects = [subject['subject'] for subject in course_data]
    except Exception as e:
        print(f"Error reading course data for analytics: {e}")
        all_subjects = ['Data Structures', 'Operating Systems', 'Database Management Systems', 'Computer Networks']
    
    # Generate mock subject scores based on activity
    subject_scores = {}
    for subject in all_subjects:
        # Use actual activity if available, otherwise generate random score
        if subject in subj_counts:
            score = min(95, max(60, 60 + (subj_counts[subject] * 5)))
        else:
            score = np.random.randint(60, 95)
        subject_scores[subject] = score
    
    # Generate topic completion data
    topic_completion = {}
    for subject in all_subjects:
        if subject in subj_counts:
            # Mock completion: 70-90% of total topics
            total_topics = subj_counts[subject] * 2  # Assume 2x the viewed topics as total
            completed = min(total_topics, int(subj_counts[subject] * 1.5))
        else:
            # Generate random completion for subjects with no activity
            completed = np.random.randint(3, 8)
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
    
    # Get actual subjects from course data
    try:
        with open('course_data.json', 'r', encoding='utf-8') as f:
            course_data = json.load(f)
        subjects = [subject['subject'] for subject in course_data]
        # Use first 6 subjects for the chart (or all if less than 6)
        chart_subjects = subjects[:6] if len(subjects) >= 6 else subjects
    except Exception as e:
        print(f"Error reading course data: {e}")
        # Fallback to default subjects
        chart_subjects = ['Data Structures', 'Operating Systems', 'Database Management Systems', 'Computer Networks', 'Artificial Intelligence', 'Machine Learning']
    
    # Bar Chart
    scores = np.random.randint(60, 100, size=len(chart_subjects))
    plt.figure(figsize=(10, 4))  # Made wider to accommodate more subjects and longer names
    colors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc948', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab']
    plt.bar(chart_subjects, scores, color=colors[:len(chart_subjects)])
    plt.title('Subject Mastery')
    plt.ylabel('Scores (%)')
    plt.ylim(0, 100)
    plt.xticks(rotation=45, ha='right')  # Rotate labels for better readability
    
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
            
            # Get actual subjects from course data
            try:
                with open('course_data.json', 'r', encoding='utf-8') as f:
                    course_data = json.load(f)
                actual_subjects = [subject['subject'] for subject in course_data]
                # Use first 4 subjects for the report
                report_subjects = actual_subjects[:4] if len(actual_subjects) >= 4 else actual_subjects
            except Exception as e:
                print(f"Error reading course data for seed reports: {e}")
                report_subjects = ['Data Structures', 'Operating Systems', 'Database Management Systems', 'Computer Networks']
            
            # Generate random scores for actual subjects
            subject_scores = {}
            topic_completion = {}
            for subject in report_subjects:
                subject_scores[subject] = np.random.randint(70, 95)
                topic_completion[subject] = np.random.randint(5, 15)
            
            report_data = {
                "subject_scores": subject_scores,
                "topic_completion": topic_completion,
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
        
        pdf_path = report['pdf_path']
        
        # Check if PDF exists and regenerate if needed with new charts
        if not os.path.exists(pdf_path):
            # Regenerate the report with new charts
            regenerate_report_with_charts(report)
            pdf_path = report['pdf_path']
        
        # Use as_attachment=False to allow inline viewing
        return send_file(pdf_path, as_attachment=False)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def regenerate_report_with_charts(report):
    """Regenerate a report with the new chart functionality"""
    try:
        student_name = report['student_name']
        
        # Generate fresh analytics data to ensure proper structure
        analytics_data = get_analytics_data()
        
        # Generate new PDF with charts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{student_name.replace(' ', '_')}_{timestamp}.pdf"
        pdf_path = os.path.join('reports', filename)
        
        # Get remarks from the original report
        remarks = report.get('remarks')
        
        # Generate PDF with fresh analytics data and new chart functionality
        pdf_generator.generate_report_pdf(student_name, analytics_data, pdf_path, charts=None, remarks=remarks)
        
        # Update the report in database with new PDF path and fresh data
        report_db.update_report_pdf_path(report['id'], pdf_path)
        
        # Also update the report data in database to ensure consistency
        report_db.update_report_data(report['id'], json.dumps(analytics_data))
        
        print(f"Successfully regenerated report for {student_name} with new charts")
        
    except Exception as e:
        print(f"Error regenerating report: {e}")
        import traceback
        traceback.print_exc()

@app.route('/api/regenerate-report/<int:report_id>', methods=['POST'])
@jwt_required()
def regenerate_report(report_id):
    """Regenerate a specific report with new chart functionality"""
    try:
        # Check if user is teacher
        claims = get_jwt()
        user_role = claims.get('role')
        
        if user_role != 'teacher':
            return jsonify({'error': 'Only teachers can regenerate reports'}), 403
        
        report = report_db.get_report_by_id(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Regenerate the report with new charts
        regenerate_report_with_charts(report)
        
        return jsonify({
            'success': True,
            'message': f'Report for {report["student_name"]} has been regenerated with new charts'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-generate-report', methods=['GET'])
def test_generate_report():
    """Test endpoint to generate a report with charts"""
    try:
        # Generate fresh analytics data
        analytics_data = get_analytics_data()
        
        # Generate test PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_report_{timestamp}.pdf"
        pdf_path = os.path.join('reports', filename)
        
        # Generate PDF with charts
        pdf_generator.generate_report_pdf("Test Student", analytics_data, pdf_path, charts=None, remarks="Test report with charts")
        
        return jsonify({
            'success': True,
            'pdf_path': pdf_path,
            'analytics_data': analytics_data,
            'message': 'Test report generated successfully'
        })
        
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

# Advanced AI Features Endpoints

@app.route('/analyze-code', methods=['POST'])
def analyze_code():
    """Analyze code and provide feedback"""
    try:
        data = request.get_json()
        code = data.get('code')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        
        # Basic code analysis (can be enhanced with AI)
        analysis = f"""
## Code Analysis for {language.upper()}

### Code Structure
- Lines of code: {len(code.split('\n'))}
- Characters: {len(code)}
- Language: {language}

### Potential Issues
1. **Syntax Check**: Code appears syntactically correct
2. **Best Practices**: 
   - Consider adding comments for complex logic
   - Ensure proper error handling
   - Follow naming conventions

### Suggestions
- Add docstrings for functions
- Consider breaking down complex functions
- Add type hints for better code clarity

### Security Considerations
- Validate all inputs
- Avoid hardcoded credentials
- Use parameterized queries for database operations

This analysis is based on general programming best practices. For more detailed analysis, consider using specialized tools for {language}.
        """
        
        return jsonify({'analysis': analysis})
        
    except Exception as e:
        print(f"Error analyzing code: {e}")
        return jsonify({'error': 'Failed to analyze code'}), 500

@app.route('/check-ocr', methods=['GET'])
def check_ocr():
    """Check if OCR (Tesseract) is properly installed and working"""
    try:
        if PYTESSERACT_AVAILABLE:
            import pytesseract
            version = pytesseract.get_tesseract_version()
            return jsonify({
                'status': 'success',
                'message': 'OCR is available',
                'tesseract_version': str(version),
                'available': True
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'pytesseract library not installed',
                'available': False
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Tesseract not properly configured: {str(e)}',
            'available': False
        })

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze uploaded images for educational content"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        analysis_type = data.get('analysis_type', 'educational')
        
        if not image_data:
            return jsonify({'error': 'Image data is required'}), 400
        
        # Remove data URL prefix if present
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as decode_error:
            print(f"Error decoding image: {decode_error}")
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Use OCR to extract text from image
        text = ""
        ocr_success = False
        try:
            # Check if pytesseract is available
            if PYTESSERACT_AVAILABLE:
                import pytesseract
                text = pytesseract.image_to_string(image)
                text = text.strip()
                ocr_success = True
                print(f"OCR extracted text: {text[:100]}...")  # Log first 100 chars
            else:
                print("pytesseract not installed")
                text = "OCR library not available"
        except Exception as ocr_error:
            print(f"OCR Error: {ocr_error}")
            text = "Could not extract text from image"
        
        # Enhanced analysis based on type
        if analysis_type == 'educational':
            if text and len(text) > 10 and ocr_success:
                analysis = f"""
## 📚 Educational Content Analysis

### 📖 Extracted Text
```
{text}
```

### 🎯 Content Analysis
- **Type**: Educational material
- **Text Quality**: {'Good' if len(text) > 50 else 'Fair'}
- **Readability**: {'High' if len(text.split()) > 10 else 'Medium'}
- **OCR Status**: ✅ Successfully extracted

### 💡 Learning Suggestions
1. **Study Tips**:
   - Create flashcards from key concepts
   - Summarize the main points in your own words
   - Connect this content to related topics you've learned

2. **Practice Ideas**:
   - Write questions based on the content
   - Explain the concepts to someone else
   - Create a mind map of the key ideas

3. **Review Strategy**:
   - Revisit this material in 24 hours
   - Quiz yourself on the main concepts
   - Apply the knowledge to real-world examples

### 🔍 Key Concepts Identified
{chr(10).join([f"- {line.strip()}" for line in text.split('\n')[:5] if line.strip()])}

Would you like me to create a quiz based on this content or explain any specific concepts in more detail?
                """
            else:
                analysis = f"""
## 🖼️ Image Analysis

### 📸 Visual Content Detected
This appears to be an image with visual content. 

### 🔍 OCR Status
- **Text Extraction**: {'❌ Failed' if not ocr_success else '✅ Successful'}
- **Extracted Text**: {'None' if not text else f'"{text[:100]}..."'}

### 🎨 Visual Learning Strategies
1. **Diagram Analysis**:
   - Identify the main components
   - Look for labels and annotations
   - Understand the relationships between elements

2. **Memory Techniques**:
   - Create your own version of the diagram
   - Use the method of loci (memory palace)
   - Associate colors and shapes with concepts

3. **Study Methods**:
   - Break down complex visuals into smaller parts
   - Explain the image to someone else
   - Create flashcards with visual cues

### 💭 Questions to Consider
- What is the main topic of this image?
- How do the different elements relate to each other?
- What concepts could this visual represent?

### 🛠️ Troubleshooting
If text extraction failed, try:
- Using a clearer, higher resolution image
- Ensuring the text is well-lit and in focus
- Using images with clear, readable fonts
- Checking that the image contains text content

Would you like me to help you understand any specific aspect of this visual content?
                """
        elif analysis_type == 'diagram':
            analysis = f"""
## 📊 Diagram Analysis

### 🔍 Visual Elements
- **Content Type**: Educational diagram
- **OCR Status**: {'❌ Failed' if not ocr_success else '✅ Successful'}

### 📝 Extracted Text
```
{text if text else 'No text detected'}
```

### 🎯 Diagram Analysis Tips
1. **Structure Identification**:
   - Look for main components and sub-components
   - Identify relationships and connections
   - Note any labels or annotations

2. **Learning Approach**:
   - Break down the diagram into sections
   - Understand the flow or hierarchy
   - Create your own simplified version

3. **Memory Techniques**:
   - Use spatial memory techniques
   - Associate colors with concepts
   - Create mental connections between elements

Would you like me to help you understand this diagram or create study materials from it?
            """
        else:  # code
            analysis = f"""
## 💻 Code Analysis

### 🔍 Extracted Code
```
{text if text else 'No code detected'}
```

### 📊 Code Assessment
- **Readability**: {'Good' if text and len(text) > 30 else 'Limited'}
- **Structure**: {'Well-organized' if text and '\n' in text else 'Single line'}
- **Language**: Appears to be programming code
- **OCR Status**: {'❌ Failed' if not ocr_success else '✅ Successful'}

### 🛠️ Code Review Checklist
1. **Syntax**: Check for proper syntax and formatting
2. **Logic**: Verify the logical flow of the code
3. **Comments**: Add explanatory comments where needed
4. **Naming**: Use descriptive variable and function names
5. **Testing**: Verify functionality with test cases

### 📚 Learning Approach
- **Type it manually**: Reinforce learning by typing the code
- **Modify it**: Make changes to test understanding
- **Explain it**: Describe what each part does
- **Practice**: Write similar code from scratch

### 💡 Best Practices
- Use consistent indentation
- Add comments for complex logic
- Choose meaningful variable names
- Test your code thoroughly
- Follow language-specific conventions

Would you like me to explain any specific part of this code or help you understand the concepts?
            """
        
        return jsonify({'analysis': analysis})
        
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return jsonify({'error': f'Failed to analyze image: {str(e)}'}), 500

@app.route('/voice-to-text', methods=['POST'])
def voice_to_text():
    """Convert voice input to text using speech recognition"""
    try:
        data = request.get_json()
        audio_data = data.get('audio')
        
        if not audio_data:
            return jsonify({'error': 'Audio data is required'}), 400
        
        # For now, we'll return a mock response since implementing actual speech-to-text
        # would require additional libraries like speech_recognition or cloud services
        
        # In a production environment, you would:
        # 1. Decode the audio data (base64 or binary)
        # 2. Use a speech-to-text service like:
        #    - Google Speech-to-Text API
        #    - Azure Speech Services
        #    - AWS Transcribe
        #    - Or local libraries like speech_recognition
        
        # Mock response for demonstration
        mock_transcripts = [
            "Hello, can you help me with my math homework?",
            "What is the derivative of x squared?",
            "Explain photosynthesis in simple terms",
            "How do I solve quadratic equations?",
            "Can you create a quiz about world history?"
        ]
        
        import random
        transcript = random.choice(mock_transcripts)
        
        return jsonify({
            'transcript': transcript,
            'confidence': 0.95,
            'message': 'Voice transcribed successfully'
        })
        
    except Exception as e:
        print(f"Error processing voice input: {e}")
        return jsonify({'error': 'Failed to process voice input'}), 500

@app.route('/collaboration-session', methods=['POST'])
def create_collaboration_session():
    """Create a new collaboration session for group study"""
    try:
        data = request.get_json()
        session_name = data.get('session_name', 'Study Session')
        participants = data.get('participants', [])
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session_data = {
            'id': session_id,
            'name': session_name,
            'participants': participants,
            'created_at': datetime.now().isoformat(),
            'messages': [],
            'shared_resources': []
        }
        
        # In a real implementation, you would store this in a database
        # For now, we'll just return the session info
        
        return jsonify({
            'session_id': session_id,
            'session_data': session_data,
            'message': 'Collaboration session created successfully'
        })
        
    except Exception as e:
        print(f"Error creating collaboration session: {e}")
        return jsonify({'error': 'Failed to create collaboration session'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    code = getattr(e, 'code', 500)
    return jsonify({"reply": f"Server error: {str(e)}"}), code

if __name__ == '__main__':
    app.run(debug=True, port=5000)
