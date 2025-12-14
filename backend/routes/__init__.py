# import all route blueprints
from .auth import auth_bp
from .patient import patient_bp  
from .doctor import doctor_bp
from .admin import admin_bp
from .medical import medical_bp
from .prescription import prescription_bp
from .payment import payment_bp

__all__ = ['auth_bp', 'patient_bp', 'doctor_bp', 'admin_bp', 'medical_bp', 'prescription_bp', 'payment_bp']