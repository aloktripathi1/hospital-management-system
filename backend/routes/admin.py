from flask import Blueprint, request, jsonify
from database import db
from models import User, Patient, Doctor, Appointment, Treatment, Department
from werkzeug.security import generate_password_hash
from datetime import datetime, date
from sqlalchemy import or_
from decorators import admin_required

admin_bp = Blueprint('admin', __name__)

# =============================================================================
# ADMIN DASHBOARD SECTION
# =============================================================================

@admin_bp.route('/dashboard-stats', methods=['GET'])
@admin_required
def dashboard_stats():
    # Count total doctors in system
    total_doctors_count = Doctor.query.count()
    
    # Count active doctors only
    active_doctors_count = Doctor.query.filter_by(is_active=True).count()
    
    # Count total patients in system  
    total_patients_count = Patient.query.count()
    
    # Count appointments for today
    todays_date = date.today()
    today_appointments_count = Appointment.query.filter_by(appointment_date=todays_date).count()
    
    # Return dashboard statistics
    return jsonify({
        'success': True,
        'message': 'Dashboard stats retrieved',
        'data': {
            'total_doctors': total_doctors_count,
            'active_doctors': active_doctors_count,
            'total_patients': total_patients_count,
            'today_appointments': today_appointments_count
        }
    })

# =============================================================================
# DOCTORS MANAGEMENT SECTION
# =============================================================================

@admin_bp.route('/doctors', methods=['GET'])
@admin_required
def get_doctors():
    # Get all doctors from database
    all_doctors_list = Doctor.query.all()
    
    # Prepare list to store doctor information
    doctors_data_list = []
    
    # Convert each doctor to dictionary format
    for single_doctor in all_doctors_list:
        doctor_info = single_doctor.to_dict()
        doctors_data_list.append(doctor_info)
    
    # Return doctors data
    return jsonify({
        'success': True,
        'message': 'Doctors retrieved successfully',
        'data': {
            'doctors': doctors_data_list
        }
    })


@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@admin_required
def update_doctor(doctor_id):
    # Find doctor by ID
    selected_doctor = Doctor.query.get(doctor_id)
    
    # Check if doctor exists
    if selected_doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor not found',
            'errors': ['Doctor not found']
        }), 404
    
    # Get update data from request
    update_data = request.get_json()
    
    # Update doctor name if provided
    if 'name' in update_data:
        selected_doctor.name = update_data['name']
    
    # Update doctor specialization if provided
    if 'specialization' in update_data:
        selected_doctor.specialization = update_data['specialization']
    
    # Update doctor experience if provided
    if 'experience' in update_data:
        selected_doctor.experience = update_data['experience']
    
    # Update doctor qualification if provided
    if 'qualification' in update_data:
        selected_doctor.qualification = update_data['qualification']
    
    # Update doctor phone if provided
    if 'phone' in update_data:
        selected_doctor.phone = update_data['phone']
    
    # Update consultation fee if provided
    if 'consultation_fee' in update_data:
        selected_doctor.consultation_fee = update_data['consultation_fee']
    
    # Update active status if provided
    if 'is_active' in update_data:
        selected_doctor.is_active = update_data['is_active']
        selected_doctor.user.is_active = update_data['is_active']
    
    # Save changes to database
    db.session.commit()
    
    # Return success response
    return jsonify({
        'success': True,
        'message': 'Doctor updated successfully',
        'data': {
            'doctor': selected_doctor.to_dict()
        }
    })

@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@admin_required
def delete_doctor(doctor_id):
    # Find the doctor by ID
    selected_doctor = Doctor.query.get(doctor_id)
    
    # Check if doctor exists
    if selected_doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor not found',
            'errors': ['Doctor not found']
        }), 404
    
    # Deactivate doctor and their user account (soft delete)
    selected_doctor.is_active = False
    selected_doctor.user.is_active = False
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Doctor deactivated successfully',
        'data': {}
    })

# =================== PATIENTS MANAGEMENT SECTION ===================

@admin_bp.route('/patients', methods=['GET'])
@admin_required
def get_patients():
    # Get all patients from database
    all_patients_list = Patient.query.all()
    
    # Convert patients to dictionary format
    patients_data_list = []
    for single_patient in all_patients_list:
        patient_info = single_patient.to_dict()
        patients_data_list.append(patient_info)
    
    return jsonify({
        'success': True,
        'message': 'Patients retrieved successfully',
        'data': {
            'patients': patients_data_list
        }
    })

