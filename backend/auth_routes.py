from flask import Blueprint, request, jsonify
from db import conn, cursor
import bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')  # default to 'student' if not provided

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({'msg': 'Email already exists'}), 400

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
        (name, email, hashed_pw, role)
    )
    conn.commit()
    return jsonify({'msg': 'Signup successful'}), 200


@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user is None:
        return jsonify({'msg': 'Invalid credentials'}), 400

    stored_hash = user[2]  # assuming columns: id, email, password, name, role

    if not bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return jsonify({'msg': 'Invalid credentials'}), 400

    user_data = {
        'id': user[0],
        'email': user[1],
        'name': user[3],
        'role': user[4]
    }
    return jsonify({'msg': 'Login successful', 'user': user_data}), 200
