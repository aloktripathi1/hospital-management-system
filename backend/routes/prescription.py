from flask import Blueprint, request, jsonify
from database import db
from models import Prescription, Appointment, Patient, Doctor
from datetime import datetime
from decorators import doctor_required, patient_required, get_current_user_id

prescription_bp = Blueprint('prescription', __name__)

# doctor creates prescription for appointment
@prescription_bp.route('/prescriptions', methods=['POST'])
@doctor_required
def create_prescription():
    try:
        user_id = get_current_user_id()
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404
        
        data = request.get_json()
        
        if not data.get('appointment_id'):
            return jsonify({'success': False, 'message': 'Appointment ID is required'}), 400
        
        appointment = Appointment.query.get(data['appointment_id'])
        
        if not appointment:
            return jsonify({'success': False, 'message': 'Appointment not found'}), 404
        
        if appointment.doctor_id != doctor.id:
            return jsonify({'success': False, 'message': 'Unauthorized. This is not your appointment'}), 403
        
        if appointment.status != 'completed':
            return jsonify({'success': False, 'message': 'Can only create prescription for completed appointments'}), 400
        
        # check if prescription already exists
        existing = Prescription.query.filter_by(appointment_id=appointment.id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Prescription already exists for this appointment'}), 400
        
        # create prescription
        follow_up_date = None
        if data.get('follow_up_date'):
            try:
                follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        prescription = Prescription(
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=doctor.id,
            diagnosis=data.get('diagnosis', ''),
            medications=data.get('medications', ''),
            dosage_instructions=data.get('dosage_instructions', ''),
            duration=data.get('duration', ''),
            lab_tests=data.get('lab_tests', ''),
            follow_up_date=follow_up_date,
            notes=data.get('notes', '')
        )
        
        db.session.add(prescription)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Prescription created successfully', 'data': {'prescription': prescription.to_dict()}})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to create prescription', 'errors': [str(e)]}), 500

# doctor updates prescription
@prescription_bp.route('/prescriptions/<int:prescription_id>', methods=['PUT'])
@doctor_required
def update_prescription(prescription_id):
    try:
        user_id = get_current_user_id()
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({'success': False, 'message': 'Doctor profile not found'}), 404
        
        prescription = Prescription.query.get(prescription_id)
        
        if not prescription:
            return jsonify({'success': False, 'message': 'Prescription not found'}), 404
        
        if prescription.doctor_id != doctor.id:
            return jsonify({'success': False, 'message': 'Unauthorized. This is not your prescription'}), 403
        
        data = request.get_json()
        
        if 'diagnosis' in data:
            prescription.diagnosis = data['diagnosis']
        if 'medications' in data:
            prescription.medications = data['medications']
        if 'dosage_instructions' in data:
            prescription.dosage_instructions = data['dosage_instructions']
        if 'duration' in data:
            prescription.duration = data['duration']
        if 'lab_tests' in data:
            prescription.lab_tests = data['lab_tests']
        if 'notes' in data:
            prescription.notes = data['notes']
        if 'follow_up_date' in data:
            if data['follow_up_date']:
                try:
                    prescription.follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()
                except ValueError:
                    pass
            else:
                prescription.follow_up_date = None
        
        prescription.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Prescription updated successfully', 'data': {'prescription': prescription.to_dict()}})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to update prescription', 'errors': [str(e)]}), 500

# patient views their prescriptions
@prescription_bp.route('/prescriptions', methods=['GET'])
@patient_required
def get_patient_prescriptions():
    try:
        user_id = get_current_user_id()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'success': False, 'message': 'Patient profile not found'}), 404
        
        prescriptions = Prescription.query.filter_by(patient_id=patient.id).order_by(Prescription.created_at.desc()).all()
        
        return jsonify({'success': True, 'message': 'Prescriptions retrieved successfully', 'data': {'prescriptions': [p.to_dict() for p in prescriptions]}})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to retrieve prescriptions', 'errors': [str(e)]}), 500

# get specific prescription
@prescription_bp.route('/prescriptions/<int:prescription_id>', methods=['GET'])
@patient_required
def get_prescription(prescription_id):
    try:
        user_id = get_current_user_id()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'success': False, 'message': 'Patient profile not found'}), 404
        
        prescription = Prescription.query.filter_by(id=prescription_id, patient_id=patient.id).first()
        
        if not prescription:
            return jsonify({'success': False, 'message': 'Prescription not found'}), 404
        
        return jsonify({'success': True, 'message': 'Prescription retrieved successfully', 'data': {'prescription': prescription.to_dict()}})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to retrieve prescription', 'errors': [str(e)]}), 500

# doctor views patient's prescriptions (for history)
@prescription_bp.route('/patient/<int:patient_id>/prescriptions', methods=['GET'])
@doctor_required
def doctor_view_patient_prescriptions(patient_id):
    try:
        patient = Patient.query.get(patient_id)
        
        if not patient:
            return jsonify({'success': False, 'message': 'Patient not found'}), 404
        
        prescriptions = Prescription.query.filter_by(patient_id=patient_id).order_by(Prescription.created_at.desc()).all()
        
        return jsonify({'success': True, 'message': 'Patient prescriptions retrieved successfully', 'data': {'prescriptions': [p.to_dict() for p in prescriptions], 'patient': patient.to_dict()}})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to retrieve patient prescriptions', 'errors': [str(e)]}), 500
