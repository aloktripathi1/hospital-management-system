from celery import Celery
from datetime import datetime, date, timedelta
from database import db
from models import User, Patient, Doctor, Appointment, Treatment
import os

celery = Celery('hospital_management')

# daily reminder

@celery.task
def send_daily_reminders():
    today = date.today()
    
    # Get all booked appointments for today
    appts = Appointment.query.filter_by(appointment_date=today, status='booked').all()
    
    count = 0
    for appt in appts:
        if appt.patient and appt.doctor:
            # Simple reminder message
            patient_name = appt.patient.name
            doctor_name = appt.doctor.name
            appointment_time = appt.appointment_time
            
            # Create reminder message
            message = f"""
            ========================================
            APPOINTMENT REMINDER
            ========================================
            Hi {patient_name},
            
            This is a reminder that you have an appointment scheduled for TODAY:
            
            Doctor: Dr. {doctor_name}
            Time: {appointment_time}
            Date: {today}
            
            Please arrive 10 minutes early.
            ========================================
            """
            
            # For now, we print the message
            # In production, you can send via:
            # - Email using SMTP
            # - SMS using Twilio/AWS SNS
            # - Google Chat webhook
            print(message)
            count += 1
    
    return f"✅ Sent {count} daily reminders for {today}"

# ==================== MONTHLY REPORTS ====================

@celery.task
def generate_monthly_report():
    """
    Simple monthly report generator - runs on 1st of every month
    Creates HTML report for each doctor with their monthly activity
    """
    now = datetime.now()
    
    # Get start of current month
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    docs = Doctor.query.filter_by(is_active=True).all()
    count = 0
    
    for doc in docs:
        # Get THIS MONTH's completed appointments
        appts = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.appointment_date >= month_start,
            Appointment.status == 'completed'
        ).all()
        
        # Get THIS MONTH's treatments
        treatments = Treatment.query.join(Appointment).filter(
            Appointment.doctor_id == doc.id,
            Treatment.created_at >= month_start
        ).all()
        
        # Generate simple HTML report
        html = make_html_report(doc, appts, treatments, now.month, now.year)
        
        # Print report (in production, send via email)
        print(f"\n{'='*70}")
        print(f"MONTHLY ACTIVITY REPORT - Dr. {doc.name}")
        print(f"Report Period: {now.strftime('%B %Y')}")
        print(f"{'='*70}\n")
        print(html)
        print(f"\n{'='*70}\n")
        
        # TODO: Send email to doctor
        # send_email(to=doc.email, subject=f"Monthly Report - {now.strftime('%B %Y')}", html=html)
        
        count += 1
    
    return f"✅ Generated {count} monthly reports for {now.strftime('%B %Y')}"

