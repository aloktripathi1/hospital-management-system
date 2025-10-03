from flask import Blueprint, request, jsonify, session
from database import db
from models import User, Doctor, Patient, Appointment, Treatment, DoctorAvailability
from datetime import datetime, date, time, timedelta
from decorators import doctor_required

doctor_bp = Blueprint('doctor', __name__)

# =================== DOCTOR DASHBOARD SECTION ===================

@doctor_bp.route('/dashboard', methods=['GET'])
@doctor_required
def get_dashboard():
    # Get the current user ID from session
    current_user_id = session.get('user_id')
    
    # Find the doctor profile for this user
    current_doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    
    # Check if doctor profile exists
    if current_doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Count today's appointments for this doctor
    today_appointments_count = Appointment.query.filter_by(
        doctor_id=current_doctor.id,
        appointment_date=date.today()
    ).count()
    
    # Count upcoming appointments (today and future dates with booked status)
    upcoming_appointments_count = Appointment.query.filter(
        Appointment.doctor_id == current_doctor.id,
        Appointment.appointment_date >= date.today(),
        Appointment.status == 'booked'
    ).count()
    
    # Count total unique patients this doctor has treated
    total_patients_count = db.session.query(Appointment.patient_id).filter_by(
        doctor_id=current_doctor.id
    ).distinct().count()
    
    # Get doctor information
    doctor_info = current_doctor.to_dict()
    
    return jsonify({
        'success': True,
        'message': 'Dashboard data retrieved',
        'data': {
            'doctor': doctor_info,
            'today_appointments': today_appointments_count,
            'upcoming_appointments': upcoming_appointments_count,
            'total_patients': total_patients_count
        }
    })

# =================== PATIENT HISTORY SECTION ===================

@doctor_bp.route('/patient-history/<int:patient_id>', methods=['GET'])
@doctor_required
def get_patient_history_details(patient_id):
    # Get the current doctor's user ID from session
    current_doctor_user_id = session.get('user_id')
    
    # Find the doctor profile using user ID
    current_doctor = Doctor.query.get(current_doctor_user_id)
    
    # Check if doctor exists
    if current_doctor is None:
        return jsonify({"error": "Doctor not found"}), 404
    
    # Find the patient by ID
    selected_patient = Patient.query.get(patient_id)
    
    # Check if patient exists
    if selected_patient is None:
        return jsonify({"error": "Patient not found"}), 404
    
    # Get all appointments between this patient and doctor (newest first)
    patient_appointments_list = Appointment.query.filter_by(
        patient_id=patient_id,
        doctor_id=current_doctor.id
    ).order_by(Appointment.appointment_date.desc()).all()
    
    # Build appointment history with treatment details
    appointment_history_list = []
    for single_appointment in patient_appointments_list:
        # Format appointment date and time
        formatted_date = single_appointment.appointment_date.strftime('%Y-%m-%d')
        formatted_time = single_appointment.appointment_time.strftime('%H:%M')
        
        # Get treatment information if available
        treatment_info = None
        if single_appointment.treatment:
            treatment_info = {
                'id': single_appointment.treatment.id,
                'diagnosis': single_appointment.treatment.diagnosis,
                'prescription': single_appointment.treatment.prescription,
                'notes': single_appointment.treatment.notes
            }
        
        # Build appointment record
        appointment_record = {
            'id': single_appointment.id,
            'appointment_date': formatted_date,
            'appointment_time': formatted_time,
            'status': single_appointment.status,
            'treatment': treatment_info
        }
        appointment_history_list.append(appointment_record)
    
    # Build complete patient data with history
    patient_complete_data = {
        'id': selected_patient.id,
        'name': selected_patient.name,
        'email': selected_patient.email,
        'phone': selected_patient.phone,
        'address': selected_patient.address,
        'date_of_birth': selected_patient.date_of_birth.strftime('%Y-%m-%d') if selected_patient.date_of_birth else None,
        'gender': selected_patient.gender,
        'medical_history': selected_patient.medical_history,
        'appointments': appointment_history_list
    }
    
    return jsonify(patient_complete_data)

