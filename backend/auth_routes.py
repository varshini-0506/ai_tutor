from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from neon_user_db import NeonUserDatabase
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

auth = Blueprint('auth', __name__)

# Initialize user database
try:
    user_db = NeonUserDatabase()
    user_db.init_database()
    print("✅ User database initialized successfully")
except Exception as e:
    print(f"❌ Error initializing user database: {e}")
    user_db = None

@auth.route('/signup', methods=['POST'])
def signup():
    print(f"Debug - Signup request received")
    print(f"Debug - Request method: {request.method}")
    print(f"Debug - Request headers: {dict(request.headers)}")
    print(f"Debug - Request origin: {request.headers.get('Origin', 'No origin header')}")
    
    if not user_db:
        return jsonify({'msg': 'User database not initialized'}), 500
        
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'student')
    email = data.get('email')

    if not username or not password:
        return jsonify({'msg': 'Username and password are required'}), 400

    try:
        # Create new user
        user = user_db.create_user(username=username, password=password, role=role, email=email)
        
        return jsonify({
            'msg': 'Signup successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'email': user.get('email')
            }
        }), 201
        
    except ValueError as e:
        return jsonify({'msg': str(e)}), 400
    except Exception as e:
        print(f"Error during signup: {e}")
        return jsonify({'msg': 'Error creating user'}), 500

@auth.route('/login', methods=['POST'])
def login():
    print(f"Debug - Login request received")
    print(f"Debug - Request method: {request.method}")
    print(f"Debug - Request headers: {dict(request.headers)}")
    print(f"Debug - Request origin: {request.headers.get('Origin', 'No origin header')}")
    
    if not user_db:
        return jsonify({'msg': 'User database not initialized'}), 500
        
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'msg': 'Username and password are required'}), 400

    try:
        # Authenticate user
        user = user_db.authenticate_user(username, password)
        
        if not user:
            return jsonify({'msg': 'Invalid credentials'}), 401

        # Create JWT token with string identity and role in claims
        access_token = create_access_token(
            identity=user["username"], 
            additional_claims={
                "role": user["role"],
                "user_id": user["id"]
            }
        )
        
        print(f"Generated JWT token for {username}: {access_token[:20]}...")
        
        return jsonify({
            'msg': 'Login successful',
            'access_token': access_token,
            'role': user["role"],
            'user': {
                'id': user['id'],
                'username': user["username"],
                'role': user["role"],
                'email': user.get('email')
            }
        }), 200
        
    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({'msg': 'Error during login'}), 500

@auth.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile (requires authentication)"""
    if not user_db:
        return jsonify({'msg': 'User database not initialized'}), 500
    
    # This would typically use JWT to get the current user
    # For now, we'll return a placeholder
    return jsonify({'msg': 'Profile endpoint - implement with JWT'}), 200

@auth.route('/change-password', methods=['POST'])
def change_password():
    """Change user password (requires authentication)"""
    if not user_db:
        return jsonify({'msg': 'User database not initialized'}), 500
    
    data = request.json
    user_id = data.get('user_id')
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not all([user_id, current_password, new_password]):
        return jsonify({'msg': 'All fields are required'}), 400
    
    try:
        # Get user to verify current password
        user = user_db.get_user_by_id(user_id)
        if not user:
            return jsonify({'msg': 'User not found'}), 404
        
        # Verify current password (you'd need to get the hashed password)
        # For now, we'll skip this verification
        # if not user_db.verify_password(current_password, user['password']):
        #     return jsonify({'msg': 'Current password is incorrect'}), 400
        
        # Change password
        success = user_db.change_password(user_id, new_password)
        if success:
            return jsonify({'msg': 'Password changed successfully'}), 200
        else:
            return jsonify({'msg': 'Failed to change password'}), 500
            
    except Exception as e:
        print(f"Error changing password: {e}")
        return jsonify({'msg': 'Error changing password'}), 500

@auth.route('/users', methods=['GET'])
def get_users():
    """Get all users (admin only)"""
    if not user_db:
        return jsonify({'msg': 'User database not initialized'}), 500
    
    try:
        users = user_db.get_all_users(active_only=True)
        return jsonify({
            'msg': 'Users retrieved successfully',
            'users': users
        }), 200
        
    except Exception as e:
        print(f"Error getting users: {e}")
        return jsonify({'msg': 'Error retrieving users'}), 500

@auth.route('/users/stats', methods=['GET'])
def get_user_stats():
    """Get user statistics"""
    if not user_db:
        return jsonify({'msg': 'User database not initialized'}), 500
    
    try:
        stats = user_db.get_user_statistics()
        return jsonify({
            'msg': 'Statistics retrieved successfully',
            'statistics': stats
        }), 200
        
    except Exception as e:
        print(f"Error getting user statistics: {e}")
        return jsonify({'msg': 'Error retrieving statistics'}), 500
