#!/usr/bin/env python3
"""
Manual trigger script for demonstrating Celery tasks during viva/presentation
Usage: python trigger_tasks.py
"""

import sys
sys.path.insert(0, '/workspaces/hospital-management-system/backend')

from app import app
from celery_tasks import send_daily_reminders, generate_monthly_report, export_patient_history_csv

def main():
    print("\n" + "="*60)
    print("🏥 Hospital Management System - Task Trigger Demo")
    print("="*60 + "\n")
    
    with app.app_context():
        print("Available Tasks:")
        print("1. Send Daily Reminders (for today's appointments)")
        print("2. Generate Monthly Report (for all doctors)")
        print("3. Export Patient History CSV (requires patient ID)")
        print("0. Exit")
        print()
        
        choice = input("Enter your choice (0-3): ").strip()
        
        if choice == '1':
            print("\n📧 Triggering Daily Reminders...")
            result = send_daily_reminders.delay()
            print(f"✅ Task queued! Task ID: {result.id}")
            print("⏳ Check Celery worker logs and MailHog (http://localhost:8025)")
            print()
            
        elif choice == '2':
            print("\n📊 Triggering Monthly Report Generation...")
            result = generate_monthly_report.delay()
            print(f"✅ Task queued! Task ID: {result.id}")
            print("⏳ Check Celery worker logs and MailHog (http://localhost:8025)")
            print()
            
        elif choice == '3':
            patient_id = input("\nEnter Patient ID: ").strip()
            try:
                patient_id = int(patient_id)
                print(f"\n📄 Triggering CSV Export for Patient ID {patient_id}...")
                result = export_patient_history_csv.delay(patient_id)
                print(f"✅ Task queued! Task ID: {result.id}")
                print("⏳ Check Celery worker logs and MailHog (http://localhost:8025)")
                print(f"📁 CSV file will be saved to: backend/exports/")
                print()
            except ValueError:
                print("❌ Invalid Patient ID! Must be a number.")
                
        elif choice == '0':
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice!")
        
        print("\n" + "="*60)
        print("💡 Tips for Viva:")
        print("   1. Open http://localhost:8025 in browser")
        print("   2. Run this script to trigger tasks")
        print("   3. Refresh MailHog page to see emails")
        print("   4. Show CSV file from backend/exports/ folder")
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
