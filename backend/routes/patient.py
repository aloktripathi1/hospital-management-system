from flask import Blueprint, request, jsonify, session
from database import db
from models import User, Patient, Doctor, Appointment, Treatment, DoctorAvailability
from datetime import datetime, date, time, timedelta
from decorators import patient_required

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/dashboard', methods=['GET'])
@patient_required
def get_dashboard():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    if patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Count upcoming appointments
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date >= date.today(),
        Appointment.status == 'booked'
    ).count()
    
    # Count total appointments
    total_appointments = Appointment.query.filter_by(patient_id=patient.id).count()
    
    # Count unique doctors visited
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

@patient_bp.route('/departments', methods=['GET'])
@patient_required
def get_departments():
    from models import Department
    
    # Get all active departments
    departments = Department.query.filter_by(is_active=True).all()
    
    department_list = []
    for department in departments:
        # Get doctors in this department
        doctors_in_department = Doctor.query.filter_by(
            department_id=department.id, 
            is_active=True
        ).all()
        
        doctors_list = []
        for doctor in doctors_in_department:
            doctors_list.append({
                'id': doctor.id,
                'name': doctor.name,
                'specialization': doctor.specialization
            })
        
        department_list.append({
            'id': department.id,
            'name': department.name,
            'description': department.description,
            'doctor_count': len(doctors_list),
            'doctors': doctors_list
        })
    
    return jsonify({
        'success': True,
        'message': 'Departments retrieved successfully',
        'data': {
            'departments': department_list
        }
    })

@patient_bp.route('/available-slots', methods=['GET'])
@patient_required
def get_available_slots():
    doctor_id = request.args.get('doctor_id')
    appointment_date = request.args.get('date')
    
    # Check if both parameters are provided
    if not doctor_id:
        return jsonify({
            'success': False,
            'message': 'Doctor ID is required',
            'errors': ['Missing doctor_id']
        }), 400
    
    if not appointment_date:
        return jsonify({
            'success': False,
            'message': 'Date is required',
            'errors': ['Missing date']
        }), 400
    
    # Convert date string to date object
    appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
    
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
    
    # If no slots exist, create some simple 2-hour slots
    if len(available_slots) == 0 and len(booked_slots) == 0:
        # Get doctor availability for this day
        day_of_week = appointment_date.weekday()
        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=day_of_week,
            is_available=True
        ).first()
        
        # Set default time slots
        if availability:
            start_time = availability.start_time
            end_time = availability.end_time
        else:
            start_time = time(9, 0)  # 9 AM
            end_time = time(17, 0)   # 5 PM
        
        # Create slots every 2 hours
        current_time = start_time
        while current_time < end_time:
            new_slot = Appointment(
                doctor_id=doctor_id,
                patient_id=None,
                appointment_date=appointment_date,
                appointment_time=current_time,
                status='available',
                notes=''
            )
            db.session.add(new_slot)
            
            # Move to next 2-hour slot
            current_datetime = datetime.combine(appointment_date, current_time)
            next_datetime = current_datetime + timedelta(hours=2)
            current_time = next_datetime.time()
        
        db.session.commit()
        
        # Get the newly created slots
        available_slots = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            status='available'
        ).order_by(Appointment.appointment_time.asc()).all()

    slots_data = []
    
    # Add available slots
    for slot in available_slots:
        start_datetime = datetime.combine(appointment_date, slot.appointment_time)
        end_datetime = start_datetime + timedelta(hours=2)
        end_time = end_datetime.time()
        
        slots_data.append({
            'id': slot.id,
            'time': f"{slot.appointment_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
            'start_time': slot.appointment_time.strftime('%H:%M'),
            'end_time': end_time.strftime('%H:%M'),
            'status': 'available',
            'patient_id': None
        })
    
    # Add booked slots
    for slot in booked_slots:
        start_datetime = datetime.combine(appointment_date, slot.appointment_time)
        end_datetime = start_datetime + timedelta(hours=2)
        end_time = end_datetime.time()
        
        slots_data.append({
            'id': slot.id,
            'time': f"{slot.appointment_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
            'start_time': slot.appointment_time.strftime('%H:%M'),
            'end_time': end_time.strftime('%H:%M'),
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

@patient_bp.route('/doctors', methods=['GET'])
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
@patient_required
def get_appointments():
    try:
        user_id = session.get('user_id')
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
@patient_required
def book_appointment():
    try:
        user_id = session.get('user_id')
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
            
            # Handle time range format (e.g., "09:00-11:00") or simple time format (e.g., "09:00")
            time_str = data['appointment_time']
            if '-' in time_str:
                # Extract start time from time range
                start_time_str = time_str.split('-')[0].strip()
                appointment_time = datetime.strptime(start_time_str, '%H:%M').time()
            else:
                # Simple time format
                appointment_time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': 'Invalid date or time format',
                'errors': [f'Invalid format: {str(e)}']
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
@patient_required
def cancel_appointment(appointment_id):
    try:
        user_id = session.get('user_id')
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
@patient_required
def get_history():
    try:
        user_id = session.get('user_id')
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
@patient_required
def export_patient_history():
    try:
        user_id = session.get('user_id')
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
