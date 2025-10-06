# ----------- Import Required Libraries -----------
from datetime import datetime
from database import db

# ----------- Appointment Model -----------
class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    # Appointment basic details
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True)  # Can be empty for available slots
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    
    # Appointment status and info
    status = db.Column(db.String(20), default='available')  # available, booked, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Prevent double booking - one doctor cannot have same time slot twice
    __table_args__ = (db.UniqueConstraint('doctor_id', 'appointment_date', 'appointment_time', name='unique_doctor_slot'),)
    
    # Connect to treatments table
    treatments = db.relationship('Treatment', backref='appointment', lazy=True)
    
    # Get appointment information as dictionary
    def get_appointment_data(self):
        appointment_info = {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'appointment_date': self.appointment_date.strftime('%Y-%m-%d') if self.appointment_date else None,
            'appointment_time': self.appointment_time.strftime('%H:%M') if self.appointment_time else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        
        # Add patient details if appointment is booked
        if self.patient:
            appointment_info['patient_name'] = self.patient.name
            appointment_info['patient_phone'] = self.patient.phone
            
            # Add nested patient object for frontend
            appointment_info['patient'] = {
                'id': self.patient.id,
                'name': self.patient.name,
                'phone': self.patient.phone,
                'age': self.patient.age,
                'gender': self.patient.gender,
                'address': self.patient.address,
                'medical_history': self.patient.medical_history
            }
            
        # Add doctor details in nested object format for frontend compatibility
        if self.doctor:
            appointment_info['doctor_name'] = self.doctor.name
            appointment_info['doctor_specialization'] = self.doctor.specialization
            appointment_info['consultation_fee'] = self.doctor.consultation_fee
            
            # Add nested doctor object for frontend
            appointment_info['doctor'] = {
                'id': self.doctor.id,
                'name': self.doctor.name,
                'specialization': self.doctor.specialization,
                'department': self.doctor.department.name if self.doctor.department else self.doctor.specialization,
                'qualification': self.doctor.qualification,
                'consultation_fee': self.doctor.consultation_fee
            }
            
        return appointment_info
    
    # Show appointment info when printing
    def __repr__(self):
        return f'<Appointment: {self.id} - {self.appointment_date} {self.appointment_time}>'

    # Add to_dict for API compatibility
    def to_dict(self):
        return self.get_appointment_data()

