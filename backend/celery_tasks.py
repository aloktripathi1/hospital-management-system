from celery import Celery
from celery.schedules import crontab
from datetime import datetime, date
from flask_mail import Mail, Message
from dotenv import load_dotenv
from database import db
from models import Patient, Doctor, Appointment, Treatment
import os

load_dotenv()

celery = Celery('hospital_management')

celery.conf.broker_url = 'redis://localhost:6379/0'
celery.conf.result_backend = 'redis://localhost:6379/0'
celery.conf.broker_connection_retry_on_startup = True

def send_email(subject, recipient, html_body):
    from app import app, mail
    
    with app.app_context():
        msg = Message(subject=subject, recipients=[recipient], html=html_body)
        mail.send(msg)
        print(f"Email sent to {recipient}: {subject}")

@celery.task
def send_daily_reminders():
    from app import app
    
    with app.app_context():
        today = date.today()
        appts = Appointment.query.filter_by(appointment_date=today, status='booked').all()
        
        count = 0
        for appt in appts:
            if appt.patient and appt.doctor and appt.patient.user:
                patient_email = appt.patient.user.email
                patient_name = appt.patient.name
                doctor_name = appt.doctor.name
                appointment_time = appt.appointment_time
                
                html = f"""
                <html>
                <body style="font-family: Arial; padding: 20px;">
                    <h2 style="color: #007bff;">Appointment Reminder</h2>
                    <p>Hi <strong>{patient_name}</strong>,</p>
                    <p>This is a reminder that you have an appointment scheduled for TODAY:</p>
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff;">
                        <p><strong>Doctor:</strong> Dr. {doctor_name}</p>
                        <p><strong>Time:</strong> {appointment_time}</p>
                        <p><strong>Date:</strong> {today}</p>
                    </div>
                    <p>Please arrive 10 minutes early.</p>
                    <p>Thank you!</p>
                </body>
                </html>
                """
                
                send_email(f"Appointment Reminder - {today}", patient_email, html)
                count += 1
        
        return f"Sent {count} reminders"

@celery.task
def generate_monthly_report():
    from app import app
    
    with app.app_context():
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        docs = Doctor.query.filter_by(is_active=True).all()
        
        count = 0
        for doc in docs:
            if not doc.user:
                continue
                
            appts = Appointment.query.filter(
                Appointment.doctor_id == doc.id,
                Appointment.appointment_date >= month_start,
                Appointment.status == 'completed'
            ).all()
            
            treatments = Treatment.query.join(Appointment).filter(
                Appointment.doctor_id == doc.id,
                Treatment.created_at >= month_start
            ).all()
            
            html = make_html_report(doc, appts, treatments, now.month, now.year)
            
            doctor_email = doc.user.email
            subject = f"Monthly Activity Report - {now.strftime('%B %Y')}"
            send_email(subject, doctor_email, html)
            
            print(f"Monthly report sent to Dr. {doc.name}")
            count += 1
        
        return f"Generated {count} reports"

def make_html_report(doc, appts, treatments, month, year):
    unique_patients = len(set([a.patient_id for a in appts if a.patient_id]))
    
    html = f"""<html>
<head>
    <style>
        body {{ font-family: Arial; padding: 20px; }}
        h1 {{ color: #007bff; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #007bff; color: white; }}
        .summary {{ background-color: #f8f9fa; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
<h1>Monthly Activity Report</h1>
<h2>Dr. {doc.name} - {doc.specialization}</h2>
<p>Report for {month}/{year}</p>
<div class="summary">
    <p><strong>Total Appointments:</strong> {len(appts)}</p>
    <p><strong>Total Treatments:</strong> {len(treatments)}</p>
    <p><strong>Unique Patients:</strong> {unique_patients}</p>
</div>
<h3>Recent Appointments</h3>
<table>
<tr><th>Date</th><th>Patient</th><th>Time</th></tr>"""
    
    for a in appts[:10]:
        patient_name = a.patient.name if a.patient else 'N/A'
        html += f"<tr><td>{a.appointment_date}</td><td>{patient_name}</td><td>{a.appointment_time}</td></tr>"
    
    html += "</table><h3>Recent Treatments</h3><table><tr><th>Date</th><th>Patient</th><th>Diagnosis</th></tr>"
    
    for t in treatments[:10]:
        patient_name = t.appointment.patient.name if t.appointment and t.appointment.patient else 'N/A'
        diagnosis = (t.diagnosis[:50] if t.diagnosis else 'N/A')
        html += f"<tr><td>{t.created_at.strftime('%Y-%m-%d')}</td><td>{patient_name}</td><td>{diagnosis}</td></tr>"
    
    html += "</table></body></html>"
    return html