# =================== APPOINTMENTS MANAGEMENT SECTION ===================

@doctor_bp.route('/appointments', methods=['GET'])
@doctor_required
def get_appointments():
    # Get the current doctor's user ID from session
    current_user_id = session.get('user_id')
    
    # Find the doctor profile for this user
    current_doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    
    # Check if doctor profile exists
    if current_doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Get filter parameters from request
    date_filter_value = request.args.get('date')
    status_filter_value = request.args.get('status')
    time_filter_value = request.args.get('time_filter')  # 'today', 'upcoming', 'completed'
    
    # Start with appointments for this doctor
    appointments_query = Appointment.query.filter_by(doctor_id=current_doctor.id)
    
    # Apply time-based filters
    if time_filter_value == 'today':
        appointments_query = appointments_query.filter_by(appointment_date=date.today())
    elif time_filter_value == 'upcoming':
        appointments_query = appointments_query.filter(Appointment.appointment_date >= date.today())
        appointments_query = appointments_query.filter(Appointment.status.in_(['booked', 'available']))
    elif time_filter_value == 'completed':
        appointments_query = appointments_query.filter(Appointment.status == 'completed')
    else:
        # Default: show today's and upcoming appointments
        appointments_query = appointments_query.filter(Appointment.appointment_date >= date.today())
    
    # Apply date filter if provided
    if date_filter_value:
        # Convert date string to date object
        filter_date_object = datetime.strptime(date_filter_value, '%Y-%m-%d').date()
        appointments_query = appointments_query.filter_by(appointment_date=filter_date_object)
    
    # Apply status filter if provided
    if status_filter_value:
        appointments_query = appointments_query.filter_by(status=status_filter_value)
    
    # Get final appointments list ordered by date and time
    final_appointments_list = appointments_query.order_by(
        Appointment.appointment_date.asc(),
        Appointment.appointment_time.asc()
    ).all()
    
    # Convert appointments to dictionary format
    appointments_data_list = []
    for single_appointment in final_appointments_list:
        appointment_info = single_appointment.to_dict()
        appointments_data_list.append(appointment_info)
    
    return jsonify({
        'success': True,
        'message': 'Appointments retrieved successfully',
        'data': {
            'appointments': appointments_data_list
        }
    })

# =================== PATIENTS MANAGEMENT SECTION ===================

@doctor_bp.route('/patients', methods=['GET'])
@doctor_required
def get_patients():
    # Get the current doctor's user ID from session
    current_user_id = session.get('user_id')
    
    # Find the doctor profile for this user
    current_doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    
    # Check if doctor profile exists
    if current_doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Get unique patients who have appointments with this doctor
    doctor_patients_list = db.session.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == current_doctor.id
    ).distinct().all()
    
    # Convert patients to dictionary format
    patients_data_list = []
    for single_patient in doctor_patients_list:
        patient_info = single_patient.to_dict()
        patients_data_list.append(patient_info)
    
    return jsonify({
        'success': True,
        'message': 'Patients retrieved successfully',
        'data': {
            'patients': patients_data_list
        }
    })

@doctor_bp.route('/appointments/<int:appointment_id>/status', methods=['PUT'])
@doctor_required
def update_appointment_status(appointment_id):
    # Get the current doctor's user ID from session
    current_user_id = session.get('user_id')
    
    # Find the doctor profile for this user
    current_doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    
    # Check if doctor profile exists
    if current_doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Find the appointment that belongs to this doctor
    selected_appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=current_doctor.id).first()
    
    # Check if appointment exists and belongs to this doctor
    if selected_appointment is None:
        return jsonify({
            'success': False,
            'message': 'Appointment not found',
            'errors': ['Appointment not found']
        }), 404
    
    # Get the status update data
    status_update_data = request.get_json()
    new_status_value = status_update_data.get('status')
    
    # Validate the new status
    valid_status_list = ['completed', 'cancelled', 'booked']
    if new_status_value not in valid_status_list:
        return jsonify({
            'success': False,
            'message': 'Invalid status',
            'errors': ['Status must be completed, cancelled, or booked']
        }), 400
    
    # Update the appointment status
    selected_appointment.status = new_status_value
    selected_appointment.updated_at = datetime.utcnow()
    
    # Update notes if provided
    if 'notes' in status_update_data:
        selected_appointment.notes = status_update_data['notes']
    
    # Save the changes
    db.session.commit()
    
    # Return success response
    updated_appointment_info = selected_appointment.to_dict()
    return jsonify({
        'success': True,
        'message': f'Appointment marked as {new_status_value}',
        'data': {
            'appointment': updated_appointment_info
        }
    })

