from app import app
from database import db
from models import Patient, Appointment

with app.app_context():
    patients = Patient.query.all()
    appointments = Appointment.query.all()
    print(f"Total Patients: {len(patients)}")
    for p in patients:
        print(f"Patient: {p.id} - {p.name}")
        
    print(f"Total Appointments: {len(appointments)}")
    for a in appointments:
        print(f"Appointment: {a.id} - {a.patient_id} - {a.doctor_id}")
