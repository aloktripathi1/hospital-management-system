from backend.app import db
from backend.models import Appointment, Doctor, Patient, DoctorAvailability
from datetime import datetime, date, time, timedelta

class AppointmentService:
    @staticmethod
    def check_availability(doctor_id, appointment_date, appointment_time):
        """Check if doctor is available at given date and time"""
        # Check if doctor exists and is active
        doctor = Doctor.query.get(doctor_id)
        if not doctor or not doctor.is_active:
            return False
        
        # Check if slot is already booked
        existing_appointment = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='booked'
        ).first()
        
        if existing_appointment:
            return False
        
        # Check doctor's availability schedule
        day_of_week = appointment_date.weekday()  # 0=Monday, 6=Sunday
        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=day_of_week,
            is_available=True
        ).first()
        
        if not availability:
            return False
        
        # Check if appointment time is within available hours
        if availability.start_time <= appointment_time <= availability.end_time:
            return True
        
        return False
    
    @staticmethod
    def book_appointment(patient_id, doctor_id, appointment_date, appointment_time, notes=''):
        """Book an appointment if available"""
        if not AppointmentService.check_availability(doctor_id, appointment_date, appointment_time):
            return {
                'success': False,
                'message': 'Time slot not available'
            }
        
        try:
            appointment = Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                notes=notes,
                status='booked'
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            return {
                'success': True,
                'appointment': appointment.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': str(e)
            }
    
    @staticmethod
    def get_upcoming_appointments(user_id, role):
        """Get upcoming appointments for user based on role"""
        today = date.today()
        
        if role == 'doctor':
            doctor = Doctor.query.filter_by(user_id=user_id).first()
            if not doctor:
                return []
            
            appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date >= today,
                Appointment.status == 'booked'
            ).order_by(
                Appointment.appointment_date.asc(),
                Appointment.appointment_time.asc()
            ).all()
            
        elif role == 'patient':
            patient = Patient.query.filter_by(user_id=user_id).first()
            if not patient:
                return []
            
            appointments = Appointment.query.filter(
                Appointment.patient_id == patient.id,
                Appointment.appointment_date >= today,
                Appointment.status == 'booked'
            ).order_by(
                Appointment.appointment_date.asc(),
                Appointment.appointment_time.asc()
            ).all()
            
        else:  # admin
            appointments = Appointment.query.filter(
                Appointment.appointment_date >= today,
                Appointment.status == 'booked'
            ).order_by(
                Appointment.appointment_date.asc(),
                Appointment.appointment_time.asc()
            ).all()
        
        return [appointment.to_dict() for appointment in appointments]
    
    @staticmethod
    def cancel_appointment(appointment_id, user_id, role):
        """Cancel an appointment"""
        appointment = Appointment.query.get(appointment_id)
        
        if not appointment:
            return {
                'success': False,
                'message': 'Appointment not found'
            }
        
        # Check permissions
        if role == 'patient':
            patient = Patient.query.filter_by(user_id=user_id).first()
            if not patient or appointment.patient_id != patient.id:
                return {
                    'success': False,
                    'message': 'Unauthorized'
                }
        elif role == 'doctor':
            doctor = Doctor.query.filter_by(user_id=user_id).first()
            if not doctor or appointment.doctor_id != doctor.id:
                return {
                    'success': False,
                    'message': 'Unauthorized'
                }
        # Admin can cancel any appointment
        
        if appointment.status != 'booked':
            return {
                'success': False,
                'message': 'Cannot cancel this appointment'
            }
        
        try:
            appointment.status = 'cancelled'
            appointment.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Appointment cancelled successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': str(e)
            }
