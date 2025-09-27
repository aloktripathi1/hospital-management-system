from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import User, Patient, Doctor, Appointment, Treatment
from werkzeug.security import generate_password_hash
from datetime import datetime, date

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to ensure user is admin"""
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required',
                'errors': ['Unauthorized']
            }), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
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
@jwt_required()
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

@admin_bp.route('/doctors', methods=['POST'])
@jwt_required()
@admin_required
def add_doctor():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'name', 'specialization']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field.title()} is required',
                    'errors': [f'Missing {field}']
                }), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'message': 'Username already exists',
                'errors': ['Username taken']
            }), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': 'Email already exists',
                'errors': ['Email taken']
            }), 400
        
        # Create new doctor user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role='doctor'
        )
        db.session.add(user)
        db.session.flush()
        
        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            name=data['name'],
            specialization=data['specialization'],
            experience=data.get('experience', 0),
            qualification=data.get('qualification', ''),
            phone=data.get('phone', ''),
            consultation_fee=data.get('consultation_fee', 0.0)
        )
        db.session.add(doctor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Doctor added successfully',
            'data': {
                'doctor': doctor.to_dict()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to add doctor',
            'errors': [str(e)]
        }), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
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