# =================== TREATMENT RECORDS SECTION ===================

@doctor_bp.route('/patient-history', methods=['POST'])
@doctor_required
def add_patient_history():
    # Get the current doctor's user ID from session
    current_user_id = session.get('user_id')
    
    # Find the doctor profile for this user
    current_doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    
    # Check if doctor profile exists
    if current_doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Get the treatment data
    treatment_data = request.get_json()
    appointment_id_value = treatment_data.get('appointment_id')
    
    # Check if appointment ID is provided
    if not appointment_id_value:
        return jsonify({
            'success': False,
            'message': 'Appointment ID is required',
            'errors': ['Missing appointment_id']
        }), 400
    
    # Find the appointment that belongs to this doctor
    selected_appointment = Appointment.query.filter_by(
        id=appointment_id_value,
        doctor_id=current_doctor.id
    ).first()
    
    # Check if appointment exists and belongs to this doctor
    if selected_appointment is None:
        return jsonify({
            'success': False,
            'message': 'Appointment not found',
            'errors': ['Appointment not found']
        }), 404
    
    # Create new treatment record
    new_treatment_record = Treatment(
        appointment_id=appointment_id_value,
        diagnosis=treatment_data.get('diagnosis', ''),
        prescription=treatment_data.get('prescription', ''),
        visit_type=treatment_data.get('visit_type', 'consultation'),
        symptoms=treatment_data.get('symptoms', ''),
        treatment_notes=treatment_data.get('treatment_notes', '')
    )
    
    # Add treatment to database
    db.session.add(new_treatment_record)
    
    # Update appointment to completed status
    selected_appointment.status = 'completed'
    selected_appointment.notes = treatment_data.get('notes', '')
    selected_appointment.updated_at = datetime.utcnow()
    
    # Save all changes
    db.session.commit()
    
    # Return success response with treatment and appointment data
    treatment_info = new_treatment_record.to_dict()
    appointment_info = selected_appointment.to_dict()
    
    return jsonify({
        'success': True,
        'message': 'Patient history updated successfully',
        'data': {
            'treatment': treatment_info,
            'appointment': appointment_info
        }
    })



# =================== AVAILABILITY MANAGEMENT SECTION ===================

@doctor_bp.route('/availability', methods=['GET'])
@doctor_required
def get_availability():
    # Get the current doctor's user ID from session
    current_user_id = session.get('user_id')
    
    # Find the doctor profile for this user
    current_doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    
    # Check if doctor profile exists
    if current_doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Get all availability records for this doctor
    doctor_availability_list = DoctorAvailability.query.filter_by(doctor_id=current_doctor.id).all()
    
    # Convert availability to dictionary format
    availability_data_list = []
    for single_availability in doctor_availability_list:
        availability_info = single_availability.to_dict()
        availability_data_list.append(availability_info)
    
    return jsonify({
        'success': True,
        'message': 'Availability retrieved successfully',
        'data': {
            'availability': availability_data_list
        }
    })

