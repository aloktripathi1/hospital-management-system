from functools import wraps
from flask import session, jsonify

# ----------- Login Required Decorator -----------
def login_required(f):
    @wraps(f)
    def check_login(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({'success': False, 'message': 'Please login first'}), 401
        return f(*args, **kwargs)
    return check_login

# ----------- Admin Required Decorator -----------
def admin_required(f):
    @wraps(f)
    def check_admin(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({'success': False, 'message': 'Please login first'}), 401
        
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access only'}), 403
        
        return f(*args, **kwargs)
    return check_admin

# ----------- Doctor Required Decorator -----------
def doctor_required(f):
    @wraps(f)
    def check_doctor(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({'success': False,'message': 'Please login first'}), 401
        
        if session.get('role') != 'doctor':
            return jsonify({
                'success': False,
                'message': 'Doctor access only'
            }), 403
        
        return f(*args, **kwargs)
    return check_doctor

# ----------- Patient Required Decorator -----------
def patient_required(f):
    @wraps(f)
    def check_patient(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({
                'success': False,
                'message': 'Please login first'
            }), 401
        
        if session.get('role') != 'patient':
            return jsonify({
                'success': False,
                'message': 'Patient access only'
            }), 403
        
        return f(*args, **kwargs)
    return check_patient

# ----------- Patient or Admin Required Decorator -----------
def patient_or_admin_required(f):
    @wraps(f)
    def check_patient_or_admin(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({
                'success': False,
                'message': 'Please login first'
            }), 401
        
        user_role = session.get('role')
        if user_role not in ['patient', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Patient or admin access only'
            }), 403
        
        return f(*args, **kwargs)
    return check_patient_or_admin