@celery.task
def export_patient_history_csv(patient_id):
    from app import app, mail
    from flask_mail import Message
    
    with app.app_context():
        patient = Patient.query.get(patient_id)
        if not patient or not patient.user:
            return f"Patient {patient_id} not found"
        
        treatments = Treatment.query.join(Appointment).filter(
            Appointment.patient_id == patient_id
        ).order_by(Treatment.created_at.desc()).all()
        
        filename = f"patient_{patient_id}_history_{datetime.now().strftime('%Y%m%d')}.csv"
        filepath = os.path.join('exports', filename)
        os.makedirs('exports', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("Date,Doctor,Visit Type,Symptoms,Diagnosis,Treatment,Prescription\n")
            
            for t in treatments:
                doctor = t.appointment.doctor.name if t.appointment and t.appointment.doctor else 'N/A'
                appt_date = str(t.appointment.appointment_date) if t.appointment else 'N/A'
                visit_type = (t.visit_type or 'N/A').replace(',', ';').replace('\n', ' ')
                symptoms = (t.symptoms or 'N/A').replace(',', ';').replace('\n', ' ')
                diagnosis = (t.diagnosis or 'N/A').replace(',', ';').replace('\n', ' ')
                treatment = (t.treatment_notes or 'N/A').replace(',', ';').replace('\n', ' ')
                prescription = (t.prescription or 'N/A').replace(',', ';').replace('\n', ' ')
                
                f.write(f"{appt_date},{doctor},{visit_type},{symptoms},{diagnosis},{treatment},{prescription}\n")
        
        patient_email = patient.user.email
        
        msg = Message(
            subject="Your Medical History Export",
            recipients=[patient_email],
            html=f"""
            <html>
            <body style="font-family: Arial; padding: 20px;">
                <h2 style="color: #007bff;">Medical History Export Ready</h2>
                <p>Hi <strong>{patient.name}</strong>,</p>
                <p>Your medical history export is ready and attached to this email.</p>
                <p><strong>Total Records:</strong> {len(treatments)}</p>
                <p>Please find your complete treatment history in the attached CSV file.</p>
                <p>Thank you!</p>
            </body>
            </html>
            """
        )
        
        with open(filepath, 'r', encoding='utf-8') as f:
            msg.attach(filename, "text/csv", f.read())
        
        mail.send(msg)
        
        print(f"CSV exported and emailed to {patient.name}: {len(treatments)} records")
        return f"Exported {len(treatments)} records to {filename}"

celery.conf.beat_schedule = {
    # DEMO MODE - runs every 2 minutes for testing
    'demo-daily-reminders': {
        'task': 'celery_tasks.send_daily_reminders',
        'schedule': 120.0,  # every 120 seconds (2 minutes)
    },
    # DEMO MODE - runs every 3 minutes for testing
    'demo-monthly-reports': {
        'task': 'celery_tasks.generate_monthly_report',
        'schedule': 180.0,  # every 180 seconds (3 minutes)
    },
    
    # PRODUCTION SCHEDULES (commented out for demo)
    # 'send-daily-reminders': {
    #     'task': 'celery_tasks.send_daily_reminders',
    #     'schedule': crontab(hour=8, minute=0),  # 8 AM daily
    # },
    # 'generate-monthly-reports': {
    #     'task': 'celery_tasks.generate_monthly_report',
    #     'schedule': crontab(hour=0, minute=0, day_of_month=1),  # 1st of month
    # },
}



