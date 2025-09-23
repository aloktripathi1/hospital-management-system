"""
Database initialization script
Run this to create tables and sample data
"""
from app import app, create_tables
from models import db, User, Doctor, Patient, DoctorAvailability
from werkzeug.security import generate_password_hash
from datetime import time

def create_sample_availability():
    """Create sample availability schedules for doctors"""
    doctors = Doctor.query.all()
    
    for doctor in doctors:
        # Check if availability already exists
        if not DoctorAvailability.query.filter_by(doctor_id=doctor.id).first():
            # Create weekday availability (Monday to Friday)
            for day in range(5):  # 0=Monday, 4=Friday
                # Morning slots
                morning_availability = DoctorAvailability(
                    doctor_id=doctor.id,
                    day_of_week=day,
                    start_time=time(9, 0),  # 9:00 AM
                    end_time=time(13, 0),   # 1:00 PM
                    is_available=True
                )
                db.session.add(morning_availability)
                
                # Evening slots
                evening_availability = DoctorAvailability(
                    doctor_id=doctor.id,
                    day_of_week=day,
                    start_time=time(14, 0),  # 2:00 PM
                    end_time=time(18, 0),    # 6:00 PM
                    is_available=True
                )
                db.session.add(evening_availability)
    
    db.session.commit()
    print("Sample availability schedules created")

def create_sample_patients():
    """Create sample patients for testing"""
    if not Patient.query.first():
        sample_patients = [
            {
                'username': 'patient1',
                'email': 'patient1@example.com',
                'password': 'patient123',
                'name': 'John Doe',
                'phone': '+1-234-567-8901',
                'address': '123 Main St, City',
                'age': 45
            },
            {
                'username': 'patient2',
                'email': 'patient2@example.com',
                'password': 'patient123',
                'name': 'Jane Smith',
                'phone': '+1-234-567-8902',
                'address': '456 Oak Ave, City',
                'age': 32
            }
        ]
        
        for patient_data in sample_patients:
            user = User(
                username=patient_data['username'],
                email=patient_data['email'],
                password_hash=generate_password_hash(patient_data['password']),
                role='patient'
            )
            db.session.add(user)
            db.session.flush()
            
            patient = Patient(
                user_id=user.id,
                name=patient_data['name'],
                phone=patient_data['phone'],
                address=patient_data['address'],
                age=patient_data['age']
            )
            db.session.add(patient)
        
        db.session.commit()
        print("Sample patients created")

if __name__ == '__main__':
    print("Initializing database...")
    with app.app_context():
        create_tables()
        create_sample_availability()
        create_sample_patients()
    print("Database initialization complete!")
    print("\nDefault login credentials:")
    print("Admin: admin / admin123")
    print("Doctor: dr_smith / doctor123")
    print("Doctor: dr_johnson / doctor123") 
    print("Patient: patient1 / patient123")
    print("Patient: patient2 / patient123")
