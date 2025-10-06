# Routes package - Hospital Management System  

# Import all route blueprints
from .auth import auth_bp
from .patient import patient_bp  
from .doctor import doctor_bp
from .admin import admin_bp

# Make all routes available when importing from routes
__all__ = [
    'auth_bp',
    'patient_bp',
    'doctor_bp', 
    'admin_bp'
]