# import all models
from .user import User
from .patient import Patient  
from .doctor import Doctor, DoctorAvailability
from .appointment import Appointment
from .treatment import Treatment
from .medical_record import MedicalRecord
from .prescription import Prescription

__all__ = [
    'User',
    'Patient', 
    'Doctor',
    'DoctorAvailability',
    'Appointment',
    'Treatment',
    'MedicalRecord',
    'Prescription'
]
