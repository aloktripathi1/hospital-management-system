from flask import Blueprint, request, jsonify, session
from database import db
from models import User, Patient, Doctor, Appointment, Treatment, DoctorAvailability
from datetime import datetime, date, time, timedelta
from decorators import patient_required

patient_bp = Blueprint('patient', __name__)

# =============================================================================
# PATIENT DASHBOARD SECTION
# =============================================================================

@patient_bp.route('/dashboard', methods=['GET'])
@patient_required
def get_dashboard():
    # Get current patient information
    current_user_id = session.get('user_id')
    current_patient = Patient.query.filter_by(user_id=current_user_id).first()
    
    # Check if patient exists
    if current_patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Count upcoming appointments for patient
    upcoming_appointment_count = Appointment.query.filter(
        Appointment.patient_id == current_patient.id,
        Appointment.appointment_date >= date.today(),
        Appointment.status == 'booked'
    ).count()
    
    # Count total appointments for patient
    total_appointment_count = Appointment.query.filter_by(patient_id=current_patient.id).count()
    
    # Count unique doctors patient has visited
    unique_doctors_count = db.session.query(Appointment.doctor_id).filter_by(
        patient_id=current_patient.id
    ).distinct().count()
    
    # Return dashboard data
    return jsonify({
        'success': True,
        'message': 'Dashboard data retrieved',
        'data': {
            'patient': current_patient.to_dict(),
            'upcoming_appointments': upcoming_appointment_count,
            'total_appointments': total_appointment_count,
            'doctors_visited': unique_doctors_count
        }
    })

# =============================================================================
# DEPARTMENTS SECTION
# =============================================================================

@patient_bp.route('/departments', methods=['GET'])
@patient_required
def get_departments():
    from models import Department
    
    # Get all active departments from database
    all_active_departments = Department.query.filter_by(is_active=True).all()
    
    # Prepare list to store department information
    departments_with_doctors = []
    
    # Loop through each department
    for single_department in all_active_departments:
        # Get all active doctors in this department
        doctors_in_this_department = Doctor.query.filter_by(
            department_id=single_department.id, 
            is_active=True
        ).all()
        
        # Prepare list to store doctor information
        doctors_info_list = []
        
        # Loop through each doctor in department
        for single_doctor in doctors_in_this_department:
            doctor_info = {
                'id': single_doctor.id,
                'name': single_doctor.name,
                'department': single_department.name
            }
            doctors_info_list.append(doctor_info)
        
        # Prepare department information with doctors
        department_info = {
            'id': single_department.id,
            'name': single_department.name,
            'description': single_department.description,
            'doctor_count': len(doctors_info_list),
            'doctors': doctors_info_list
        }
        departments_with_doctors.append(department_info)
    
    # Return departments data
    return jsonify({
        'success': True,
        'message': 'Departments retrieved successfully',
        'data': {
            'departments': departments_with_doctors
        }
    })

# =============================================================================
# APPOINTMENT SLOTS SECTION
# =============================================================================

