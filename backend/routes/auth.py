from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User, Patient, Doctor

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required', 'errors': ['Missing credentials']}), 400

    user = User.query.filter_by(username=username).first()

    if user is not None:
        if check_password_hash(user.password_hash, password):
            if user.is_active:
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                session['is_authenticated'] = True
                return jsonify({'success': True, 'message': 'Login successful', 'data': {'user': user.to_dict()}})
            else:
                return jsonify({'success': False, 'message': 'Account is deactivated', 'errors': ['Account deactivated']}), 401
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials', 'errors': ['Invalid username or password']}), 401
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials', 'errors': ['Invalid username or password']}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if not username:
        return jsonify({'success': False, 'message': 'Username is required', 'errors': ['Missing username']}), 400
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required', 'errors': ['Missing email']}), 400
    
    if not password:
        return jsonify({'success': False, 'message': 'Password is required', 'errors': ['Missing password']}), 400
    
    if not name:
        return jsonify({'success': False, 'message': 'Name is required', 'errors': ['Missing name']}), 400
    
    existing = User.query.filter_by(username=username).first()
    if existing:
        return jsonify({'success': False, 'message': 'Username already exists', 'errors': ['Username taken']}), 400
    
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({'success': False, 'message': 'Email already exists', 'errors': ['Email taken']}), 400
    
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role='patient'
    )
    db.session.add(user)
    db.session.flush()
    
    patient = Patient(
        user_id=user.id,
        name=name,
        phone=data.get('phone', ''),
        address=data.get('address', ''),
        age=data.get('age'),
        gender=data.get('gender', ''),
        emergency_contact=data.get('emergency_contact', '')
    )
    db.session.add(patient)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Registration successful! Please login to complete your profile with additional information.', 'data': {'user': user.to_dict()}})

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    is_auth = session.get('is_authenticated')
    if not is_auth:
        return jsonify({'success': False, 'message': 'Not authenticated', 'errors': ['Not logged in']}), 401
    
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if user is None:
        session.clear()
        return jsonify({'success': False, 'message': 'User not found', 'errors': ['User not found']}), 404
    
    data = user.to_dict()
    
    if user.role == 'patient' and user.patient:
        data['name'] = user.patient.name
    elif user.role == 'doctor' and user.doctor:
        data['name'] = user.doctor.name
    elif user.role == 'admin':
        data['name'] = 'Administrator'
    else:
        data['name'] = user.username
    
    return jsonify({'success': True, 'message': 'User retrieved successfully', 'data': {'user': data}})

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logout successful', 'data': {}})