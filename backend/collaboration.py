from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, JWTManager
import json
import os
from datetime import datetime
import uuid

collaboration = Blueprint('collaboration', __name__)

# Data storage (in production, use a proper database)
classrooms_file = 'classrooms.json'
team_quizzes_file = 'team_quizzes.json'

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def get_username_from_jwt():
    """Helper function to extract username from JWT identity"""
    user = get_jwt_identity()
    if isinstance(user, str):
        return user
    elif isinstance(user, dict):
        return user.get('username')
    return user

# Classroom Management
@collaboration.route('/test', methods=['GET'])
def test_route():
    """Test route to check if blueprint is working"""
    return jsonify({"message": "Collaboration blueprint is working"})

@collaboration.route('/test-jwt', methods=['GET'])
@jwt_required()
def test_jwt_route():
    """Test JWT validation in collaboration blueprint"""
    try:
        user = get_jwt_identity()
        print(f"Debug - Collaboration JWT test successful, user: {user}")
        return jsonify({"message": "JWT is working in collaboration blueprint", "user": user})
    except Exception as e:
        print(f"Debug - Collaboration JWT test failed: {str(e)}")
        return jsonify({"error": f"JWT test failed: {str(e)}"}), 401

@collaboration.route('/test-post', methods=['POST'])
@jwt_required()
def test_post_route():
    """Test POST route with JWT"""
    data = request.get_json()
    return jsonify({"message": "POST route working", "data": data})

