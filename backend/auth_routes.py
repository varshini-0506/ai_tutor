from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import bcrypt

auth = Blueprint('auth', __name__)

# Import users from main app to avoid conflicts
# This will be set by the main app
users = None

def set_users(user_list):
    global users
    users = user_list

@auth.route('/signup', methods=['POST'])
def signup():
    if not users:
        return jsonify({'msg': 'Users not initialized'}), 500
        
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'student')

    if not username or not password:
        return jsonify({'msg': 'Username and password are required'}), 400

    # Check if user already exists
    if any(u["username"] == username for u in users):
        return jsonify({'msg': 'Username already exists'}), 400

    # Add new user
    users.append({"username": username, "password": password, "role": role})
    
    return jsonify({'msg': 'Signup successful'}), 200

@auth.route('/login', methods=['POST'])
def login():
    if not users:
        return jsonify({'msg': 'Users not initialized'}), 500
        
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'msg': 'Username and password are required'}), 400

    # Find user
    user = next((u for u in users if u["username"] == username and u["password"] == password), None)
    
    if not user:
        return jsonify({'msg': 'Invalid credentials'}), 400

    # Create JWT token with string identity and role in claims
    access_token = create_access_token(identity=user["username"], additional_claims={"role": user["role"]})
    
    print(f"Generated JWT token for {username}: {access_token[:20]}...")
    
    return jsonify({
        'msg': 'Login successful',
        'access_token': access_token,
        'role': user["role"],
        'user': {
            'username': user["username"],
            'role': user["role"]
        }
    }), 200
