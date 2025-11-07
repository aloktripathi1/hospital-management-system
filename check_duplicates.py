#!/usr/bin/env python3
"""
Script to check for duplicate treatments and fix database issues
"""

import sys
sys.path.insert(0, '/workspaces/hospital-management-system/backend')

from app import app
from database import db
from models import Treatment, Appointment, Patient, Doctor
from sqlalchemy import func

def check_duplicate_treatments():
    """Check for duplicate treatment records"""
    with app.app_context():
        print("\n" + "="*60)
        print("Checking for Duplicate Treatments")
        print("="*60 + "\n")
        
        # Find appointments with multiple treatments
        duplicates = db.session.query(
            Treatment.appointment_id, 
            func.count(Treatment.id).label('count')
        ).group_by(Treatment.appointment_id).having(func.count(Treatment.id) > 1).all()
        
        if not duplicates:
            print("✓ No duplicate treatments found!")
            return
        
        print(f"⚠ Found {len(duplicates)} appointments with duplicate treatments:\n")
        
        for appt_id, count in duplicates:
            appointment = Appointment.query.get(appt_id)
            treatments = Treatment.query.filter_by(appointment_id=appt_id).all()
            
            print(f"Appointment ID: {appt_id}")
            print(f"  Patient: {appointment.patient.name if appointment.patient else 'N/A'}")
            print(f"  Doctor: Dr. {appointment.doctor.name if appointment.doctor else 'N/A'}")
            print(f"  Date: {appointment.appointment_date}")
            print(f"  Duplicate Treatments: {count}")
            
            for i, t in enumerate(treatments, 1):
                print(f"    Treatment {i}: ID={t.id}, Created={t.created_at}, Diagnosis={t.diagnosis[:30] if t.diagnosis else 'N/A'}")
            print()

def remove_duplicate_treatments():
    """Remove duplicate treatments, keeping only the latest one"""
    with app.app_context():
        print("\n" + "="*60)
        print("Removing Duplicate Treatments")
        print("="*60 + "\n")
        
        duplicates = db.session.query(
            Treatment.appointment_id, 
            func.count(Treatment.id).label('count')
        ).group_by(Treatment.appointment_id).having(func.count(Treatment.id) > 1).all()
        
        if not duplicates:
            print("✓ No duplicates to remove!")
            return
        
        removed_count = 0
        for appt_id, count in duplicates:
            treatments = Treatment.query.filter_by(appointment_id=appt_id).order_by(Treatment.created_at.desc()).all()
            
            # Keep the most recent, delete the rest
            keep = treatments[0]
            to_delete = treatments[1:]
            
            print(f"Appointment {appt_id}: Keeping treatment {keep.id}, removing {len(to_delete)} duplicates")
            
            for t in to_delete:
                db.session.delete(t)
                removed_count += 1
        
        db.session.commit()
        print(f"\n✓ Removed {removed_count} duplicate treatments!")

def show_patient_history(patient_id):
    """Show patient history to verify no duplicates"""
    with app.app_context():
        patient = Patient.query.get(patient_id)
        if not patient:
            print(f"Patient {patient_id} not found")
            return
        
        print("\n" + "="*60)
        print(f"Patient History: {patient.name}")
        print("="*60 + "\n")
        
        treatments = db.session.query(Treatment).join(Appointment).filter(
            Appointment.patient_id == patient_id
        ).order_by(Treatment.created_at.desc()).all()
        
        print(f"Total treatments: {len(treatments)}\n")
        
        for i, t in enumerate(treatments, 1):
            appt = t.appointment
            print(f"{i}. Treatment ID: {t.id}")
            print(f"   Appointment ID: {appt.id}")
            print(f"   Date: {appt.appointment_date}")
            print(f"   Doctor: Dr. {appt.doctor.name if appt.doctor else 'N/A'}")
            print(f"   Diagnosis: {t.diagnosis or 'N/A'}")
            print(f"   Created: {t.created_at}")
            print()

def main():
    print("\n" + "="*60)
    print("Hospital Management System - Database Check Tool")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Check for duplicate treatments")
        print("2. Remove duplicate treatments")
        print("3. Show patient history (by ID)")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            check_duplicate_treatments()
        elif choice == '2':
            confirm = input("Are you sure you want to remove duplicates? (yes/no): ").strip().lower()
            if confirm == 'yes':
                remove_duplicate_treatments()
                print("\nRunning check again to verify...")
                check_duplicate_treatments()
        elif choice == '3':
            patient_id = input("Enter patient ID: ").strip()
            try:
                show_patient_history(int(patient_id))
            except ValueError:
                print("Invalid patient ID")
        elif choice == '4':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == '__main__':
    main()
