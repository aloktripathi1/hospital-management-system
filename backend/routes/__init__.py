# Routes package - Hospital Management System  

# Import all route blueprints
from .auth import auth_routes
from .patient import patient_routes  
from .doctor import doctor_routes
from .admin import admin_routes

# Make all routes available when importing from routes
__all__ = [
    'auth_routes',
    'patient_routes',
    'doctor_routes', 
    'admin_routes'
]