def make_html_report(doc, appts, treatments, month, year):
    # Calculate unique patients
    unique_patients = len(set([a.patient_id for a in appts if a.patient_id]))
    
    html = f"""
    <html>
    <head>
        <title>Monthly Report - Dr. {doc.name}</title>
        <style>
            body {{ font-family: Arial; margin: 20px; }}
            h1 {{ color: #007bff; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Monthly Activity Report</h1>
        <h2>Dr. {doc.name} - {doc.specialization}</h2>
        <p>Report for {month}/{year}</p>
        
        <h3>Summary</h3>
        <p>Total Appointments: {len(appts)}</p>
        <p>Total Treatments: {len(treatments)}</p>
        <p>Unique Patients: {unique_patients}</p>
        
        <h3>Appointments This Month</h3>
        <table>
            <tr>
                <th>Date</th>
                <th>Patient</th>
                <th>Time</th>
                <th>Status</th>
            </tr>
    """
    
    # Add appointment rows (show last 10)
    for a in appts[:10]:
        patient_name = a.patient.name if a.patient else 'N/A'
        html += f"""
            <tr>
                <td>{a.appointment_date}</td>
                <td>{patient_name}</td>
                <td>{a.appointment_time}</td>
                <td>{a.status}</td>
            </tr>
        """
    
    html += """
        </table>
        
        <h3>Treatments Provided</h3>
        <table>
            <tr>
                <th>Date</th>
                <th>Patient</th>
                <th>Visit Type</th>
                <th>Diagnosis</th>
                <th>Treatment</th>
            </tr>
    """
    
    # Add treatment rows (show last 10)
    for t in treatments[:10]:
        patient_name = 'N/A'
        if t.appointment and t.appointment.patient:
            patient_name = t.appointment.patient.name
        
        diagnosis = t.diagnosis[:50] if t.diagnosis else 'N/A'
        treatment = t.treatment_notes[:50] if t.treatment_notes else 'N/A'
        
        html += f"""
            <tr>
                <td>{t.created_at.strftime('%Y-%m-%d')}</td>
                <td>{patient_name}</td>
                <td>{t.visit_type or 'N/A'}</td>
                <td>{diagnosis}</td>
                <td>{treatment}</td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    
    return html

# ==================== CSV EXPORT ====================

@celery.task
def export_patient_history_csv(patient_id):
    """
    Simple async CSV export task - triggered by patient
    Exports all treatment history to CSV file
    """
    patient = Patient.query.get(patient_id)
    if not patient:
        return f"❌ Patient {patient_id} not found"
    
    # Get all treatments for this patient
    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient_id
    ).order_by(Treatment.created_at.desc()).all()
    
    # Create simple CSV filename
    filename = f"patient_{patient_id}_history_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = os.path.join('exports', filename)
    
    # Create exports directory if it doesn't exist
    os.makedirs('exports', exist_ok=True)
    
    # Write CSV file with all patient treatment history
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        # Simple CSV header
        f.write("Patient ID,Patient Name,Doctor Name,Appointment Date,Visit Type,Symptoms,Diagnosis,Treatment,Prescription,Notes,Next Visit\n")
        
        # Write each treatment record
        for t in treatments:
            # Get doctor name
            doctor = t.appointment.doctor.name if t.appointment and t.appointment.doctor else 'N/A'
            
            # Get appointment date
            appt_date = str(t.appointment.appointment_date) if t.appointment else 'N/A'
            
            # Clean data (replace commas and newlines to keep CSV format clean)
            visit_type = (t.visit_type or 'N/A').replace(',', ';').replace('\n', ' ')
            symptoms = (t.symptoms or 'N/A').replace(',', ';').replace('\n', ' ')
            diagnosis = (t.diagnosis or 'N/A').replace(',', ';').replace('\n', ' ')
            treatment = (t.treatment_notes or 'N/A').replace(',', ';').replace('\n', ' ')
            prescription = (t.prescription or 'N/A').replace(',', ';').replace('\n', ' ')
            notes = (t.treatment_notes or 'N/A').replace(',', ';').replace('\n', ' ')
            next_visit = 'N/A'  # Can be added to Treatment model if needed
            
            # Write CSV row
            row = f"{patient.id},{patient.name},{doctor},{appt_date},{visit_type},{symptoms},{diagnosis},{treatment},{prescription},{notes},{next_visit}\n"
            f.write(row)
    
    # Print completion message
    print(f"\n{'='*70}")
    print(f"✅ CSV EXPORT COMPLETED")
    print(f"Patient: {patient.name} (ID: {patient.id})")
    print(f"File: {filepath}")
    print(f"Records: {len(treatments)}")
    print(f"{'='*70}\n")
    
    # TODO: Notify patient (via email or in-app notification)
    # send_notification(patient_id, f"Your medical history export is ready: {filename}")
    
    return f"✅ CSV exported for {patient.name}: {len(treatments)} records saved to {filename}"

# ==================== CELERY SCHEDULE ====================

from celery.schedules import crontab

celery.conf.beat_schedule = {
    # Run daily at 8 AM
    'send-daily-reminders': {
        'task': 'tasks.celery_tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
    # Run on 1st of every month at midnight
    'generate-monthly-reports': {
        'task': 'tasks.celery_tasks.generate_monthly_report',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),
    },
}