@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@admin_required
def update_patient(patient_id):
    # Find the patient by ID
    selected_patient = Patient.query.get(patient_id)
    
    # Check if patient exists
    if selected_patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient not found',
            'errors': ['Patient not found']
        }), 404
    
    # Get the update data
    update_data = request.get_json()
    
    # Update patient fields one by one
    if 'name' in update_data:
        selected_patient.name = update_data['name']
    if 'phone' in update_data:
        selected_patient.phone = update_data['phone']
    if 'address' in update_data:
        selected_patient.address = update_data['address']
    if 'age' in update_data:
        selected_patient.age = update_data['age']
    if 'gender' in update_data:
        selected_patient.gender = update_data['gender']
    if 'medical_history' in update_data:
        selected_patient.medical_history = update_data['medical_history']
    if 'emergency_contact' in update_data:
        selected_patient.emergency_contact = update_data['emergency_contact']
    if 'is_active' in update_data:
        selected_patient.user.is_active = update_data['is_active']
    
    # Save the changes
    db.session.commit()
    
    # Return success response with updated patient data
    updated_patient_info = selected_patient.to_dict()
    return jsonify({
        'success': True,
        'message': 'Patient updated successfully',
        'data': {
            'patient': updated_patient_info
        }
    })

# =================== APPOINTMENTS MANAGEMENT SECTION ===================

@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def get_appointments():
    # Get all appointments ordered by date (newest first)
    all_appointments_list = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    
    # Convert appointments to dictionary format
    appointments_data_list = []
    for single_appointment in all_appointments_list:
        appointment_info = single_appointment.to_dict()
        appointments_data_list.append(appointment_info)
    
    return jsonify({
        'success': True,
        'message': 'Appointments retrieved successfully',
        'data': {
            'appointments': appointments_data_list
        }
    })

@admin_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@admin_required
def update_appointment(appointment_id):
    # Find the appointment by ID
    selected_appointment = Appointment.query.get(appointment_id)
    
    # Check if appointment exists
    if selected_appointment is None:
        return jsonify({
            'success': False,
            'message': 'Appointment not found',
            'errors': ['Appointment not found']
        }), 404
    
    # Get the update data
    update_data = request.get_json()
    
    # Update appointment fields one by one
    if 'status' in update_data:
        selected_appointment.status = update_data['status']
    if 'notes' in update_data:
        selected_appointment.notes = update_data['notes']
    
    # Update the modification time
    selected_appointment.updated_at = datetime.utcnow()
    
    # Save the changes
    db.session.commit()
    
    # Return success response with updated appointment data
    updated_appointment_info = selected_appointment.to_dict()
    return jsonify({
        'success': True,
        'message': 'Appointment updated successfully',
        'data': {
            'appointment': updated_appointment_info
        }
    })

# =================== SEARCH FUNCTIONALITY SECTION ===================

@admin_bp.route('/search', methods=['GET'])
@admin_required
def search():
    # Get search parameters
    search_type = request.args.get('type')
    search_query = request.args.get('query', '')
    
    # Check if required parameters are provided
    if not search_type or not search_query:
        return jsonify({
            'success': False,
            'message': 'Search type and query are required',
            'errors': ['Missing parameters']
        }), 400
    
    # Initialize empty results list
    search_results = []
    
    # Search based on type
    if search_type == 'doctor':
        matching_doctors = Doctor.query.filter(
            Doctor.name.contains(search_query) | 
            Doctor.specialization.contains(search_query)
        ).all()
        for single_doctor in matching_doctors:
            doctor_info = single_doctor.to_dict()
            search_results.append(doctor_info)
    
    elif search_type == 'patient':
        matching_patients = Patient.query.filter(
            Patient.name.contains(search_query) |
            Patient.phone.contains(search_query)
        ).all()
        for single_patient in matching_patients:
            patient_info = single_patient.to_dict()
            search_results.append(patient_info)
    
    elif search_type == 'appointment':
        matching_appointments = Appointment.query.join(Patient).join(Doctor).filter(
            Patient.name.contains(search_query) |
            Doctor.name.contains(search_query)
        ).all()
        for single_appointment in matching_appointments:
            appointment_info = single_appointment.to_dict()
            search_results.append(appointment_info)
    
    # Calculate total results count
    total_results_count = len(search_results)
    
    return jsonify({
        'success': True,
        'message': 'Search completed successfully',
        'data': {
            'results': search_results,
            'count': total_results_count
        }
    })

