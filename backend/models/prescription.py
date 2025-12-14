from datetime import datetime
from database import db

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False, unique=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    
    # prescription details
    diagnosis = db.Column(db.Text, nullable=False)
    medications = db.Column(db.Text, nullable=False)  # JSON string or plain text
    dosage_instructions = db.Column(db.Text)
    duration = db.Column(db.String(100))  # e.g., "7 days", "2 weeks"
    
    # additional info
    lab_tests = db.Column(db.Text)  # recommended lab tests
    follow_up_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    
    # status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'diagnosis': self.diagnosis,
            'medications': self.medications,
            'dosage_instructions': self.dosage_instructions,
            'duration': self.duration,
            'lab_tests': self.lab_tests,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'doctor': self.doctor.to_dict() if self.doctor else None,
            'patient': self.patient.to_dict() if self.patient else None,
            'appointment': self.appointment.to_dict() if self.appointment else None
        }
    
    def __repr__(self):
        return f'<Prescription {self.id} - Patient: {self.patient_id}>'
