from app import app
from database import db
from models import User, Doctor, Patient, DoctorAvailability, Appointment
from werkzeug.security import generate_password_hash
from datetime import date, timedelta, time as datetime_time

# =================== ADMIN USER CREATION SECTION ===================

def create_admin_user():
    existing_admin = User.query.filter_by(username='admin').first()
    if existing_admin is None:
        admin_user = User(
            username='admin',
            email='admin@medihub.in',
            password_hash=generate_password_hash('Admin@123'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully")

# =================== SAMPLE DOCTORS CREATION SECTION ===================

def create_sample_doctors():
    existing_doctors = Doctor.query.first()
    if existing_doctors is None:
        sample_doctors_list = [
            {
                'username': 'dr_ajay',
                'email': 'ajay.kumar@medihub.in',
                'password': 'Doctor#123',
                'name': 'Ajay Kumar',
                'specialization': 'Cardiology',
                'experience': 14,
                'qualification': 'MD, DM (Cardiology)',
                'phone': '+91-9876543210',
                'consultation_fee': 1200
            },
            {
                'username': 'dr_rajesh',
                'email': 'rajesh.verma@medihub.in',
                'password': 'Doctor#123',
                'name': 'Rajesh Verma',
                'specialization': 'Neurology',
                'experience': 12,
                'qualification': 'MBBS, MD (Neurology)',
                'phone': '+91-9876543212',
                'consultation_fee': 1400
            },
            {
                'username': 'dr_sneha',
                'email': 'sneha.patel@medihub.in',
                'password': 'Doctor#123',
                'name': 'Sneha Patel',
                'specialization': 'Orthopedics',
                'experience': 8,
                'qualification': 'MS Orthopedics',
                'phone': '+91-9876543213',
                'consultation_fee': 1000
            },
            {
                'username': 'dr_rahul',
                'email': 'rahul.kumar@medihub.in',
                'password': 'Doctor#123',
                'name': 'Rahul Kumar',
                'specialization': 'Psychiatry',
                'experience': 11,
                'qualification': 'MD Psychiatry',
                'phone': '+91-9876543216',
                'consultation_fee': 1000
            }
        ]

        for d in sample_doctors_list:
            doctor_user_account = User(
                username=d['username'],
                email=d['email'],
                password_hash=generate_password_hash(d['password']),
                role='doctor',
                is_active=True
            )
            db.session.add(doctor_user_account)
            db.session.flush()

            doctor_profile = Doctor(
                user_id=doctor_user_account.id,
                name=d['name'],
                specialization=d['specialization'],
                experience=d['experience'],
                qualification=d['qualification'],
                phone=d['phone'],
                consultation_fee=d['consultation_fee'],
                is_active=True
            )
            db.session.add(doctor_profile)

        db.session.commit()
        print("Sample doctors created successfully")

# =================== SAMPLE AVAILABILITY SCHEDULES SECTION ===================

def create_sample_availability():
    """
    Create simplified 2-slot availability for next 7 days for all doctors
    Morning: 9AM-1PM, Evening: 3PM-7PM
    Only creates DoctorAvailability records - no pre-created appointment slots
    """
    all_doctors_list = Doctor.query.all()
    today = date.today()
    
    for doc in all_doctors_list:
        # Create availability for next 7 days
        for i in range(7):
            current_date = today + timedelta(days=i)
            
            # Morning slot availability
            morning_availability = DoctorAvailability(
                doctor_id=doc.id,
                availability_date=current_date,
                slot_type='morning',
                is_available=True
            )
            db.session.add(morning_availability)
            
            # Evening slot availability
            evening_availability = DoctorAvailability(
                doctor_id=doc.id,
                availability_date=current_date,
                slot_type='evening',
                is_available=True
            )
            db.session.add(evening_availability)
    
    db.session.commit()
    print("Sample availability schedules created (2 slots per day for next 7 days)")
    print("Appointments will be created when patients book slots")

# =================== SAMPLE PATIENTS CREATION SECTION ===================

def create_sample_patients():
    existing_patients = Patient.query.first()
    if existing_patients is None:
        sample_patients_list = [
            {
                'username': 'arjun',
                'email': 'arjun.patel@gmail.com',
                'password': 'arjun',
                'name': 'Arjun Patel',
                'phone': '+91-9100001001',
                'address': 'Flat 201, S V Apartments, Andheri East, Mumbai',
                'age': 37,
                'gender': 'Male',
                'medical_history': 'Hypertension'
            },
            {
                'username': 'vikram30',
                'email': 'vikram.singh@gmail.com',
                'password': 'Patient#123',
                'name': 'Vikram Singh',
                'phone': '+91-9100001003',
                'address': '12, MG Road, Bengaluru',
                'age': 29,
                'gender': 'Male',
                'medical_history': 'Asthma'
            },
            {
                'username': 'anjali56',
                'email': 'anjali.mukherjee@gmail.com',
                'password': 'Patient#123',
                'name': 'Anjali Mukherjee',
                'phone': '+91-9100001004',
                'address': 'House No. 7, Salt Lake, Kolkata',
                'age': 56,
                'gender': 'Female',
                'medical_history': 'Diabetes Type 2'
            }
        ]

        for p in sample_patients_list:
            patient_user_account = User(
                username=p['username'],
                email=p['email'],
                password_hash=generate_password_hash(p['password']),
                role='patient',
                is_active=True
            )
            db.session.add(patient_user_account)
            db.session.flush()

            patient_profile = Patient(
                user_id=patient_user_account.id,
                name=p['name'],
                phone=p['phone'],
                address=p['address'],
                age=p['age'],
                gender=p['gender'],
                medical_history=p['medical_history'],
                is_blacklisted=False
            )
            db.session.add(patient_profile)

        db.session.commit()
        print("Sample patients created successfully")

# =================== DATABASE INITIALIZATION EXECUTION SECTION ===================

if __name__ == '__main__':
    print("Starting database initialization process...")

    with app.app_context():
        # Create all database tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        create_admin_user()
        create_sample_doctors()
        create_sample_availability()
        create_sample_patients()

    print("\n" + "="*60)
    print("MediHub - Hospital Management System (Simplified 2-Slot System)")
    print("DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nDefault login credentials for testing purposes:")
    print("\n📋 ADMIN ACCESS:")
    print("   Username: admin")
    print("   Password: Admin@123")
    print("\n👨‍⚕️ DOCTOR ACCOUNTS:")
    print("   Username: dr_ajay       | Password: Doctor#123 | Specialization: Cardiology")
    print("   Username: dr_rajesh     | Password: Doctor#123 | Specialization: Neurology")
    print("   Username: dr_sneha      | Password: Doctor#123 | Specialization: Orthopedics")
    print("   Username: dr_rahul      | Password: Doctor#123 | Specialization: Psychiatry")
    print("\n🏥 PATIENT ACCOUNTS:")
    print("   Username: arjun         | Password: arjun      | Name: Arjun Patel")
    print("   Username: vikram30      | Password: Patient#123 | Name: Vikram Singh")
    print("   Username: anjali56      | Password: Patient#123 | Name: Anjali Mukherjee")
    print("\n⏰ AVAILABILITY SYSTEM:")
    print("   - Morning Slot: 9:00 AM - 1:00 PM")
    print("   - Evening Slot: 3:00 PM - 7:00 PM")
    print("   - Doctors can set availability for next 7 days")
    print("="*60)