@patient_bp.route('/available-slots', methods=['GET'])
@patient_required
def get_available_slots():
    # Get parameters from request
    requested_doctor_id = request.args.get('doctor_id')
    requested_appointment_date = request.args.get('date')
    
    # Check if doctor ID is provided
    if not requested_doctor_id:
        return jsonify({
            'success': False,
            'message': 'Doctor ID is required',
            'errors': ['Missing doctor_id']
        }), 400
    
    # Check if date is provided
    if not requested_appointment_date:
        return jsonify({
            'success': False,
            'message': 'Date is required',
            'errors': ['Missing date']
        }), 400
    
    # Convert date string to proper date format
    selected_appointment_date = datetime.strptime(requested_appointment_date, '%Y-%m-%d').date()
    
    # Find available time slots for selected doctor and date
    available_time_slots = Appointment.query.filter_by(
        doctor_id=requested_doctor_id,
        appointment_date=selected_appointment_date,
        status='available'
    ).order_by(Appointment.appointment_time.asc()).all()
    
    # Find booked time slots for selected doctor and date
    booked_time_slots = Appointment.query.filter_by(
        doctor_id=requested_doctor_id,
        appointment_date=selected_appointment_date,
        status='booked'
    ).order_by(Appointment.appointment_time.asc()).all()
    
    # Check if we need to create new time slots
    total_existing_slots = len(available_time_slots) + len(booked_time_slots)
    if total_existing_slots == 0:
        # Find doctor availability for this day of week
        selected_day_of_week = selected_appointment_date.weekday()
        doctor_availability = DoctorAvailability.query.filter_by(
            doctor_id=requested_doctor_id,
            day_of_week=selected_day_of_week,
            is_available=True
        ).first()
        
        # Set working hours for slot creation
        if doctor_availability:
            working_start_time = doctor_availability.start_time
            working_end_time = doctor_availability.end_time
        else:
            working_start_time = time(9, 0)  # Default 9 AM
            working_end_time = time(17, 0)   # Default 5 PM
        
        # Create time slots every 2 hours
        current_slot_time = working_start_time
        while current_slot_time < working_end_time:
            # Create new appointment slot
            new_appointment_slot = Appointment(
                doctor_id=requested_doctor_id,
                patient_id=None,
                appointment_date=selected_appointment_date,
                appointment_time=current_slot_time,
                status='available',
                notes=''
            )
            db.session.add(new_appointment_slot)
            
            # Calculate next slot time (2 hours later)
            current_slot_datetime = datetime.combine(selected_appointment_date, current_slot_time)
            next_slot_datetime = current_slot_datetime + timedelta(hours=2)
            current_slot_time = next_slot_datetime.time()
        
        # Save new slots to database
        db.session.commit()
        
        # Get the newly created available slots
        available_time_slots = Appointment.query.filter_by(
            doctor_id=requested_doctor_id,
            appointment_date=selected_appointment_date,
            status='available'
        ).order_by(Appointment.appointment_time.asc()).all()

    # Prepare list for all time slot information
    all_time_slots_info = []
    
    # Process available time slots
    for available_slot in available_time_slots:
        slot_start_datetime = datetime.combine(selected_appointment_date, available_slot.appointment_time)
        slot_end_datetime = slot_start_datetime + timedelta(hours=2)
        slot_end_time = slot_end_datetime.time()
        
        slot_info = {
            'id': available_slot.id,
            'time': f"{available_slot.appointment_time.strftime('%H:%M')}-{slot_end_time.strftime('%H:%M')}",
            'start_time': available_slot.appointment_time.strftime('%H:%M'),
            'end_time': slot_end_time.strftime('%H:%M'),
            'status': 'available',
            'patient_id': None
        }
        all_time_slots_info.append(slot_info)
    
    # Process booked time slots
    for booked_slot in booked_time_slots:
        slot_start_datetime = datetime.combine(selected_appointment_date, booked_slot.appointment_time)
        slot_end_datetime = slot_start_datetime + timedelta(hours=2)
        slot_end_time = slot_end_datetime.time()
        
        slot_info = {
            'id': booked_slot.id,
            'time': f"{booked_slot.appointment_time.strftime('%H:%M')}-{slot_end_time.strftime('%H:%M')}",
            'start_time': booked_slot.appointment_time.strftime('%H:%M'),
            'end_time': slot_end_time.strftime('%H:%M'),
            'status': 'booked',
            'patient_id': booked_slot.patient_id
        }
        all_time_slots_info.append(slot_info)
    
    # Return time slots information
    return jsonify({
        'success': True,
        'message': 'Available slots retrieved successfully',
        'data': {
            'slots': all_time_slots_info,
            'date': selected_appointment_date.isoformat(),
            'doctor_id': requested_doctor_id
        }
    })