@doctor_bp.route('/availability', methods=['PUT'])
@doctor_required
def update_availability():
    # Get the current doctor's user ID from session
    current_user_id = session.get('user_id')
    
    # Find the doctor profile for this user
    current_doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    
    # Check if doctor profile exists
    if current_doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Get the availability update data
    availability_update_data = request.get_json()
    new_availability_list = availability_update_data.get('availability', [])
    
    # Remove all existing availability for this doctor
    DoctorAvailability.query.filter_by(doctor_id=current_doctor.id).delete()
    
    # Add each new availability record
    for single_availability in new_availability_list:
        # Convert time strings to time objects
        start_time_object = datetime.strptime(single_availability['start_time'], '%H:%M').time()
        end_time_object = datetime.strptime(single_availability['end_time'], '%H:%M').time()
        
        # Create new availability record
        new_availability_record = DoctorAvailability(
            doctor_id=current_doctor.id,
            day_of_week=single_availability['day_of_week'],
            start_time=start_time_object,
            end_time=end_time_object,
            is_available=single_availability.get('is_available', True)
        )
        db.session.add(new_availability_record)
    
    # Save all changes
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Availability updated successfully',
        'data': {}
    })

# =================== APPOINTMENT SLOTS CREATION SECTION ===================

@doctor_bp.route('/set-slots', methods=['POST'])
@doctor_required
def set_availability_slots():
    # Get the current doctor's user ID from session
    current_user_id = session.get('user_id')
    
    # Find the doctor profile for this user
    current_doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    
    # Check if doctor profile exists
    if current_doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Get the slots creation data
    slots_data = request.get_json()
    
    # Convert date strings to date objects
    start_date_object = datetime.strptime(slots_data.get('start_date'), '%Y-%m-%d').date()
    end_date_object = datetime.strptime(slots_data.get('end_date'), '%Y-%m-%d').date()
    
    # Convert time strings to time objects (with defaults)
    daily_start_time = datetime.strptime(slots_data.get('start_time', '09:00'), '%H:%M').time()
    daily_end_time = datetime.strptime(slots_data.get('end_time', '17:00'), '%H:%M').time()
    
    # Initialize slots counter
    total_slots_created = 0
    
    # Get optional break periods
    break_periods_list = slots_data.get('break_periods', []) or []
    
    # Remove existing available slots in this date range to avoid duplicates
    Appointment.query.filter(
        Appointment.doctor_id == current_doctor.id,
        Appointment.appointment_date >= start_date_object,
        Appointment.appointment_date <= end_date_object,
        Appointment.status == 'available'
    ).delete(synchronize_session=False)
    
    # Generate slots for each day in the date range
    current_processing_date = start_date_object
    while current_processing_date <= end_date_object:
        # Use the provided daily time window
        day_start_time = daily_start_time
        day_end_time = daily_end_time
        
        # Process break periods for this day
        daily_breaks_list = []
        for single_break in break_periods_list:
            # Convert break time strings to time objects
            break_start_time = datetime.strptime(single_break.get('start_time', '00:00'), '%H:%M').time()
            break_end_time = datetime.strptime(single_break.get('end_time', '00:00'), '%H:%M').time()
            
            # Only add valid breaks (start before end)
            if break_start_time < break_end_time:
                daily_breaks_list.append((break_start_time, break_end_time))
        
        # Function to check if a time falls within any break period
        def time_is_in_break_period(check_time):
            for break_start, break_end in daily_breaks_list:
                if break_start <= check_time < break_end:
                    return True
            return False
        
        # Create 2-hour appointment slots for this day
        current_slot_time = day_start_time
        while current_slot_time < day_end_time:
            # Only create slot if time is not in break period
            if not time_is_in_break_period(current_slot_time):
                # Create new appointment slot
                new_appointment_slot = Appointment(
                    doctor_id=current_doctor.id,
                    patient_id=None,
                    appointment_date=current_processing_date,
                    appointment_time=current_slot_time,
                    status='available',
                    notes=''
                )
                db.session.add(new_appointment_slot)
                total_slots_created += 1
            
            # Move to next 2-hour slot
            next_slot_datetime = datetime.combine(current_processing_date, current_slot_time) + timedelta(hours=2)
            current_slot_time = next_slot_datetime.time()
        
        # Move to next day
        current_processing_date += timedelta(days=1)
    
    # Save all created slots
    db.session.commit()
    
    # Create date range string for response
    date_range_string = f'{start_date_object} to {end_date_object}'
    
    return jsonify({
        'success': True,
        'message': f'Created {total_slots_created} appointment slots',
        'data': {
            'slots_created': total_slots_created,
            'date_range': date_range_string
        }
    })
