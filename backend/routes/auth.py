from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User, Patient

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required',
                'errors': ['Missing credentials']
            }), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                return jsonify({
                    'success': False,
                    'message': 'Account is deactivated',
                    'errors': ['Account deactivated']
                }), 401
            
            # Set session data
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['is_authenticated'] = True
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'user': user.to_dict()
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials',
                'errors': ['Invalid username or password']
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Login failed',
            'errors': [str(e)]
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'name', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field.title()} is required',
                    'errors': [f'Missing {field}']
                }), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'message': 'Username already exists',
                'errors': ['Username taken']
            }), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': 'Email already exists',
                'errors': ['Email taken']
            }), 400
        
        # Create new user (patients only can register)
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role='patient'
        )
        db.session.add(user)
        db.session.flush()
        
        # Create patient profile
        patient = Patient(
            user_id=user.id,
            name=data['name'],
            phone=data['phone'],
            address=data.get('address', ''),
            age=data.get('age'),
            gender=data.get('gender'),
            emergency_contact=data.get('emergency_contact', '')
        )
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'data': {
                'user': user.to_dict()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'errors': [str(e)]
        }), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    try:
        if not session.get('is_authenticated'):
            return jsonify({
                'success': False,
                'message': 'Not authenticated',
                'errors': ['Not logged in']
            }), 401
        
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            session.clear()
            return jsonify({
                'success': False,
                'message': 'User not found',
                'errors': ['User not found']
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'User retrieved successfully',
            'data': {
                'user': user.to_dict()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get user',
            'errors': [str(e)]
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logout successful',
            'data': {}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Logout failed',
            'errors': [str(e)]
        }), 500