@patient_bp.route('/doctors', methods=['GET'])
@patient_required
def get_doctors():
    try:
        department_name = request.args.get('department')
        
        query = Doctor.query.filter_by(is_active=True)
        
        if department_name:
            # Join with Department table to filter by department name
            from models import Department
            query = query.join(Department).filter(Department.name == department_name)
        
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

# =============================================================================
# APPOINTMENTS SECTION  
# =============================================================================

@patient_bp.route('/appointments', methods=['GET'])
@patient_required
def get_appointments():
    # Get current patient information
    current_user_id = session.get('user_id')
    current_patient = Patient.query.filter_by(user_id=current_user_id).first()
    
    # Check if patient exists
    if current_patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Get status filter from request if provided
    appointment_status_filter = request.args.get('status')
    
    # Start building query to get patient appointments
    patient_appointments_query = Appointment.query.filter_by(patient_id=current_patient.id)
    
    # Apply status filter if user provided one
    if appointment_status_filter:
        patient_appointments_query = patient_appointments_query.filter_by(status=appointment_status_filter)
    
    # Get appointments sorted by date and time (newest first)
    patient_appointments_list = patient_appointments_query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).all()
    
    # Return appointments data
    return jsonify({
        'success': True,
        'message': 'Appointments retrieved successfully',
        'data': {
            'appointments': [single_appointment.to_dict() for single_appointment in patient_appointments_list]
        }
    })

# =============================================================================
# BOOK APPOINTMENT SECTION
# =============================================================================

@patient_bp.route('/appointments', methods=['POST'])
@patient_required
def book_appointment():
    # Get current patient information
    current_user_id = session.get('user_id')
    current_patient = Patient.query.filter_by(user_id=current_user_id).first()
    
    # Check if patient exists
    if current_patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Get booking information from request
    booking_data = request.get_json()
    
    # Check if doctor ID is provided
    if not booking_data.get('doctor_id'):
        return jsonify({
            'success': False,
            'message': 'Doctor ID is required',
            'errors': ['Missing doctor_id']
        }), 400
    
    # Check if appointment date is provided
    if not booking_data.get('appointment_date'):
        return jsonify({
            'success': False,
            'message': 'Appointment date is required',
            'errors': ['Missing appointment_date']
        }), 400
    
    # Check if appointment time is provided
    if not booking_data.get('appointment_time'):
        return jsonify({
            'success': False,
            'message': 'Appointment time is required',
            'errors': ['Missing appointment_time']
        }), 400
    
    # Check if selected doctor exists and is active
    selected_doctor = Doctor.query.get(booking_data['doctor_id'])
    if selected_doctor is None or not selected_doctor.is_active:
        return jsonify({
            'success': False,
            'message': 'Doctor not found or inactive',
            'errors': ['Invalid doctor']
        }), 404
    
    # Convert date string to date format
    requested_appointment_date = datetime.strptime(booking_data['appointment_date'], '%Y-%m-%d').date()
    
    # Convert time string to time format (handle both range and simple formats)
    requested_time_string = booking_data['appointment_time']
    if '-' in requested_time_string:
        # If time is in range format like "09:00-11:00", take start time
        start_time_part = requested_time_string.split('-')[0].strip()
        requested_appointment_time = datetime.strptime(start_time_part, '%H:%M').time()
    else:
        # If time is simple format like "09:00"
        requested_appointment_time = datetime.strptime(requested_time_string, '%H:%M').time()
    
    # Find available time slot for booking
    available_time_slot = Appointment.query.filter_by(
        doctor_id=booking_data['doctor_id'],
        appointment_date=requested_appointment_date,
        appointment_time=requested_appointment_time,
        status='available'
    ).first()
    
    # Check if time slot is available
    if available_time_slot is None:
        return jsonify({
            'success': False,
            'message': 'Time slot not available',
            'errors': ['This time slot is not available for booking']
        }), 400
    
    # Check if patient already has appointment at same time
    patient_existing_appointment = Appointment.query.filter_by(
        patient_id=current_patient.id,
        appointment_date=requested_appointment_date,
        appointment_time=requested_appointment_time,
        status='booked'
    ).first()
    
    # If patient already has appointment at this time, show error
    if patient_existing_appointment:
        return jsonify({
            'success': False,
            'message': 'You already have an appointment at this time',
            'errors': ['Time slot already booked']
        }), 400
    
    # Book the appointment by updating slot information
    available_time_slot.patient_id = current_patient.id
    available_time_slot.status = 'booked'
    available_time_slot.notes = booking_data.get('notes', '')
    available_time_slot.updated_at = datetime.utcnow()
    
    # Save changes to database
    db.session.commit()
    
    # Return success response
    return jsonify({
        'success': True,
        'message': 'Appointment booked successfully',
        'data': {
            'appointment': available_time_slot.to_dict()
        }
    })