@admin_bp.route('/search/doctors', methods=['GET'])
@admin_required
def search_doctors():
    # Get search parameters
    general_query = request.args.get('q', '')
    specialization_query = request.args.get('specialization', '')
    
    # Check if at least one search parameter is provided
    if not general_query and not specialization_query:
        return jsonify({
            'success': False,
            'message': 'Search query or specialization is required',
            'errors': ['Missing search parameters']
        }), 400
    
    # Start building the search query
    doctors_search_query = Doctor.query
    
    # Add general name or specialization search
    if general_query:
        doctors_search_query = doctors_search_query.filter(
            or_(
                Doctor.name.ilike(f'%{general_query}%'),
                Doctor.specialization.ilike(f'%{general_query}%')
            )
        )
    
    # Add specific specialization filter
    if specialization_query:
        doctors_search_query = doctors_search_query.filter(
            Doctor.specialization.ilike(f'%{specialization_query}%')
        )
    
    # Execute the search
    matching_doctors_list = doctors_search_query.all()
    
    # Convert to dictionary format
    doctors_data_list = []
    for single_doctor in matching_doctors_list:
        doctor_info = single_doctor.to_dict()
        doctors_data_list.append(doctor_info)
    
    # Calculate total count
    total_doctors_found = len(doctors_data_list)
    
    return jsonify({
        'success': True,
        'message': 'Doctors found',
        'data': {
            'doctors': doctors_data_list,
            'count': total_doctors_found
        }
    })

@admin_bp.route('/search/patients', methods=['GET'])
@admin_required
def search_patients():
    # Get the search query
    patient_search_query = request.args.get('q', '')
    
    # Check if search query is provided
    if not patient_search_query:
        return jsonify({
            'success': False,
            'message': 'Search query is required',
            'errors': ['Missing search parameter']
        }), 400
    
    # Search patients by name or email
    matching_patients_list = db.session.query(Patient).join(User).filter(
        or_(
            Patient.name.ilike(f'%{patient_search_query}%'),
            User.email.ilike(f'%{patient_search_query}%')
        )
    ).all()
    
    # Convert to dictionary format
    patients_data_list = []
    for single_patient in matching_patients_list:
        patient_info = single_patient.to_dict()
        patients_data_list.append(patient_info)
    
    # Calculate total count
    total_patients_found = len(patients_data_list)
    
    return jsonify({
        'success': True,
        'message': 'Patients found',
        'data': {
            'patients': patients_data_list,
            'count': total_patients_found
        }
    })


@admin_bp.route('/doctors', methods=['POST'])
@admin_required
def add_doctor():
    # Get the new doctor data
    new_doctor_data = request.get_json()
    
    # Check all required fields
    required_fields_list = ['name', 'email', 'specialization', 'phone', 'experience', 'qualification']
    for field in required_fields_list:
        if not new_doctor_data.get(field):
            field_name = field.replace("_", " ").title()
            return jsonify({
                'success': False,
                'message': f'{field_name} is required',
                'errors': [f'Missing {field}']
            }), 400
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=new_doctor_data['email']).first()
    if existing_user is not None:
        return jsonify({
            'success': False,
            'message': 'Email already exists',
            'errors': ['Email taken']
        }), 400
    
    # Generate username from email (part before @)
    base_username = new_doctor_data['email'].split('@')[0]
    
    # Make sure username is unique
    final_username = base_username
    username_counter = 1
    while User.query.filter_by(username=final_username).first():
        final_username = f"{base_username}{username_counter}"
        username_counter += 1
    
    # Generate simple temporary password: firstname + 123
    name_parts_list = new_doctor_data['name'].split()
    # Skip titles like Dr., Mr., Ms., etc.
    if name_parts_list[0].lower() in ['dr.', 'dr', 'mr.', 'mr', 'ms.', 'ms', 'mrs.', 'mrs']:
        first_name = name_parts_list[1].lower()
    else:
        first_name = name_parts_list[0].lower()
    
    temporary_password = f"{first_name}123"
    
    # Create user account
    new_user = User(
        username=final_username,
        email=new_doctor_data['email'],
        password_hash=generate_password_hash(temporary_password),
        role='doctor'
    )
    db.session.add(new_user)
    db.session.flush()
    
    # Create doctor profile
    new_doctor = Doctor(
        user_id=new_user.id,
        name=new_doctor_data['name'],
        specialization=new_doctor_data['specialization'],
        phone=new_doctor_data['phone'],
        experience=new_doctor_data['experience'],
        qualification=new_doctor_data['qualification'],
        is_active=True
    )
    db.session.add(new_doctor)
    db.session.commit()
    
    # Return success with doctor info and credentials
    new_doctor_info = new_doctor.to_dict()
    return jsonify({
        'success': True,
        'message': 'Doctor account created successfully',
        'data': {
            'doctor': new_doctor_info,
            'credentials': {
                'username': final_username,
                'password': temporary_password
            }
        }
    })

