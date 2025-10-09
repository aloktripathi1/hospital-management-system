from functools import wraps
from flask import session, jsonify

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({'success': False, 'message': 'Please login first'}), 401
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({'success': False, 'message': 'Please login first'}), 401
        
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access only'}), 403
        
        return f(*args, **kwargs)
    return wrapper

def doctor_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({'success': False,'message': 'Please login first'}), 401
        
        if session.get('role') != 'doctor':
            return jsonify({
                'success': False,
                'message': 'Doctor access only'
            }), 403
        
        return f(*args, **kwargs)
    return wrapper

def patient_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
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
    return wrapper

def patient_or_admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({
                'success': False,
                'message': 'Please login first'
            }), 401
        
        role = session.get('role')
        if role not in ['patient', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Patient or admin access only'
            }), 403
        
        return f(*args, **kwargs)
    return wrapper