# =============================================================================
# CANCEL APPOINTMENT SECTION
# =============================================================================

@patient_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@patient_required
def cancel_appointment(appointment_id):
    # Get current patient information
    current_user_id = session.get('user_id')
    current_patient = Patient.query.filter_by(user_id=current_user_id).first()
    
    # Check if patient exists
    if current_patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Find appointment belonging to this patient
    patient_appointment = Appointment.query.filter_by(
        id=appointment_id,
        patient_id=current_patient.id
    ).first()
    
    # Check if appointment exists and belongs to patient
    if patient_appointment is None:
        return jsonify({
            'success': False,
            'message': 'Appointment not found',
            'errors': ['Appointment not found']
        }), 404
    
    # Check if appointment can be cancelled (only booked appointments)
    if patient_appointment.status != 'booked':
        return jsonify({
            'success': False,
            'message': 'Cannot cancel this appointment',
            'errors': ['Invalid status']
        }), 400
    
    # Cancel the appointment
    patient_appointment.status = 'cancelled'
    patient_appointment.updated_at = datetime.utcnow()
    
    # Save changes to database
    db.session.commit()
    
    # Return success response
    return jsonify({
        'success': True,
        'message': 'Appointment cancelled successfully',
        'data': {}
    })

# =============================================================================
# PATIENT HISTORY SECTION
# =============================================================================

@patient_bp.route('/history', methods=['GET'])
@patient_required
def get_history():
    # Get current patient information
    current_user_id = session.get('user_id')
    current_patient = Patient.query.filter_by(user_id=current_user_id).first()
    
    # Check if patient exists
    if current_patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Get all treatments for this patient (joined with appointments)
    patient_treatment_history = db.session.query(Treatment).join(Appointment).filter(
        Appointment.patient_id == current_patient.id
    ).order_by(Treatment.created_at.desc()).all()
    
    # Return treatment history
    return jsonify({
        'success': True,
        'message': 'Patient history retrieved successfully',
        'data': {
            'treatments': [single_treatment.to_dict() for single_treatment in patient_treatment_history]
        }
    })

# =============================================================================
# DOCTOR AVAILABILITY SECTION
# =============================================================================

@patient_bp.route('/doctor/availability/<int:doctor_id>', methods=['GET'])
@patient_required
def get_doctor_availability(doctor_id):
    # Find doctor by ID
    selected_doctor = Doctor.query.get(doctor_id)
    
    # Check if doctor exists and is active
    if selected_doctor is None or not selected_doctor.is_active:
        return jsonify({
            'success': False,
            'message': 'Doctor not found or inactive',
            'errors': ['Invalid doctor']
        }), 404
    
    # Get doctor availability schedule
    doctor_availability_schedule = DoctorAvailability.query.filter_by(
        doctor_id=doctor_id,
        is_available=True
    ).all()
    
    # Return doctor and availability information
    return jsonify({
        'success': True,
        'message': 'Doctor availability retrieved successfully',
        'data': {
            'doctor': selected_doctor.to_dict(),
            'availability': [single_availability.to_dict() for single_availability in doctor_availability_schedule]
        }
    })

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
