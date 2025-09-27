from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Patient, Doctor, Appointment, Treatment, DoctorAvailability
from datetime import datetime, date, time

patient_bp = Blueprint('patient', __name__)

def patient_required(f):
    """Decorator to ensure user is patient"""
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != 'patient':
            return jsonify({
                'success': False,
                'message': 'Patient access required',
                'errors': ['Unauthorized']
            }), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@patient_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@patient_required
def get_dashboard():
    try:
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient profile not found',
                'errors': ['Profile not found']
            }), 404
        
        # Get upcoming appointments
        upcoming_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date >= date.today(),
            Appointment.status == 'booked'
        ).count()
        
        # Get total appointments
        total_appointments = Appointment.query.filter_by(patient_id=patient.id).count()
        
        # Get unique doctors visited
        doctors_visited = db.session.query(Appointment.doctor_id).filter_by(
            patient_id=patient.id
        ).distinct().count()
        
        return jsonify({
            'success': True,
            'message': 'Dashboard data retrieved',
            'data': {
                'patient': patient.to_dict(),
                'upcoming_appointments': upcoming_appointments,
                'total_appointments': total_appointments,
                'doctors_visited': doctors_visited
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get dashboard data',
            'errors': [str(e)]
        }), 500

@patient_bp.route('/departments', methods=['GET'])
@jwt_required()
@patient_required
def get_departments():
    try:
        from models import Department
        
        # Get all active departments
        departments = Department.query.filter_by(is_active=True).all()
        
        department_list = []
        for dept in departments:
            doctor_count = Doctor.query.filter_by(
                department_id=dept.id,
                is_active=True
            ).count()
            
            department_list.append({
                'id': dept.id,
                'name': dept.name,
                'description': dept.description,
                'doctor_count': doctor_count
            })
        
        return jsonify({
            'success': True,
            'message': 'Departments retrieved successfully',
            'data': {
                'departments': department_list
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get departments',
            'errors': [str(e)]
        }), 500

@patient_bp.route('/available-slots', methods=['GET'])
@jwt_required()
@patient_required
def get_available_slots():
    """Get available appointment slots for a doctor on a specific date"""
    try:
        doctor_id = request.args.get('doctor_id')
        appointment_date = request.args.get('date')
        
        if not doctor_id or not appointment_date:
            return jsonify({
                'success': False,
                'message': 'Doctor ID and date are required',
                'errors': ['Missing required parameters']
            }), 400
        
        try:
            appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid date format',
                'errors': ['Use YYYY-MM-DD format']
            }), 400
        
        # Get available slots for the doctor on the specified date
        available_slots = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            status='available'
        ).order_by(Appointment.appointment_time.asc()).all()
        
        # Get booked slots to show as unavailable
        booked_slots = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            status='booked'
        ).order_by(Appointment.appointment_time.asc()).all()
        
        slots_data = []
        
        # Add available slots
        for slot in available_slots:
            slots_data.append({
                'id': slot.id,
                'time': slot.appointment_time.strftime('%H:%M'),
                'status': 'available',
                'patient_id': None
            })
        
        # Add booked slots
        for slot in booked_slots:
            slots_data.append({
                'id': slot.id,
                'time': slot.appointment_time.strftime('%H:%M'),
                'status': 'booked',
                'patient_id': slot.patient_id
            })
        
        return jsonify({
            'success': True,
            'message': 'Available slots retrieved successfully',
            'data': {
                'slots': slots_data,
                'date': appointment_date.isoformat(),
                'doctor_id': doctor_id
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get available slots',
            'errors': [str(e)]
        }), 500

@patient_bp.route('/doctors', methods=['GET'])
@jwt_required()
@patient_required
def get_doctors():
    try:
        specialization = request.args.get('specialization')
        
        query = Doctor.query.filter_by(is_active=True)
        
        if specialization:
            query = query.filter_by(specialization=specialization)
        
        doctors = query.all()
        
        return jsonify({
            'success': True,
            'message': 'Doctors retrieved successfully',
            'data': {
                'doctors': [doctor.to_dict() for doctor in doctors]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get doctors',
            'errors': [str(e)]
        }), 500

@patient_bp.route('/appointments', methods=['GET'])
@jwt_required()
@patient_required
def get_appointments():
    try:
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient profile not found',
                'errors': ['Profile not found']
            }), 404
        
        status_filter = request.args.get('status')
        
        query = Appointment.query.filter_by(patient_id=patient.id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        appointments = query.order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'message': 'Appointments retrieved successfully',
            'data': {
                'appointments': [appointment.to_dict() for appointment in appointments]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get appointments',
            'errors': [str(e)]
        }), 500

