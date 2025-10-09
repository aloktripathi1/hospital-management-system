from celery import Celery
from datetime import datetime, date, timedelta
import csv
from database import db
from models import User, Patient, Doctor, Appointment, Treatment

celery = Celery('hospital_management')

def send_reminder(patient, doctor, time):
    print(f"Reminder sent to {patient}: Appointment with Dr. {doctor} at {time}")

def send_report(doctor, data):
    print(f"Monthly report sent to Dr. {doctor}")
    print(f"Report contains: {data}")

def create_csv(patient, data):
    print(f"CSV file created for {patient}")
    print(f"Contains {len(data)} records")

@celery.task
def send_daily_reminders():
    today = date.today()
    
    appointments = Appointment.query.filter_by(
        appointment_date=today,
        status='booked'
    ).all()
    
    count = 0
    for appt in appointments:
        if appt.patient:
            send_reminder(appt.patient.name, appt.doctor.name, appt.appointment_time)
            count += 1
    
    return f"Sent {count} reminders for {today}"

@celery.task
def generate_monthly_report():
    now = datetime.now()
    
    doctors = Doctor.query.filter_by(is_active=True).all()
    count = 0
    
    for doc in doctors:
        appt_count = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.status == 'completed'
        ).count()
        
        data = f"Total appointments: {appt_count}"
        
        send_report(doc.name, data)
        count += 1
    
    return f"Generated {count} reports for {now.strftime('%B %Y')}"

def make_report_html(doc, appts, treatments, month, year):
    html = f"""
    <html>
    <head>
        <title>Monthly Report - {doc.name}</title>
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
        <p>Unique Patients: {len(set([a.patient_id for a in appts]))}</p>
        
        <h3>Recent Appointments</h3>
        <table>
            <tr>
                <th>Date</th>
                <th>Patient</th>
                <th>Time</th>
                <th>Status</th>
            </tr>
    """
    
    for a in appts[:10]:
        html += f"""
            <tr>
                <td>{a.appointment_date}</td>
                <td>{a.patient.name if a.patient else 'N/A'}</td>
                <td>{a.appointment_time}</td>
                <td>{a.status}</td>
            </tr>
        """
    
    html += """
        </table>
        
        <h3>Recent Treatments</h3>
        <table>
            <tr>
                <th>Date</th>
                <th>Patient</th>
                <th>Visit Type</th>
                <th>Diagnosis</th>
            </tr>
    """
    
    for t in treatments[:10]:
        html += f"""
            <tr>
                <td>{t.created_at.strftime('%Y-%m-%d')}</td>
                <td>{t.appointment.patient.name if t.appointment and t.appointment.patient else 'N/A'}</td>
                <td>{t.visit_type}</td>
                <td>{t.diagnosis[:50] if t.diagnosis else 'N/A'}...</td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    
    return html

@celery.task
def export_patient_history_csv(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        print(f"Patient {patient_id} not found")
        return f"Patient {patient_id} not found"
    
    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient_id
    ).all()
    
    filename = f"patient_{patient_id}_history.csv"
    
    with open(filename, 'w') as f:
        f.write("Patient ID,Patient Name,Doctor Name,Date,Diagnosis,Prescription,Notes\n")
        
        for t in treatments:
            doctor = t.appointment.doctor.name if t.appointment.doctor else 'N/A'
            date = str(t.appointment.appointment_date) if t.appointment else 'N/A'
            
            line = f"{patient.id},{patient.name},{doctor},{date},{t.diagnosis},{t.prescription},{t.treatment_notes}\n"
            f.write(line)
    
    print(f"CSV file created: {filename} for patient {patient.name}")
    print(f"Total treatments exported: {len(treatments)}")
    
    return f"CSV exported for {patient.name}: {len(treatments)} records"

from celery.schedules import crontab

celery.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.celery_tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
    'monthly-reports': {
        'task': 'tasks.celery_tasks.generate_monthly_report',
        'schedule': crontab(0, 0, day_of_month=1),
    },
}