@admin_bp.route('/patients', methods=['POST'])
@admin_required
def add_patient():
    # Get the new patient data
    new_patient_data = request.get_json()
    
    # Check all required fields
    required_fields_list = ['name', 'email', 'phone', 'age']
    for field in required_fields_list:
        if not new_patient_data.get(field):
            field_name = field.replace("_", " ").title()
            return jsonify({
                'success': False,
                'message': f'{field_name} is required',
                'errors': [f'Missing {field}']
            }), 400
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=new_patient_data['email']).first()
    if existing_user is not None:
        return jsonify({
            'success': False,
            'message': 'Email already exists',
            'errors': ['Email taken']
        }), 400
    
    # Generate username from email (part before @)
    base_username = new_patient_data['email'].split('@')[0]
    
    # Make sure username is unique
    final_username = base_username
    username_counter = 1
    while User.query.filter_by(username=final_username).first():
        final_username = f"{base_username}{username_counter}"
        username_counter += 1
    
    # Generate simple temporary password: firstname + 123
    name_parts_list = new_patient_data['name'].split()
    # Skip titles like Dr., Mr., Ms., etc.
    if name_parts_list[0].lower() in ['dr.', 'dr', 'mr.', 'mr', 'ms.', 'ms', 'mrs.', 'mrs']:
        first_name = name_parts_list[1].lower()
    else:
        first_name = name_parts_list[0].lower()
    
    temporary_password = f"{first_name}123"
    
    # Create user account
    new_user = User(
        username=final_username,
        email=new_patient_data['email'],
        password_hash=generate_password_hash(temporary_password),
        role='patient'
    )
    db.session.add(new_user)
    db.session.flush()
    
    # Create patient profile
    new_patient = Patient(
        user_id=new_user.id,
        name=new_patient_data['name'],
        phone=new_patient_data['phone'],
        age=new_patient_data['age'],
        gender=new_patient_data.get('gender', ''),
        address=new_patient_data.get('address', ''),
        medical_history=new_patient_data.get('medical_history', ''),
        emergency_contact=new_patient_data.get('emergency_contact', ''),
        is_blacklisted=False
    )
    db.session.add(new_patient)
    db.session.commit()
    
    # Return success with patient info and credentials
    new_patient_info = new_patient.to_dict()
    return jsonify({
        'success': True,
        'message': 'Patient account created successfully',
        'data': {
            'patient': new_patient_info,
            'credentials': {
                'username': final_username,
                'password': temporary_password
            }
        }
    })

@admin_bp.route('/patients/<int:patient_id>/blacklist', methods=['PUT'])
@admin_required
def toggle_patient_blacklist(patient_id):
    # Find the patient by ID
    selected_patient = Patient.query.get(patient_id)
    
    # Check if patient exists
    if selected_patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient not found',
            'errors': ['Patient not found']
        }), 404
    
    # Toggle blacklist status (flip true to false or false to true)
    selected_patient.is_blacklisted = not selected_patient.is_blacklisted
    
    # Save the changes
    db.session.commit()
    
    # Determine action message
    if selected_patient.is_blacklisted:
        action_message = "blacklisted"
    else:
        action_message = "unblacklisted"
    
    # Return success response
    updated_patient_info = selected_patient.to_dict()
    return jsonify({
        'success': True,
        'message': f'Patient {action_message} successfully',
        'data': {
            'patient': updated_patient_info
        }
    })

