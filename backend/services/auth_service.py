from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from backend.models import User

class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user and return token if valid"""
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.is_active:
                token = create_access_token(identity=user.id)
                return {
                    'success': True,
                    'token': token,
                    'user': user.to_dict()
                }
            else:
                return {
                    'success': False,
                    'message': 'Account is deactivated'
                }
        
        return {
            'success': False,
            'message': 'Invalid credentials'
        }
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def is_admin(user_id):
        """Check if user is admin"""
        user = User.query.get(user_id)
        return user and user.role == 'admin'
    
    @staticmethod
    def is_doctor(user_id):
        """Check if user is doctor"""
        user = User.query.get(user_id)
        return user and user.role == 'doctor'
    
    @staticmethod
    def is_patient(user_id):
        """Check if user is patient"""
        user = User.query.get(user_id)
        return user and user.role == 'patient'
