# =================== DATABASE INITIALIZATION SCRIPT ===================
# This script creates all database tables and populates them with sample data
# Run this file directly to initialize the database with test data

from app import main_app, create_database_tables
from database import db
from models import User, Doctor, Patient, DoctorAvailability, Department
from werkzeug.security import generate_password_hash
from datetime import time

# =================== SAMPLE DEPARTMENTS CREATION SECTION ===================

def create_sample_departments():
    # Check if departments already exist
    existing_departments = Department.query.first()
    
    # Create departments only if none exist
    if existing_departments is None:
        # List of hospital departments to create
        departments_list = [
            {'name': 'Cardiology', 'description': 'Heart and cardiovascular diseases'},
            {'name': 'Oncology', 'description': 'Cancer treatment and care'},
            {'name': 'Neurology', 'description': 'Brain and nervous system disorders'},
            {'name': 'Orthopedics', 'description': 'Bone and joint problems'},
            {'name': 'Pediatrics', 'description': 'Children health and medicine'},
            {'name': 'Dermatology', 'description': 'Skin and hair related issues'},
            {'name': 'Psychiatry', 'description': 'Mental health and behavioral disorders'}
        ]
        
        # Create each department
        for single_department_data in departments_list:
            new_department = Department(
                name=single_department_data['name'],
                description=single_department_data['description'],
                is_active=True
            )
            db.session.add(new_department)
        
        # Save all departments to database
        db.session.commit()
        print("Sample departments created successfully")

# =================== SAMPLE DOCTORS CREATION SECTION ===================

def create_sample_doctors():
    # Check if doctors already exist
    existing_doctors = Doctor.query.first()
    
    # Create doctors only if none exist
    if existing_doctors is None:
        # Get departments for assignment
        cardiology_department = Department.query.filter_by(name='Cardiology').first()
        oncology_department = Department.query.filter_by(name='Oncology').first()
        neurology_department = Department.query.filter_by(name='Neurology').first()
        orthopedics_department = Department.query.filter_by(name='Orthopedics').first()
        pediatrics_department = Department.query.filter_by(name='Pediatrics').first()
        
        # List of sample doctors to create
        sample_doctors_list = [
            {
                'username': 'dr_smith',
                'email': 'dr.smith@hospital.com',
                'password': 'doctor123',
                'name': 'Dr. John Smith',
                'specialization': 'Cardiology',
                'department_id': cardiology_department.id if cardiology_department else None,
                'experience': 10,
                'qualification': 'MD Cardiology',
                'phone': '+1-555-0101',
                'consultation_fee': 200
            },
            {
                'username': 'dr_johnson',
                'email': 'dr.johnson@hospital.com',
                'password': 'doctor123',
                'name': 'Dr. Sarah Johnson',
                'specialization': 'Oncology',
                'department_id': oncology_department.id if oncology_department else None,
                'experience': 8,
                'qualification': 'MD Oncology',
                'phone': '+1-555-0102',
                'consultation_fee': 250
            },
            {
                'username': 'dr_williams',
                'email': 'dr.williams@hospital.com',
                'password': 'doctor123',
                'name': 'Dr. Michael Williams',
                'specialization': 'Neurology',
                'department_id': neurology_department.id if neurology_department else None,
                'experience': 12,
                'qualification': 'MD Neurology',
                'phone': '+1-555-0103',
                'consultation_fee': 300
            },
            {
                'username': 'dr_davis',
                'email': 'dr.davis@hospital.com',
                'password': 'doctor123',
                'name': 'Dr. Emily Davis',
                'specialization': 'Orthopedics',
                'department_id': orthopedics_department.id if orthopedics_department else None,
                'experience': 6,
                'qualification': 'MD Orthopedics',
                'phone': '+1-555-0104',
                'consultation_fee': 180
            },
            {
                'username': 'dr_brown',
                'email': 'dr.brown@hospital.com',
                'password': 'doctor123',
                'name': 'Dr. James Brown',
                'specialization': 'Pediatrics',
                'department_id': pediatrics_department.id if pediatrics_department else None,
                'experience': 9,
                'qualification': 'MD Pediatrics',
                'phone': '+1-555-0105',
                'consultation_fee': 150
            }
        ]
        
        # Create each doctor with user account
        for single_doctor_data in sample_doctors_list:
            # Create user account for doctor
            doctor_user_account = User(
                username=single_doctor_data['username'],
                email=single_doctor_data['email'],
                password_hash=generate_password_hash(single_doctor_data['password']),
                role='doctor',
                is_active=True
            )
            db.session.add(doctor_user_account)
            db.session.flush()  # Get the user ID
            
            # Create doctor profile
            doctor_profile = Doctor(
                user_id=doctor_user_account.id,
                name=single_doctor_data['name'],
                specialization=single_doctor_data['specialization'],
                department_id=single_doctor_data['department_id'],
                experience=single_doctor_data['experience'],
                qualification=single_doctor_data['qualification'],
                phone=single_doctor_data['phone'],
                consultation_fee=single_doctor_data['consultation_fee'],
                is_active=True
            )
            db.session.add(doctor_profile)
        
        # Save all doctors to database
        db.session.commit()
        print("Sample doctors created successfully")

# =================== SAMPLE AVAILABILITY SCHEDULES SECTION ===================

