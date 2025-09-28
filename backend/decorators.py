from functools import wraps
from flask import session, jsonify

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({
                'success': False,
                'message': 'Authentication required',
                'errors': ['Please login first']
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({
                'success': False,
                'message': 'Authentication required',
                'errors': ['Please login first']
            }), 401
        
        if session.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required',
                'errors': ['Insufficient permissions']
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({
                'success': False,
                'message': 'Authentication required',
                'errors': ['Please login first']
            }), 401
        
        if session.get('role') != 'doctor':
            return jsonify({
                'success': False,
                'message': 'Doctor access required',
                'errors': ['Insufficient permissions']
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_authenticated'):
            return jsonify({
                'success': False,
                'message': 'Authentication required',
                'errors': ['Please login first']
            }), 401
        
        if session.get('role') != 'patient':
            return jsonify({
                'success': False,
                'message': 'Patient access required',
                'errors': ['Insufficient permissions']
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function