@collaboration.route('/classrooms', methods=['GET'])
@jwt_required()
def get_classrooms():
    """Get all available classrooms"""
    try:
        print("Debug - get_classrooms called")
        print(f"Debug - Request headers: {dict(request.headers)}")
        print(f"Debug - Authorization header: {request.headers.get('Authorization')}")
        
        username = get_username_from_jwt()
        print(f"Debug - Username from JWT: {username}")
        
        classrooms = load_data(classrooms_file)
        print(f"Debug - Loaded {len(classrooms)} classrooms")
        
        return jsonify(classrooms)
    except Exception as e:
        print(f"Debug - Exception in get_classrooms: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@collaboration.route('/classrooms', methods=['POST'])
@jwt_required()
def create_classroom():
    """Create a new classroom"""
    try:
        print("Debug - create_classroom called")
        print(f"Debug - Request headers: {dict(request.headers)}")
        print(f"Debug - Authorization header: {request.headers.get('Authorization')}")
        
        username = get_username_from_jwt()
        data = request.get_json()
        
        print(f"Debug - Username: {username}")
        print(f"Debug - Data: {data}")
        print(f"Debug - Data type: {type(data)}")
        if data:
            print(f"Debug - Subject: {data.get('subject')} (type: {type(data.get('subject'))})")
            print(f"Debug - Name: {data.get('name')} (type: {type(data.get('name'))})")
            print(f"Debug - Description: {data.get('description')} (type: {type(data.get('description'))})")
            print(f"Debug - Max members: {data.get('max_members')} (type: {type(data.get('max_members'))})")
        
        if not data or not data.get('name'):
            return jsonify({"error": "Classroom name is required"}), 400
        
        if not username:
            return jsonify({"error": "Invalid user identity"}), 422
        
        # Ensure subject is a string
        subject = data.get('subject', 'General')
        if not isinstance(subject, str):
            subject = str(subject)
        
        classrooms = load_data(classrooms_file)
        
        new_classroom = {
            "id": str(uuid.uuid4()),
            "name": data['name'],
            "description": data.get('description', ''),
            "subject": subject,
            "created_by": username,
            "created_at": datetime.now().isoformat(),
            "members": [username],
            "max_members": data.get('max_members', 20),
            "is_active": True
        }
        
        print(f"Debug - New classroom: {new_classroom}")
        
        classrooms.append(new_classroom)
        save_data(classrooms, classrooms_file)
        
        return jsonify(new_classroom), 201
    except Exception as e:
        print(f"Debug - Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@collaboration.route('/classrooms/<classroom_id>/join', methods=['POST'])
@jwt_required()
def join_classroom(classroom_id):
    """Join a classroom"""
    username = get_username_from_jwt()
    classrooms = load_data(classrooms_file)
    
    classroom = next((c for c in classrooms if c['id'] == classroom_id), None)
    if not classroom:
        return jsonify({"error": "Classroom not found"}), 404
    
    if username in classroom['members']:
        return jsonify({"error": "Already a member of this classroom"}), 400
    
    if len(classroom['members']) >= classroom['max_members']:
        return jsonify({"error": "Classroom is full"}), 400
    
    classroom['members'].append(username)
    save_data(classrooms, classrooms_file)
    
    return jsonify({"message": "Successfully joined classroom", "classroom": classroom})

@collaboration.route('/classrooms/<classroom_id>/leave', methods=['POST'])
@jwt_required()
def leave_classroom(classroom_id):
    """Leave a classroom"""
    username = get_username_from_jwt()
    classrooms = load_data(classrooms_file)
    
    classroom = next((c for c in classrooms if c['id'] == classroom_id), None)
    if not classroom:
        return jsonify({"error": "Classroom not found"}), 404
    
    if username not in classroom['members']:
        return jsonify({"error": "Not a member of this classroom"}), 400
    
    classroom['members'].remove(username)
    
    # If no members left, delete the classroom
    if not classroom['members']:
        classrooms = [c for c in classrooms if c['id'] != classroom_id]
    else:
        # If creator left, transfer ownership to first member
        if classroom['created_by'] == username:
            classroom['created_by'] = classroom['members'][0]
    
    save_data(classrooms, classrooms_file)
    return jsonify({"message": "Successfully left classroom"})

@collaboration.route('/classrooms/<classroom_id>', methods=['DELETE'])
@jwt_required()
def delete_classroom(classroom_id):
    """Delete a classroom (only by owner)"""
    username = get_username_from_jwt()
    classrooms = load_data(classrooms_file)
    
    classroom = next((c for c in classrooms if c['id'] == classroom_id), None)
    if not classroom:
        return jsonify({"error": "Classroom not found"}), 404
    
    if classroom['created_by'] != username:
        return jsonify({"error": "Only the classroom owner can delete the classroom"}), 403
    
    # Remove the classroom
    classrooms = [c for c in classrooms if c['id'] != classroom_id]
    save_data(classrooms, classrooms_file)
    
    return jsonify({"message": "Classroom deleted successfully"})

@collaboration.route('/classrooms/<classroom_id>/members', methods=['POST'])
@jwt_required()
def add_member(classroom_id):
    """Add a member to a classroom (only by owner)"""
    username = get_username_from_jwt()
    data = request.get_json()
    new_member = data.get('username')
    
    if not new_member:
        return jsonify({"error": "Username is required"}), 400
    
    classrooms = load_data(classrooms_file)
    classroom = next((c for c in classrooms if c['id'] == classroom_id), None)
    
    if not classroom:
        return jsonify({"error": "Classroom not found"}), 404
    
    if classroom['created_by'] != username:
        return jsonify({"error": "Only the classroom owner can add members"}), 403
    
    if new_member in classroom['members']:
        return jsonify({"error": "User is already a member"}), 400
    
    if len(classroom['members']) >= classroom['max_members']:
        return jsonify({"error": "Classroom is full"}), 400
    
    classroom['members'].append(new_member)
    save_data(classrooms, classrooms_file)
    
    return jsonify({"message": f"Successfully added {new_member} to classroom"})

@collaboration.route('/classrooms/<classroom_id>/members/<member_username>', methods=['DELETE'])
@jwt_required()
def remove_member(classroom_id, member_username):
    """Remove a member from a classroom (only by owner)"""
    username = get_username_from_jwt()
    classrooms = load_data(classrooms_file)
    classroom = next((c for c in classrooms if c['id'] == classroom_id), None)
    
    if not classroom:
        return jsonify({"error": "Classroom not found"}), 404
    
    if classroom['created_by'] != username:
        return jsonify({"error": "Only the classroom owner can remove members"}), 403
    
    if member_username not in classroom['members']:
        return jsonify({"error": "User is not a member of this classroom"}), 400
    
    if member_username == classroom['created_by']:
        return jsonify({"error": "Cannot remove the classroom owner"}), 400
    
    classroom['members'].remove(member_username)
    save_data(classrooms, classrooms_file)
    
    return jsonify({"message": f"Successfully removed {member_username} from classroom"})

# Team Quiz Management
@collaboration.route('/team-quizzes', methods=['GET'])
@jwt_required()
def get_team_quizzes():
    """Get all team quizzes"""
    team_quizzes = load_data(team_quizzes_file)
    return jsonify(team_quizzes)

@collaboration.route('/team-quizzes', methods=['POST'])
@jwt_required()
def create_team_quiz():
    """Create a new team quiz session"""
    username = get_username_from_jwt()
    data = request.get_json()
    
    if not data or not data.get('classroom_id') or not data.get('quiz_data'):
        return jsonify({"error": "Classroom ID and quiz data are required"}), 400
    
    # Verify user is in the classroom
    classrooms = load_data(classrooms_file)
    classroom = next((c for c in classrooms if c['id'] == data['classroom_id']), None)
    if not classroom or username not in classroom['members']:
        return jsonify({"error": "Not a member of this classroom"}), 403
    
    team_quizzes = load_data(team_quizzes_file)
    
    new_quiz = {
        "id": str(uuid.uuid4()),
        "classroom_id": data['classroom_id'],
        "classroom_name": classroom['name'],
        "created_by": username,
        "created_at": datetime.now().isoformat(),
        "quiz_data": data['quiz_data'],
        "status": "waiting",  # waiting, active, completed
        "participants": [username],
        "scores": {},
        "current_question": 0,
        "time_limit": data.get('time_limit', 30),  # seconds per question
        "team_mode": data.get('team_mode', True)
    }
    
    team_quizzes.append(new_quiz)
    save_data(team_quizzes, team_quizzes_file)
    
    return jsonify(new_quiz), 201

@collaboration.route('/team-quizzes/<quiz_id>/join', methods=['POST'])
@jwt_required()
def join_team_quiz(quiz_id):
    """Join a team quiz session"""
    username = get_username_from_jwt()
    team_quizzes = load_data(team_quizzes_file)
    
    quiz = next((q for q in team_quizzes if q['id'] == quiz_id), None)
    if not quiz:
        return jsonify({"error": "Quiz session not found"}), 404
    
    if quiz['status'] != 'waiting':
        return jsonify({"error": "Quiz session has already started or ended"}), 400
    
    if username in quiz['participants']:
        return jsonify({"error": "Already participating in this quiz"}), 400
    
    # Verify user is in the classroom
    classrooms = load_data(classrooms_file)
    classroom = next((c for c in classrooms if c['id'] == quiz['classroom_id']), None)
    if not classroom or username not in classroom['members']:
        return jsonify({"error": "Not a member of this classroom"}), 403
    
    quiz['participants'].append(username)
    quiz['scores'][username] = 0
    save_data(team_quizzes, team_quizzes_file)
    
    return jsonify({"message": "Successfully joined quiz", "quiz": quiz})

@collaboration.route('/team-quizzes/<quiz_id>/start', methods=['POST'])
@jwt_required()
def start_team_quiz(quiz_id):
    """Start a team quiz session"""
    username = get_username_from_jwt()
    team_quizzes = load_data(team_quizzes_file)
    
    quiz = next((q for q in team_quizzes if q['id'] == quiz_id), None)
    if not quiz:
        return jsonify({"error": "Quiz session not found"}), 404
    
    if quiz['created_by'] != username:
        return jsonify({"error": "Only the quiz creator can start the session"}), 403
    
    if quiz['status'] != 'waiting':
        return jsonify({"error": "Quiz session has already started or ended"}), 400
    
    quiz['status'] = 'active'
    quiz['started_at'] = datetime.now().isoformat()
    save_data(team_quizzes, team_quizzes_file)
    
    return jsonify({"message": "Quiz session started", "quiz": quiz})

@collaboration.route('/team-quizzes/<quiz_id>/submit-answer', methods=['POST'])
@jwt_required()
def submit_quiz_answer(quiz_id):
    """Submit an answer for the current question"""
    username = get_username_from_jwt()
    data = request.get_json()
    
    if not data or 'answer' not in data:
        return jsonify({"error": "Answer is required"}), 400
    
    team_quizzes = load_data(team_quizzes_file)
    quiz = next((q for q in team_quizzes if q['id'] == quiz_id), None)
    
    if not quiz:
        return jsonify({"error": "Quiz session not found"}), 404
    
    if quiz['status'] != 'active':
        return jsonify({"error": "Quiz session is not active"}), 400
    
    if username not in quiz['participants']:
        return jsonify({"error": "Not participating in this quiz"}), 403
    
    # Check if answer is correct
    current_question = quiz['quiz_data']['questions'][quiz['current_question']]
    is_correct = data['answer'] == current_question['correct_answer']
    
    if is_correct:
        quiz['scores'][username] += 1
    
    # Move to next question or end quiz
    quiz['current_question'] += 1
    if quiz['current_question'] >= len(quiz['quiz_data']['questions']):
        quiz['status'] = 'completed'
        quiz['completed_at'] = datetime.now().isoformat()
    
    save_data(team_quizzes, team_quizzes_file)
    
    return jsonify({
        "correct": is_correct,
        "next_question": quiz['current_question'] < len(quiz['quiz_data']['questions']),
        "quiz_completed": quiz['status'] == 'completed'
    })

@collaboration.route('/team-quizzes/<quiz_id>', methods=['GET'])
@jwt_required()
def get_team_quiz(quiz_id):
    """Get details of a specific team quiz"""
    username = get_username_from_jwt()
    team_quizzes = load_data(team_quizzes_file)
    
    quiz = next((q for q in team_quizzes if q['id'] == quiz_id), None)
    if not quiz:
        return jsonify({"error": "Quiz session not found"}), 404
    
    if username not in quiz['participants']:
        return jsonify({"error": "Not participating in this quiz"}), 403
    
    return jsonify(quiz)

# Chat/Communication (Simple implementation)
@collaboration.route('/classrooms/<classroom_id>/messages', methods=['GET'])
@jwt_required()
def get_classroom_messages(classroom_id):
    """Get chat messages for a classroom"""
    username = get_username_from_jwt()
    classrooms = load_data(classrooms_file)
    
    classroom = next((c for c in classrooms if c['id'] == classroom_id), None)
    if not classroom or username not in classroom['members']:
        return jsonify({"error": "Not a member of this classroom"}), 403
    
    messages_file = f'messages_{classroom_id}.json'
    messages = load_data(messages_file)
    return jsonify(messages)

@collaboration.route('/classrooms/<classroom_id>/messages', methods=['POST'])
@jwt_required()
def send_classroom_message(classroom_id):
    """Send a message to classroom chat"""
    username = get_username_from_jwt()
    data = request.get_json()
    
    if not data or not data.get('message'):
        return jsonify({"error": "Message is required"}), 400
    
    classrooms = load_data(classrooms_file)
    classroom = next((c for c in classrooms if c['id'] == classroom_id), None)
    if not classroom or username not in classroom['members']:
        return jsonify({"error": "Not a member of this classroom"}), 403
    
    messages_file = f'messages_{classroom_id}.json'
    messages = load_data(messages_file)
    
    new_message = {
        "id": str(uuid.uuid4()),
        "sender": username,
        "message": data['message'],
        "timestamp": datetime.now().isoformat(),
        "type": data.get('type', 'text')  # text, system, quiz
    }
    
    messages.append(new_message)
    save_data(messages, messages_file)
    
    return jsonify(new_message), 201 