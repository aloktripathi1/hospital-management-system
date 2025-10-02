from flask import Blueprint, request, jsonify
from database import db
from models import User, Patient, Doctor, Appointment, Treatment, Department
from werkzeug.security import generate_password_hash
from datetime import datetime, date
from sqlalchemy import or_
from decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard-stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    try:
        total_doctors = Doctor.query.count()
        active_doctors = Doctor.query.filter_by(is_active=True).count()
        total_patients = Patient.query.count()
        today_appointments = Appointment.query.filter_by(appointment_date=date.today()).count()
        
        return jsonify({
            'success': True,
            'message': 'Dashboard stats retrieved',
            'data': {
                'total_doctors': total_doctors,
                'active_doctors': active_doctors,
                'total_patients': total_patients,
                'today_appointments': today_appointments
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get dashboard stats',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/doctors', methods=['GET'])
@admin_required
def get_doctors():
    try:
        doctors = Doctor.query.all()
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


@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@admin_required
def update_doctor(doctor_id):
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({
                'success': False,
                'message': 'Doctor not found',
                'errors': ['Doctor not found']
            }), 404
        
        data = request.get_json()
        
        # Update doctor fields
        if 'name' in data:
            doctor.name = data['name']
        if 'specialization' in data:
            doctor.specialization = data['specialization']
        if 'experience' in data:
            doctor.experience = data['experience']
        if 'qualification' in data:
            doctor.qualification = data['qualification']
        if 'phone' in data:
            doctor.phone = data['phone']
        if 'consultation_fee' in data:
            doctor.consultation_fee = data['consultation_fee']
        if 'is_active' in data:
            doctor.is_active = data['is_active']
            doctor.user.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Doctor updated successfully',
            'data': {
                'doctor': doctor.to_dict()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update doctor',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@admin_required
def delete_doctor(doctor_id):
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({
                'success': False,
                'message': 'Doctor not found',
                'errors': ['Doctor not found']
            }), 404
        
        # Soft delete - deactivate instead of actual deletion
        doctor.is_active = False
        doctor.user.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Doctor deactivated successfully',
            'data': {}
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to delete doctor',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/patients', methods=['GET'])
@admin_required
def get_patients():
    try:
        patients = Patient.query.all()
        return jsonify({
            'success': True,
            'message': 'Patients retrieved successfully',
            'data': {
                'patients': [patient.to_dict() for patient in patients]
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get patients',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@admin_required
def update_patient(patient_id):
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient not found',
                'errors': ['Patient not found']
            }), 404
        
        data = request.get_json()
        
        # Update patient fields
        if 'name' in data:
            patient.name = data['name']
        if 'phone' in data:
            patient.phone = data['phone']
        if 'address' in data:
            patient.address = data['address']
        if 'age' in data:
            patient.age = data['age']
        if 'gender' in data:
            patient.gender = data['gender']
        if 'medical_history' in data:
            patient.medical_history = data['medical_history']
        if 'emergency_contact' in data:
            patient.emergency_contact = data['emergency_contact']
        if 'is_active' in data:
            patient.user.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Patient updated successfully',
            'data': {
                'patient': patient.to_dict()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update patient',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def get_appointments():
    try:
        appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
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

@admin_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@admin_required
def update_appointment(appointment_id):
    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({
                'success': False,
                'message': 'Appointment not found',
                'errors': ['Appointment not found']
            }), 404
        
        data = request.get_json()
        
        if 'status' in data:
            appointment.status = data['status']
        if 'notes' in data:
            appointment.notes = data['notes']
        
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment updated successfully',
            'data': {
                'appointment': appointment.to_dict()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update appointment',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/search', methods=['GET'])
@admin_required
def search():
    try:
        search_type = request.args.get('type')
        query = request.args.get('query', '')
        
        if not search_type or not query:
            return jsonify({
                'success': False,
                'message': 'Search type and query are required',
                'errors': ['Missing parameters']
            }), 400
        
        results = []
        
        if search_type == 'doctor':
            doctors = Doctor.query.filter(
                Doctor.name.contains(query) | 
                Doctor.specialization.contains(query)
            ).all()
            results = [doctor.to_dict() for doctor in doctors]
        
        elif search_type == 'patient':
            patients = Patient.query.filter(
                Patient.name.contains(query) |
                Patient.phone.contains(query)
            ).all()
            results = [patient.to_dict() for patient in patients]
        
        elif search_type == 'appointment':
            appointments = Appointment.query.join(Patient).join(Doctor).filter(
                Patient.name.contains(query) |
                Doctor.name.contains(query)
            ).all()
            results = [appointment.to_dict() for appointment in appointments]
        
        return jsonify({
            'success': True,
            'message': 'Search completed successfully',
            'data': {
                'results': results,
                'count': len(results)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Search failed',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/search/doctors', methods=['GET'])
@admin_required
def search_doctors():
    """Search doctors by specialization or name"""
    try:
        query = request.args.get('q', '')
        specialization = request.args.get('specialization', '')
        
        if not query and not specialization:
            return jsonify({
                'success': False,
                'message': 'Search query or specialization is required',
                'errors': ['Missing search parameters']
            }), 400
        
        # Build search query
        search_query = Doctor.query
        
        if query:
            search_query = search_query.filter(
                or_(
                    Doctor.name.ilike(f'%{query}%'),
                    Doctor.specialization.ilike(f'%{query}%')
                )
            )
        
        if specialization:
            search_query = search_query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
        
        doctors = search_query.all()
        
        return jsonify({
            'success': True,
            'message': 'Doctors found',
            'data': {
                'doctors': [doctor.to_dict() for doctor in doctors],
                'count': len(doctors)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Search failed',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/search/patients', methods=['GET'])
@admin_required
def search_patients():
    """Search patients by name or email"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'success': False,
                'message': 'Search query is required',
                'errors': ['Missing search parameter']
            }), 400
        
        # Search patients by name or email
        patients = db.session.query(Patient).join(User).filter(
            or_(
                Patient.name.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        ).all()
        
        return jsonify({
            'success': True,
            'message': 'Patients found',
            'data': {
                'patients': [patient.to_dict() for patient in patients],
                'count': len(patients)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Search failed',
            'errors': [str(e)]
        }), 500


@admin_bp.route('/doctors', methods=['POST'])
@admin_required
def add_doctor():
    """Add a new doctor"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'specialization', 'phone', 'experience', 'qualification']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field.replace("_", " ").title()} is required',
                    'errors': [f'Missing {field}']
                }), 400
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': 'Email already exists',
                'errors': ['Email taken']
            }), 400
        
        # Generate username from email (part before @)
        username = data['email'].split('@')[0]
        # Ensure username is unique
        original_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Generate simple temporary password: firstname + 123
        name_parts = data['name'].split()
        # Skip titles like Dr., Mr., Ms., etc.
        first_name = name_parts[1].lower() if name_parts[0].lower() in ['dr.', 'dr', 'mr.', 'mr', 'ms.', 'ms', 'mrs.', 'mrs'] else name_parts[0].lower()
        temp_password = f"{first_name}123"
        
        # Create user account
        user = User(
            username=username,
            email=data['email'],
            password_hash=generate_password_hash(temp_password),
            role='doctor'
        )
        db.session.add(user)
        db.session.flush()
        
        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            name=data['name'],
            specialization=data['specialization'],
            phone=data['phone'],
            experience=data['experience'],
            qualification=data['qualification'],
            is_active=True
        )
        db.session.add(doctor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Doctor account created successfully',
            'data': {
                'doctor': doctor.to_dict(),
                'credentials': {
                    'username': username,
                    'password': temp_password
                }
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to create doctor account',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/patients', methods=['POST'])
@admin_required
def add_patient():
    """Add a new patient"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'phone', 'age']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field.replace("_", " ").title()} is required',
                    'errors': [f'Missing {field}']
                }), 400
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': 'Email already exists',
                'errors': ['Email taken']
            }), 400
        
        # Generate username from email (part before @)
        username = data['email'].split('@')[0]
        # Ensure username is unique
        original_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Generate simple temporary password: firstname + 123
        name_parts = data['name'].split()
        # Skip titles like Dr., Mr., Ms., etc.
        first_name = name_parts[1].lower() if name_parts[0].lower() in ['dr.', 'dr', 'mr.', 'mr', 'ms.', 'ms', 'mrs.', 'mrs'] else name_parts[0].lower()
        temp_password = f"{first_name}123"
        
        # Create user account
        user = User(
            username=username,
            email=data['email'],
            password_hash=generate_password_hash(temp_password),
            role='patient'
        )
        db.session.add(user)
        db.session.flush()
        
        # Create patient profile
        patient = Patient(
            user_id=user.id,
            name=data['name'],
            phone=data['phone'],
            age=data['age'],
            gender=data.get('gender', ''),
            address=data.get('address', ''),
            medical_history=data.get('medical_history', ''),
            emergency_contact=data.get('emergency_contact', ''),
            is_blacklisted=False
        )
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Patient account created successfully',
            'data': {
                'patient': patient.to_dict(),
                'credentials': {
                    'username': username,
                    'password': temp_password
                }
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to create patient account',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/patients/<int:patient_id>/blacklist', methods=['PUT'])
@admin_required
def toggle_patient_blacklist(patient_id):
    """Toggle patient blacklist status"""
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient not found',
                'errors': ['Patient not found']
            }), 404
        
        # Toggle blacklist status
        patient.is_blacklisted = not patient.is_blacklisted
        db.session.commit()
        
        action = "blacklisted" if patient.is_blacklisted else "unblacklisted"
        
        return jsonify({
            'success': True,
            'message': f'Patient {action} successfully',
            'data': {
                'patient': patient.to_dict()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update patient blacklist status',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@admin_required
def get_patient_history(patient_id):
    """Get patient appointment history"""
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient not found',
                'errors': ['Patient not found']
            }), 404
        
        # Get all appointments for this patient
        appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.appointment_date.desc()).all()
        
        return jsonify({
            'success': True,
            'message': 'Patient history retrieved successfully',
            'data': {
                'patient': patient.to_dict(),
                'appointments': [appointment.to_dict() for appointment in appointments]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get patient history',
            'errors': [str(e)]
        }), 500

# Department CRUD Operations
@admin_bp.route('/departments', methods=['GET'])
@admin_required
def get_departments():
    """Get all departments"""
    try:
        departments = Department.query.all()
        return jsonify({
            'success': True,
            'message': 'Departments retrieved successfully',
            'data': {
                'departments': [dept.to_dict() for dept in departments]
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get departments',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/departments', methods=['POST'])
@admin_required
def add_department():
    """Add a new department"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({
                'success': False,
                'message': 'Department name is required',
                'errors': ['Missing name']
            }), 400
        
        # Check if department already exists
        if Department.query.filter_by(name=data['name']).first():
            return jsonify({
                'success': False,
                'message': 'Department already exists',
                'errors': ['Department name taken']
            }), 400
        
        # Create department
        department = Department(
            name=data['name'],
            description=data.get('description', ''),
            is_active=True
        )
        db.session.add(department)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Department created successfully',
            'data': {
                'department': department.to_dict()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to create department',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/departments/<int:department_id>', methods=['PUT'])
@admin_required
def update_department(department_id):
    """Update department"""
    try:
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found',
                'errors': ['Department not found']
            }), 404
        
        data = request.get_json()
        
        # Update department fields
        if 'name' in data:
            # Check if new name already exists (except current department)
            existing = Department.query.filter_by(name=data['name']).first()
            if existing and existing.id != department_id:
                return jsonify({
                    'success': False,
                    'message': 'Department name already exists',
                    'errors': ['Name taken']
                }), 400
            department.name = data['name']
        
        if 'description' in data:
            department.description = data['description']
        
        if 'is_active' in data:
            department.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Department updated successfully',
            'data': {
                'department': department.to_dict()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update department',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/departments/<int:department_id>', methods=['DELETE'])
@admin_required
def delete_department(department_id):
    """Delete department"""
    try:
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                'success': False,
                'message': 'Department not found',
                'errors': ['Department not found']
            }), 404
        
        # Check if department has doctors
        if department.doctors:
            return jsonify({
                'success': False,
                'message': 'Cannot delete department with assigned doctors',
                'errors': ['Department has doctors']
            }), 400
        
        # Delete department
        db.session.delete(department)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Department deleted successfully',
            'data': {}
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to delete department',
            'errors': [str(e)]
        }), 500
