# Import functions from service modules
from .auth_service import authenticate_user, is_admin, is_doctor, is_patient
from .appointment_service import check_availability, book_appointment, get_upcoming_appointments, cancel_appointment

__all__ = [
    'authenticate_user', 'is_admin', 'is_doctor', 'is_patient',
    'check_availability', 'book_appointment', 'get_upcoming_appointments', 'cancel_appointment'
]
