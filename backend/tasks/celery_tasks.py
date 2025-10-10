from celery import Celery
from datetime import datetime, date, timedelta
from database import db
from models import User, Patient, Doctor, Appointment, Treatment

celery = Celery('hospital_management')

# ==================== DAILY REMINDERS ====================

@celery.task
def send_daily_reminders():
    today = date.today()
    
    # Get all booked appointments for today
    appts = Appointment.query.filter_by(appointment_date=today, status='booked').all()
    
    count = 0
    for appt in appts:
        if appt.patient and appt.doctor:
            # Send reminder (print for demo - can be email/SMS/webhook in production)
            msg = f"Reminder: Hi {appt.patient.name}, you have an appointment today at {appt.appointment_time} with Dr. {appt.doctor.name}. Please be on time!"
            print(msg)
            count += 1
    
    return f"Sent {count} reminders for {today}"

# ==================== MONTHLY REPORTS ====================

@celery.task
def generate_monthly_report():
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
        
        # Generate HTML report
        html = make_html_report(doc, appts, treatments, now.month, now.year)
        
        # Send report (print for demo - can be emailed in production)
        print(f"\n{'='*60}")
        print(f"Monthly Report for Dr. {doc.name}")
        print(f"{'='*60}")
        print(html)
        print(f"{'='*60}\n")
        
        count += 1
    
    return f"Generated {count} reports for {now.strftime('%B %Y')}"

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
    patient = Patient.query.get(patient_id)
    if not patient:
        return f"Patient {patient_id} not found"
    
    # Get all treatments for this patient
    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient_id
    ).order_by(Treatment.created_at.desc()).all()
    
    # Create CSV filename
    filename = f"patient_{patient_id}_history.csv"
    
    # Write CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        # Write header with all required fields
        f.write("Patient ID,Patient Name,Doctor Name,Appointment Date,Visit Type,Symptoms,Diagnosis,Treatment Given,Prescription,Notes,Next Visit\n")
        
        # Write data rows
        for t in treatments:
            # Get doctor name
            if t.appointment and t.appointment.doctor:
                doctor = t.appointment.doctor.name
            else:
                doctor = 'N/A'
            
            # Get appointment date
            if t.appointment:
                appt_date = str(t.appointment.appointment_date)
            else:
                appt_date = 'N/A'
            
            # Get fields (handle None values)
            visit_type = t.visit_type or 'N/A'
            symptoms = t.symptoms or 'N/A'
            diagnosis = t.diagnosis or 'N/A'
            treatment = t.treatment_notes or 'N/A'
            prescription = t.prescription or 'N/A'
            notes = t.treatment_notes or 'N/A'
            
            # Next visit - can add this field to Treatment model if needed
            next_visit = 'N/A'  # Default value
            
            # Clean data (remove commas and newlines)
            symptoms = symptoms.replace(',', ';').replace('\n', ' ')
            diagnosis = diagnosis.replace(',', ';').replace('\n', ' ')
            treatment = treatment.replace(',', ';').replace('\n', ' ')
            prescription = prescription.replace(',', ';').replace('\n', ' ')
            notes = notes.replace(',', ';').replace('\n', ' ')
            
            # Write row
            row = f"{patient.id},{patient.name},{doctor},{appt_date},{visit_type},{symptoms},{diagnosis},{treatment},{prescription},{notes},{next_visit}\n"
            f.write(row)
    
    # Print confirmation (in production, send notification to patient)
    print(f"\n{'='*60}")
    print(f"CSV Export Complete!")
    print(f"Patient: {patient.name}")
    print(f"File: {filename}")
    print(f"Total Records: {len(treatments)}")
    print(f"{'='*60}\n")
    
    return f"CSV exported for {patient.name}: {len(treatments)} records"

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