@admin_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@admin_required
def get_patient_history(patient_id):
    # Find the patient by ID
    selected_patient = Patient.query.get(patient_id)
    
    # Check if patient exists
    if selected_patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient not found',
            'errors': ['Patient not found']
        }), 404
    
    # Get all appointments for this patient (newest first)
    patient_appointments_list = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.appointment_date.desc()).all()
    
    # Convert appointments to dictionary format
    appointments_data_list = []
    for single_appointment in patient_appointments_list:
        appointment_info = single_appointment.to_dict()
        appointments_data_list.append(appointment_info)
    
    # Get patient information
    patient_info = selected_patient.to_dict()
    
    return jsonify({
        'success': True,
        'message': 'Patient history retrieved successfully',
        'data': {
            'patient': patient_info,
            'appointments': appointments_data_list
        }
    })


# =============== Departments CRUD Operations ================

@admin_bp.route('/departments', methods=['GET'])
@admin_required
def get_departments():
    # Get all departments from database
    all_departments_list = Department.query.all()
    
    # Convert departments to dictionary format
    departments_data_list = []
    for single_department in all_departments_list:
        department_info = single_department.to_dict()
        departments_data_list.append(department_info)
    
    return jsonify({
        'success': True,
        'message': 'Departments retrieved successfully',
        'data': {
            'departments': departments_data_list
        }
    })

@admin_bp.route('/departments', methods=['POST'])
@admin_required
def add_department():
    # Get the new department data
    new_department_data = request.get_json()
    
    # Check if department name is provided
    if not new_department_data.get('name'):
        return jsonify({
            'success': False,
            'message': 'Department name is required',
            'errors': ['Missing name']
        }), 400
    
    # Check if department with same name already exists
    existing_department = Department.query.filter_by(name=new_department_data['name']).first()
    if existing_department is not None:
        return jsonify({
            'success': False,
            'message': 'Department already exists',
            'errors': ['Department name taken']
        }), 400
    
    # Create new department
    new_department = Department(
        name=new_department_data['name'],
        description=new_department_data.get('description', ''),
        is_active=True
    )
    
    # Save the new department
    db.session.add(new_department)
    db.session.commit()
    
    # Return success response with new department data
    new_department_info = new_department.to_dict()
    return jsonify({
        'success': True,
        'message': 'Department created successfully',
        'data': {
            'department': new_department_info
        }
    })

@admin_bp.route('/departments/<int:department_id>', methods=['PUT'])
@admin_required
def update_department(department_id):
    # Find the department by ID
    selected_department = Department.query.get(department_id)
    
    # Check if department exists
    if selected_department is None:
        return jsonify({
            'success': False,
            'message': 'Department not found',
            'errors': ['Department not found']
        }), 404
    
    # Get the update data
    update_data = request.get_json()
    
    # Update department name if provided
    if 'name' in update_data:
        # Check if new name already exists (except current department)
        existing_department = Department.query.filter_by(name=update_data['name']).first()
        if existing_department is not None and existing_department.id != department_id:
            return jsonify({
                'success': False,
                'message': 'Department name already exists',
                'errors': ['Name taken']
            }), 400
        selected_department.name = update_data['name']
    
    # Update description if provided
    if 'description' in update_data:
        selected_department.description = update_data['description']
    
    # Update active status if provided
    if 'is_active' in update_data:
        selected_department.is_active = update_data['is_active']
    
    # Save the changes
    db.session.commit()
    
    # Return success response with updated department data
    updated_department_info = selected_department.to_dict()
    return jsonify({
        'success': True,
        'message': 'Department updated successfully',
        'data': {
            'department': updated_department_info
        }
    })

@admin_bp.route('/departments/<int:department_id>', methods=['DELETE'])
@admin_required
def delete_department(department_id):
    # Find the department by ID
    selected_department = Department.query.get(department_id)
    
    # Check if department exists
    if selected_department is None:
        return jsonify({
            'success': False,
            'message': 'Department not found',
            'errors': ['Department not found']
        }), 404
    
    # Check if department has doctors assigned
    if selected_department.doctors:
        return jsonify({
            'success': False,
            'message': 'Cannot delete department with assigned doctors',
            'errors': ['Department has doctors']
        }), 400
    
    # Delete the department
    db.session.delete(selected_department)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Department deleted successfully',
        'data': {}
    })
