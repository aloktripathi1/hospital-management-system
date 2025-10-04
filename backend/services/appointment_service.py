from app import db
from models import Appointment, Doctor, Patient, DoctorAvailability
from datetime import datetime, date

# ----------- Check Availability -----------
def check_availability(doc_id, appt_date, appt_time):
    # Check if doctor exists and active
    doc = Doctor.query.get(doc_id)
    if not doc or not doc.is_active:
        return False
    
    # Check if slot already booked
    existing = Appointment.query.filter_by(
        doctor_id=doc_id,
        appointment_date=appt_date,
        appointment_time=appt_time,
        status='booked'
    ).first()
    
    if existing:
        return False
    
    # Check doctor availability schedule
    day = appt_date.weekday()
    availability = DoctorAvailability.query.filter_by(
        doctor_id=doc_id,
        day_of_week=day,
        is_available=True
    ).first()
    
    if not availability:
        return False
    
    # Check if time is within available hours
    if availability.start_time <= appt_time <= availability.end_time:
        return True
    
    return False

# ----------- Book Appointment -----------
def book_appointment(pt_id, doc_id, appt_date, appt_time, notes=''):
    if not check_availability(doc_id, appt_date, appt_time):
        return {'success': False, 'message': 'Slot not available'}
    
    appt = Appointment(
        patient_id=pt_id,
        doctor_id=doc_id,
        appointment_date=appt_date,
        appointment_time=appt_time,
        notes=notes,
        status='booked'
    )
    
    db.session.add(appt)
    db.session.commit()
    
    return {'success': True, 'appointment': appt.to_dict()}

# ----------- Get Upcoming Appointments -----------
def get_upcoming_appointments(user_id, role):
    today = date.today()
    
    if role == 'doctor':
        doc = Doctor.query.filter_by(user_id=user_id).first()
        if not doc:
            return []
        
        appts = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.appointment_date >= today,
            Appointment.status == 'booked'
        ).order_by(
            Appointment.appointment_date.asc(),
            Appointment.appointment_time.asc()
        ).all()
        
    elif role == 'patient':
        pt = Patient.query.filter_by(user_id=user_id).first()
        if not pt:
            return []
        
        appts = Appointment.query.filter(
            Appointment.patient_id == pt.id,
            Appointment.appointment_date >= today,
            Appointment.status == 'booked'
        ).order_by(
            Appointment.appointment_date.asc(),
            Appointment.appointment_time.asc()
        ).all()
        
    else:  # admin
        appts = Appointment.query.filter(
            Appointment.appointment_date >= today,
            Appointment.status == 'booked'
        ).order_by(
            Appointment.appointment_date.asc(),
            Appointment.appointment_time.asc()
        ).all()
    
    return [appt.to_dict() for appt in appts]

# ----------- Cancel Appointment -----------
def cancel_appointment(appt_id, user_id, role):
    appt = Appointment.query.get(appt_id)
    
    if not appt:
        return {'success': False, 'message': 'Appointment not found'}
    
    # Check permissions
    if role == 'patient':
        pt = Patient.query.filter_by(user_id=user_id).first()
        if not pt or appt.patient_id != pt.id:
            return {'success': False, 'message': 'Unauthorized'}
    
    elif role == 'doctor':
        doc = Doctor.query.filter_by(user_id=user_id).first()
        if not doc or appt.doctor_id != doc.id:
            return {'success': False, 'message': 'Unauthorized'}
    
    if appt.status != 'booked':
        return {'success': False, 'message': 'Cannot cancel this appointment'}
    
    appt.status = 'cancelled'
    appt.updated_at = datetime.utcnow()
    db.session.commit()
    
    return {'success': True, 'message': 'Appointment cancelled'}