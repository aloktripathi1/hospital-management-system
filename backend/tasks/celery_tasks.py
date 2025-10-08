from celery import Celery
from datetime import datetime, date, timedelta
import csv
from database import db
from models import User, Patient, Doctor, Appointment, Treatment

celery = Celery('hospital_management')   # initialize celery

# Simple helper functions
def send_reminder(patient_name, doctor_name, time):
    print(f"Reminder sent to {patient_name}: Appointment with Dr. {doctor_name} at {time}")

def send_report(doctor_name, report_data):
    print(f"Monthly report sent to Dr. {doctor_name}")
    print(f"Report contains: {report_data}")

def create_csv_file(patient_name, data):
    print(f"CSV file created for {patient_name}")
    print(f"Contains {len(data)} records")

# Daily reminder task - simple student code
@celery.task
def send_daily_reminders():
    today = date.today()
    
    # Get today's appointments
    appointments = Appointment.query.filter_by(
        appointment_date=today,
        status='booked'
    ).all()
    
    count = 0
    for appt in appointments:
        if appt.patient:
            # Send simple reminder
            send_reminder(appt.patient.name, appt.doctor.name, appt.appointment_time)
            count += 1
    
    return f"Sent {count} reminders for {today}"

# Monthly report task - basic student code
@celery.task
def generate_monthly_report():
    now = datetime.now()
    
    doctors = Doctor.query.filter_by(is_active=True).all()
    count = 0
    
    for doc in doctors:
        # Count this month's appointments
        appointments_count = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.status == 'completed'
        ).count()
        
        # Create simple report data
        report_data = f"Total appointments: {appointments_count}"
        
        # Send report
        send_report(doc.name, report_data)
        count += 1
    
    return f"Generated {count} reports for {now.strftime('%B %Y')}"

# ----------- Make HTML Report -----------
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
    
    # Show last 10 appointments
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
    
    # Show last 10 treatments
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

# ----------- Export Patient History -----------
@celery.task
def export_patient_history_csv(pt_id):
    pt = Patient.query.get(pt_id)
    if not pt:
        print(f"Patient {pt_id} not found")
        return f"Patient {pt_id} not found"
    
    # Get patient treatments
    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == pt_id
    ).all()
    
    # Simple CSV creation
    filename = f"patient_{pt_id}_history.csv"
    
    # Create basic CSV file
    with open(filename, 'w') as f:
        # Write header
        f.write("Patient ID,Patient Name,Doctor Name,Date,Symptoms,Diagnosis\n")
        
        # Write data
        for t in treatments:
            doctor_name = t.appointment.doctor.name if t.appointment.doctor else 'N/A'
            date = str(t.appointment.appointment_date) if t.appointment else 'N/A'
            
            # Simple CSV line
            line = f"{pt.id},{pt.name},{doctor_name},{date},{t.symptoms},{t.diagnosis}\n"
            f.write(line)
    
    # Simple notification
    print(f"CSV file created: {filename} for patient {pt.name}")
    print(f"Total treatments exported: {len(treatments)}")
    
    return f"CSV exported for {pt.name}: {len(treatments)} records"

# ----------- Schedule Tasks -----------
from celery.schedules import crontab

celery.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.celery_tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),  # 8 AM daily
    },
    'monthly-reports': {
        'task': 'tasks.celery_tasks.generate_monthly_report',
        'schedule': crontab(0, 0, day_of_month=1),  # 1st of month at midnight
    },
}