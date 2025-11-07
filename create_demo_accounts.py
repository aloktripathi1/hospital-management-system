#!/usr/bin/env python3
"""
Script to create demo doctor and patient accounts for email demonstration
"""

import sys
sys.path.insert(0, '/workspaces/hospital-management-system/backend')

from app import app
from database import db
from models import User, Doctor, Patient
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_demo_accounts():
    """Create demo doctor and patient accounts with real Gmail"""
    with app.app_context():
        print("\n" + "="*60)
        print("Creating Demo Accounts for Email Demonstration")
        print("="*60 + "\n")
        
        # Get email addresses from user
        print("Enter email addresses that will receive demonstration emails:\n")
        
        doctor_email = input("Enter Doctor's Gmail address: ").strip()
        patient_email = input("Enter Patient's Gmail address: ").strip()
        
        if not doctor_email or not patient_email:
            print("\n❌ Both email addresses are required!")
            return
        
        # Create Doctor Account
        print(f"\n📧 Creating doctor account with email: {doctor_email}")
        
        # Check if doctor user already exists
        existing_doc_user = User.query.filter_by(username='demo_doctor').first()
        if existing_doc_user:
            print("⚠ Doctor user 'demo_doctor' already exists. Updating email...")
            existing_doc_user.email = doctor_email
            doc_user = existing_doc_user
        else:
            doc_user = User(
                username='demo_doctor',
                email=doctor_email,
                password_hash=generate_password_hash('doctor123'),
                role='doctor',
                is_active=True
            )
            db.session.add(doc_user)
            db.session.flush()
        
        # Check if doctor profile exists
        existing_doc = Doctor.query.filter_by(user_id=doc_user.id).first()
        if existing_doc:
            print("⚠ Doctor profile already exists. Updating...")
            existing_doc.name = "Dr. Demo Kumar"
            existing_doc.email = doctor_email
            existing_doc.specialization = "Cardiology"
            existing_doc.experience = 10
            existing_doc.phone = "9876543210"
            existing_doc.qualification = "MBBS, MD (Cardiology)"
            existing_doc.is_active = True
        else:
            doctor = Doctor(
                user_id=doc_user.id,
                name="Dr. Demo Kumar",
                email=doctor_email,
                specialization="Cardiology",
                experience=10,
                phone="9876543210",
                qualification="MBBS, MD (Cardiology)",
                consultation_fee=500,
                is_active=True
            )
            db.session.add(doctor)
        
        # Create Patient Account
        print(f"📧 Creating patient account with email: {patient_email}")
        
        # Check if patient user already exists
        existing_pat_user = User.query.filter_by(username='demo_patient').first()
        if existing_pat_user:
            print("⚠ Patient user 'demo_patient' already exists. Updating email...")
            existing_pat_user.email = patient_email
            pat_user = existing_pat_user
        else:
            pat_user = User(
                username='demo_patient',
                email=patient_email,
                password_hash=generate_password_hash('patient123'),
                role='patient',
                is_active=True
            )
            db.session.add(pat_user)
            db.session.flush()
        
        # Check if patient profile exists
        existing_pat = Patient.query.filter_by(user_id=pat_user.id).first()
        if existing_pat:
            print("⚠ Patient profile already exists. Updating...")
            existing_pat.name = "Demo Patient"
            existing_pat.phone = "9876543211"
            existing_pat.age = 30
            existing_pat.gender = "Male"
            existing_pat.address = "123 Demo Street, Demo City"
            existing_pat.is_blacklisted = False
        else:
            patient = Patient(
                user_id=pat_user.id,
                name="Demo Patient",
                phone="9876543211",
                age=30,
                gender="Male",
                address="123 Demo Street, Demo City",
                medical_history="No major illnesses",
                emergency_contact="9876543212",
                is_blacklisted=False
            )
            db.session.add(patient)
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ Demo Accounts Created Successfully!")
        print("="*60 + "\n")
        
        print("Doctor Account:")
        print(f"  Username: demo_doctor")
        print(f"  Password: doctor123")
        print(f"  Email: {doctor_email}")
        print(f"  Name: Dr. Demo Kumar")
        print(f"  Specialization: Cardiology")
        print()
        
        print("Patient Account:")
        print(f"  Username: demo_patient")
        print(f"  Password: patient123")
        print(f"  Email: {patient_email}")
        print(f"  Name: Demo Patient")
        print()
        
        print("📧 Email Notifications will be sent to:")
        print(f"  • Doctor monthly reports → {doctor_email}")
        print(f"  • Patient appointment reminders → {patient_email}")
        print(f"  • Patient CSV exports → {patient_email}")
        print()
        
        print("🎯 Next Steps:")
        print("  1. Log in as patient (demo_patient / patient123)")
        print("  2. Book an appointment with Dr. Demo Kumar for TODAY")
        print("  3. Wait 2 minutes - patient will receive appointment reminder email")
        print("  4. Log in as doctor (demo_doctor / doctor123)")
        print("  5. Complete the appointment")
        print("  6. Wait 3 minutes - doctor will receive monthly report email")
        print("  7. As patient, export medical history CSV - email with attachment")
        print()

if __name__ == '__main__':
    create_demo_accounts()
