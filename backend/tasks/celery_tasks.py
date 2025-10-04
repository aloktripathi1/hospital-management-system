from celery import Celery
from datetime import datetime, date, timedelta
import csv
import io
from database import db
from models import User, Patient, Doctor, Appointment, Treatment

# ----------- Initialize Celery -----------
celery = Celery('hospital_management')

# ----------- Send Daily Reminders -----------
@celery.task
def send_daily_reminders():
    today = date.today()
    
    # Get today's appointments
    appts = Appointment.query.filter_by(
        appointment_date=today,
        status='booked'
    ).all()
    
    count = 0
    for appt in appts:
        if appt.patient and appt.patient.user:
            # Just log the reminder (in real app, send email/SMS/gchat webhook)
            print(f"Reminder: {appt.patient.name} has appointment with {appt.doctor.name} at {appt.appointment_time}")
            count += 1
    
    return f"Sent {count} reminders for {today}"

# ----------- Generate Monthly Report -----------
@celery.task
def generate_monthly_report():
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    docs = Doctor.query.filter_by(is_active=True).all()
    count = 0
    
    for doc in docs:
        # Get this month's appointments
        appts = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.appointment_date >= month_start,
            Appointment.status == 'completed'
        ).all()
        
        # Get this month's treatments
        treatments = Treatment.query.join(Appointment).filter(
            Appointment.doctor_id == doc.id,
            Treatment.created_at >= month_start
        ).all()
        
        # Generate HTML report
        html = make_report_html(doc, appts, treatments, now.month, now.year)
        
        # Just log (in real app, send email with HTML)
        print(f"Report generated for {doc.name}: {len(appts)} appointments, {len(treatments)} treatments")
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
        return f"Patient {pt_id} not found"
    
    # Get all treatments
    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == pt_id
    ).order_by(Treatment.created_at.desc()).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Patient ID', 'Patient Name', 'Doctor Name', 'Appointment Date', 
        'Visit Type', 'Symptoms', 'Diagnosis', 'Prescription', 'Treatment Notes', 'Next Visit'
    ])
    
    # Data rows
    for t in treatments:
        writer.writerow([
            pt.id,
            pt.name,
            t.appointment.doctor.name if t.appointment.doctor else 'N/A',
            t.appointment.appointment_date if t.appointment else 'N/A',
            t.visit_type,
            t.symptoms,
            t.diagnosis,
            t.prescription,
            t.treatment_notes,
            t.follow_up_date if hasattr(t, 'follow_up_date') else 'N/A'
        ])
    
    csv_data = output.getvalue()
    output.close()
    
    # Just log (in real app, save file and send notification)
    print(f"CSV exported for {pt.name}: {len(treatments)} records")
    
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