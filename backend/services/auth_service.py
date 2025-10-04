from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from models import User

# ----------- Authenticate User -----------
def authenticate_user(uname, pwd):
    user = User.query.filter_by(username=uname).first()
    
    if user and check_password_hash(user.password_hash, pwd):
        if user.is_active:
            token = create_access_token(identity=user.id)
            return {
                'success': True,
                'token': token,
                'user': user.to_dict()
            }
        else:
            return {'success': False, 'message': 'Account deactivated'}
    
    return {'success': False, 'message': 'Invalid credentials'}

# ----------- Get User by ID -----------
def get_user_by_id(user_id):
    return User.query.get(user_id)

# ----------- Check if Admin -----------
def is_admin(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'admin'

# ----------- Check if Doctor -----------
def is_doctor(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'doctor'

# ----------- Check if Patient -----------
def is_patient(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'patient'