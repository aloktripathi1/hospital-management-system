# Models package - Hospital Management System

# Import all model classes
from .user import User
from .patient import Patient  
from .doctor import Doctor
from .appointment import Appointment
from .treatment import Treatment
from .department import Department

# Make all models available when importing from models
__all__ = [
    'User',
    'Patient', 
    'Doctor',
    'Appointment',
    'Treatment',
    'Department'
]