from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from backend.app import db
from backend.models import User, Patient

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
            
            access_token = create_access_token(identity=user.id)
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'token': access_token,
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
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found',
                'errors': ['Invalid token']
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
@jwt_required()
def logout():
    # In a real application, you might want to blacklist the token
    return jsonify({
        'success': True,
        'message': 'Logout successful',
        'data': {}
    })