def create_sample_availability():
    # Get all doctors from database
    all_doctors_list = Doctor.query.all()
    
    # Create availability schedules for each doctor
    for single_doctor in all_doctors_list:
        # Check if this doctor already has availability schedules
        existing_availability = DoctorAvailability.query.filter_by(doctor_id=single_doctor.id).first()
        
        # Create availability only if none exists for this doctor
        if existing_availability is None:
            # Create schedules for weekdays (Monday=0 to Friday=4)
            for weekday_number in range(5):
                # Create morning availability (9 AM to 1 PM)
                morning_schedule = DoctorAvailability(
                    doctor_id=single_doctor.id,
                    day_of_week=weekday_number,
                    start_time=time(9, 0),   # 9:00 AM
                    end_time=time(13, 0),    # 1:00 PM
                    is_available=True
                )
                db.session.add(morning_schedule)
                
                # Create afternoon availability (2 PM to 6 PM)
                afternoon_schedule = DoctorAvailability(
                    doctor_id=single_doctor.id,
                    day_of_week=weekday_number,
                    start_time=time(14, 0),  # 2:00 PM
                    end_time=time(18, 0),    # 6:00 PM
                    is_available=True
                )
                db.session.add(afternoon_schedule)
    
    # Save all availability schedules to database
    db.session.commit()
    print("Sample availability schedules created successfully")

# =================== SAMPLE PATIENTS CREATION SECTION ===================

def create_sample_patients():
    # Check if patients already exist
    existing_patients = Patient.query.first()
    
    # Create patients only if none exist
    if existing_patients is None:
        # List of sample patients to create
        sample_patients_list = [
            {
                'username': 'patient1',
                'email': 'patient1@example.com',
                'password': 'patient123',
                'name': 'John Doe',
                'phone': '+1-234-567-8901',
                'address': '123 Main St, Springfield',
                'age': 45,
                'gender': 'Male',
                'medical_history': 'Hypertension, Diabetes Type 2'
            },
            {
                'username': 'patient2',
                'email': 'patient2@example.com',
                'password': 'patient123',
                'name': 'Jane Smith',
                'phone': '+1-234-567-8902',
                'address': '456 Oak Ave, Springfield',
                'age': 32,
                'gender': 'Female',
                'medical_history': 'Allergic to penicillin'
            },
            {
                'username': 'patient3',
                'email': 'patient3@example.com',
                'password': 'patient123',
                'name': 'Robert Johnson',
                'phone': '+1-234-567-8903',
                'address': '789 Pine Rd, Springfield',
                'age': 28,
                'gender': 'Male',
                'medical_history': 'No known medical conditions'
            },
            {
                'username': 'patient4',
                'email': 'patient4@example.com',
                'password': 'patient123',
                'name': 'Maria Garcia',
                'phone': '+1-234-567-8904',
                'address': '321 Elm St, Springfield',
                'age': 56,
                'gender': 'Female',
                'medical_history': 'Arthritis, High cholesterol'
            },
            {
                'username': 'patient5',
                'email': 'patient5@example.com',
                'password': 'patient123',
                'name': 'David Wilson',
                'phone': '+1-234-567-8905',
                'address': '654 Maple Dr, Springfield',
                'age': 41,
                'gender': 'Male',
                'medical_history': 'Asthma, Seasonal allergies'
            }
        ]
        
        # Create each patient with user account
        for single_patient_data in sample_patients_list:
            # Create user account for patient
            patient_user_account = User(
                username=single_patient_data['username'],
                email=single_patient_data['email'],
                password_hash=generate_password_hash(single_patient_data['password']),
                role='patient',
                is_active=True
            )
            db.session.add(patient_user_account)
            db.session.flush()  # Get the user ID
            
            # Create patient profile
            patient_profile = Patient(
                user_id=patient_user_account.id,
                name=single_patient_data['name'],
                phone=single_patient_data['phone'],
                address=single_patient_data['address'],
                age=single_patient_data['age'],
                gender=single_patient_data['gender'],
                medical_history=single_patient_data['medical_history'],
                is_blacklisted=False
            )
            db.session.add(patient_profile)
        
        # Save all patients to database
        db.session.commit()
        print("Sample patients created successfully")

# =================== DATABASE INITIALIZATION EXECUTION SECTION ===================

if __name__ == '__main__':
    print("Starting database initialization process...")
    
    # Use Flask application context for database operations
    with main_app.app_context():
        # Step 1: Create all database tables and default admin user
        create_database_tables()
        
        # Step 2: Create sample departments
        create_sample_departments()
        
        # Step 3: Create sample doctors with their user accounts
        create_sample_doctors()
        
        # Step 4: Create availability schedules for all doctors
        create_sample_availability()
        
        # Step 5: Create sample patients with their user accounts
        create_sample_patients()
    
    print("\n" + "="*60)
    print("DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nDefault login credentials for testing:")
    print("\n📋 ADMIN ACCESS:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n👨‍⚕️ DOCTOR ACCOUNTS:")
    print("   Username: dr_smith     | Password: doctor123 | Specialization: Cardiology")
    print("   Username: dr_johnson   | Password: doctor123 | Specialization: Oncology")
    print("   Username: dr_williams  | Password: doctor123 | Specialization: Neurology")
    print("   Username: dr_davis     | Password: doctor123 | Specialization: Orthopedics")
    print("   Username: dr_brown     | Password: doctor123 | Specialization: Pediatrics")
    print("\n🏥 PATIENT ACCOUNTS:")
    print("   Username: patient1     | Password: patient123 | Name: John Doe")
    print("   Username: patient2     | Password: patient123 | Name: Jane Smith")
    print("   Username: patient3     | Password: patient123 | Name: Robert Johnson")
    print("   Username: patient4     | Password: patient123 | Name: Maria Garcia")
    print("   Username: patient5     | Password: patient123 | Name: David Wilson")
    print("\n💡 TIP: Run 'python app.py' to start the hospital management system!")
    print("="*60)
