from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from database import db
from models import MedicalRecord, Patient, Doctor, Appointment
from datetime import datetime
from decorators import patient_required, doctor_required, admin_required, get_current_user_id
import os

medical_bp = Blueprint('medical', __name__)

# allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
UPLOAD_FOLDER = 'uploads/medical_records'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# patient uploads medical record
@medical_bp.route('/records', methods=['POST'])
@patient_required
def upload_medical_record():
    try:
        user_id = get_current_user_id()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'success': False, 'message': 'Patient profile not found'}), 404
        
        # check if file is present
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type. Allowed: pdf, png, jpg, jpeg, doc, docx'}), 400
        
        # check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'message': 'File too large. Max size is 10 MB'}), 400
        
        # save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"patient_{patient.id}_{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(file_path)
        
        # get form data
        record_type = request.form.get('record_type', 'other')
        title = request.form.get('title', filename)
        description = request.form.get('description', '')
        record_date_str = request.form.get('record_date')
        
        record_date = None
        if record_date_str:
            try:
                record_date = datetime.strptime(record_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # create medical record entry
        medical_record = MedicalRecord(
            patient_id=patient.id,
            file_name=filename,
            file_path=file_path,
            file_type=filename.rsplit('.', 1)[1].lower(),
            file_size=file_size,
            record_type=record_type,
            title=title,
            description=description,
            record_date=record_date,
            uploaded_by='patient'
        )
        
        db.session.add(medical_record)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Medical record uploaded successfully', 'data': {'record': medical_record.to_dict()}})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to upload medical record', 'errors': [str(e)]}), 500

# get all medical records for patient
@medical_bp.route('/records', methods=['GET'])
@patient_required
def get_patient_medical_records():
    try:
        user_id = get_current_user_id()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'success': False, 'message': 'Patient profile not found'}), 404
        
        records = MedicalRecord.query.filter_by(patient_id=patient.id).order_by(MedicalRecord.created_at.desc()).all()
        
        return jsonify({'success': True, 'message': 'Medical records retrieved successfully', 'data': {'records': [r.to_dict() for r in records]}})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to retrieve medical records', 'errors': [str(e)]}), 500

# get specific medical record
@medical_bp.route('/records/<int:record_id>', methods=['GET'])
@patient_required
def get_medical_record(record_id):
    try:
        user_id = get_current_user_id()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'success': False, 'message': 'Patient profile not found'}), 404
        
        record = MedicalRecord.query.filter_by(id=record_id, patient_id=patient.id).first()
        
        if not record:
            return jsonify({'success': False, 'message': 'Medical record not found'}), 404
        
        return jsonify({'success': True, 'message': 'Medical record retrieved successfully', 'data': {'record': record.to_dict()}})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to retrieve medical record', 'errors': [str(e)]}), 500

# download medical record file
@medical_bp.route('/records/<int:record_id>/download', methods=['GET'])
@patient_required
def download_medical_record(record_id):
    try:
        user_id = get_current_user_id()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'success': False, 'message': 'Patient profile not found'}), 404
        
        record = MedicalRecord.query.filter_by(id=record_id, patient_id=patient.id).first()
        
        if not record:
            return jsonify({'success': False, 'message': 'Medical record not found'}), 404
        
        directory = os.path.dirname(record.file_path)
        filename = os.path.basename(record.file_path)
        
        return send_from_directory(directory, filename, as_attachment=True, download_name=record.file_name)
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to download medical record', 'errors': [str(e)]}), 500

# delete medical record
@medical_bp.route('/records/<int:record_id>', methods=['DELETE'])
@patient_required
def delete_medical_record(record_id):
    try:
        user_id = get_current_user_id()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'success': False, 'message': 'Patient profile not found'}), 404
        
        record = MedicalRecord.query.filter_by(id=record_id, patient_id=patient.id).first()
        
        if not record:
            return jsonify({'success': False, 'message': 'Medical record not found'}), 404
        
        # delete file
        if os.path.exists(record.file_path):
            os.remove(record.file_path)
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Medical record deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to delete medical record', 'errors': [str(e)]}), 500

# doctor views patient's medical records
@medical_bp.route('/patient/<int:patient_id>/records', methods=['GET'])
@doctor_required
def doctor_view_patient_records(patient_id):
    try:
        patient = Patient.query.get(patient_id)
        
        if not patient:
            return jsonify({'success': False, 'message': 'Patient not found'}), 404
        
        records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.created_at.desc()).all()
        
        return jsonify({'success': True, 'message': 'Patient medical records retrieved successfully', 'data': {'records': [r.to_dict() for r in records], 'patient': patient.to_dict()}})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to retrieve patient medical records', 'errors': [str(e)]}), 500
