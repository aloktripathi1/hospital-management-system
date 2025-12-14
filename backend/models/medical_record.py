from datetime import datetime
from database import db

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    
    # file information
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))  # pdf, jpg, png, etc
    file_size = db.Column(db.Integer)  # in bytes
    
    # record metadata
    record_type = db.Column(db.String(50))  # prescription, lab_report, scan, xray, etc
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    record_date = db.Column(db.Date)
    
    # upload info
    uploaded_by = db.Column(db.String(20))  # patient, doctor, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'appointment_id': self.appointment_id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'record_type': self.record_type,
            'title': self.title,
            'description': self.description,
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'doctor': self.doctor.to_dict() if self.doctor else None,
            'patient': self.patient.to_dict() if self.patient else None
        }
    
    def __repr__(self):
        return f'<MedicalRecord {self.id} - {self.title}>'