@patient_bp.route('/appointments', methods=['POST'])
@jwt_required()
@patient_required
def book_appointment():
    try:
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient profile not found',
                'errors': ['Profile not found']
            }), 404
        
        data = request.get_json()
        
        required_fields = ['doctor_id', 'appointment_date', 'appointment_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field.replace("_", " ").title()} is required',
                    'errors': [f'Missing {field}']
                }), 400
        
        doctor = Doctor.query.get(data['doctor_id'])
        if not doctor or not doctor.is_active:
            return jsonify({
                'success': False,
                'message': 'Doctor not found or inactive',
                'errors': ['Invalid doctor']
            }), 404
        
        # Parse date and time
        try:
            appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid date or time format',
                'errors': ['Invalid format']
            }), 400
        
        # Find available slot
        available_slot = Appointment.query.filter_by(
            doctor_id=data['doctor_id'],
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='available'
        ).first()
        
        if not available_slot:
            return jsonify({
                'success': False,
                'message': 'Time slot not available',
                'errors': ['This time slot is not available for booking']
            }), 400
        
        # Check for existing appointment at the same time for this patient
        existing_appointment = Appointment.query.filter_by(
            patient_id=patient.id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).first()
        
        if existing_appointment:
            return jsonify({
                'success': False,
                'message': 'You already have an appointment at this time',
                'errors': ['Time slot already booked']
            }), 400
        
        # Book the slot
        available_slot.patient_id = patient.id
        available_slot.status = 'booked'
        available_slot.notes = data.get('notes', '')
        available_slot.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment booked successfully',
            'data': {
                'appointment': available_slot.to_dict()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to book appointment',
            'errors': [str(e)]
        }), 500

@patient_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
@patient_required
def cancel_appointment(appointment_id):
    try:
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient profile not found',
                'errors': ['Profile not found']
            }), 404
        
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            patient_id=patient.id
        ).first()
        
        if not appointment:
            return jsonify({
                'success': False,
                'message': 'Appointment not found',
                'errors': ['Appointment not found']
            }), 404
        
        if appointment.status != 'booked':
            return jsonify({
                'success': False,
                'message': 'Cannot cancel this appointment',
                'errors': ['Invalid status']
            }), 400
        
        appointment.status = 'cancelled'
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment cancelled successfully',
            'data': {}
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to cancel appointment',
            'errors': [str(e)]
        }), 500

@patient_bp.route('/history', methods=['GET'])
@jwt_required()
@patient_required
def get_history():
    try:
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient profile not found',
                'errors': ['Profile not found']
            }), 404
        
        # Get treatment history
        treatments = db.session.query(Treatment).join(Appointment).filter(
            Appointment.patient_id == patient.id
        ).order_by(Treatment.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'message': 'Patient history retrieved successfully',
            'data': {
                'treatments': [treatment.to_dict() for treatment in treatments]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get patient history',
            'errors': [str(e)]
        }), 500

@patient_bp.route('/doctor/availability/<int:doctor_id>', methods=['GET'])
@jwt_required()
@patient_required
def get_doctor_availability(doctor_id):
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor or not doctor.is_active:
            return jsonify({
                'success': False,
                'message': 'Doctor not found or inactive',
                'errors': ['Invalid doctor']
            }), 404
        
        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            is_available=True
        ).all()
        
        return jsonify({
            'success': True,
            'message': 'Doctor availability retrieved successfully',
            'data': {
                'doctor': doctor.to_dict(),
                'availability': [avail.to_dict() for avail in availability]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get doctor availability',
            'errors': [str(e)]
        }), 500

@patient_bp.route('/export-history', methods=['POST'])
@jwt_required()
@patient_required
def export_patient_history():
    try:
        user_id = get_jwt_identity()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient profile not found',
                'errors': ['Profile not found']
            }), 404
        
        # Import and trigger the Celery task
        from tasks.celery_tasks import export_patient_history_csv
        task = export_patient_history_csv.delay(patient.id)
        
        return jsonify({
            'success': True,
            'message': 'CSV export started. You will be notified when ready.',
            'data': {
                'task_id': task.id
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to start CSV export',
            'errors': [str(e)]
        }), 500
