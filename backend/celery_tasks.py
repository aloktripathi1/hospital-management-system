from celery import Celery
from datetime import datetime, date, timedelta
from flask_mail import Message
from dotenv import load_dotenv
from database import db
from models import Patient, Doctor, Appointment, Treatment
import os
import csv

load_dotenv()

celery = Celery('hospital_management')
celery.conf.broker_url = 'redis://localhost:6379/0'
celery.conf.result_backend = 'redis://localhost:6379/0'
celery.conf.broker_connection_retry_on_startup = True


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # daily reminder every 2 minutes
    sender.add_periodic_task(120.0, send_daily_reminders.s())
    # monthly report every 3 minutes
    sender.add_periodic_task(180.0, generate_monthly_report.s())

# daily reminder task
@celery.task
def send_daily_reminders():
    from app import app, mail
    with app.app_context():
        today = date.today()
        appts = Appointment.query.filter_by(appointment_date=today, status='booked').all()
        for appt in appts:
            if not (appt.patient and appt.patient.user and appt.doctor):
                continue
            patient_email = appt.patient.user.email
            patient_name = appt.patient.name
            doctor_name = appt.doctor.name
            appointment_time = appt.appointment_time
            html = f"""<html><body>
            <h2>Appointment Reminder</h2>
            <p>Hi {patient_name},</p>
            <p>You have an appointment today with Dr. {doctor_name} at {appointment_time}.</p>
            <p>Please arrive 10 minutes early.</p>
            </body></html>"""
            msg = Message(subject=f"Appointment Reminder - {today}", recipients=[patient_email])
            msg.html = html
            mail.send(msg)
        return f"Sent {len(appts)} reminders for {today}"

# monthly report task
@celery.task
def generate_monthly_report():
    from app import app, mail
    with app.app_context():
        now = datetime.now()
        first_day_current = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_current = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        docs = Doctor.query.filter_by(is_active=True).all()
        sent = 0
        for doc in docs:
            if not doc.user:
                continue
            appts = Appointment.query.filter(
                Appointment.doctor_id == doc.id,
                Appointment.appointment_date >= first_day_current.date(),
                Appointment.appointment_date <= last_day_current.date(),
                Appointment.status == 'completed'
            ).all()
            treatments = Treatment.query.join(Appointment).filter(
                Appointment.doctor_id == doc.id,
                Treatment.created_at >= first_day_current,
                Treatment.created_at <= last_day_current
            ).all()

            # html report
            html = f"""<html><body>
            <h2>Monthly Activity Report</h2>
            <p>Dr. {doc.name} - {doc.specialization}</p>
            <p>Period: {first_day_current.strftime('%B %Y')} (Current Month - Demo Mode)</p>
            <p>Total appointments: {len(appts)}</p>
            <p>Total treatments: {len(treatments)}</p>
            <h3>recent appointments</h3>
            <table border="1" cellpadding="4"><tr><th>date</th><th>patient</th><th>time</th></tr>"""
            for a in appts[:10]:
                pname = a.patient.name if a.patient else 'N/A'
                html += f"<tr><td>{a.appointment_date}</td><td>{pname}</td><td>{a.appointment_time}</td></tr>"
            html += "</table></body></html>"

            doctor_email = doc.user.email
            msg = Message(subject=f"Monthly Activity Report - {first_day_current.strftime('%B %Y')}", recipients=[doctor_email])
            msg.html = html
            mail.send(msg)
            sent += 1
        return f"Sent {sent} monthly reports for {first_day_current.strftime('%B %Y')}"

# export patient history csv
@celery.task
def export_patient_history_csv(patient_id):
    from app import app, mail
    with app.app_context():
        patient = Patient.query.get(patient_id)
        if not patient or not patient.user:
            return f"Patient {patient_id} not found or has no user account"

        treatments = Treatment.query.join(Appointment).filter(
            Appointment.patient_id == patient_id
        ).order_by(Treatment.created_at.desc()).all()

        exports_dir = os.path.join(os.path.dirname(__file__), 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"patient_{patient_id}_history_{timestamp}.csv"
        filepath = os.path.join(exports_dir, filename)

        # write csv file
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['date', 'doctor', 'diagnosis', 'treatment_notes'])
            for t in treatments:
                doctor_name = t.appointment.doctor.name if t.appointment and t.appointment.doctor else 'N/A'
                appt_date = str(t.appointment.appointment_date) if t.appointment else 'N/A'
                writer.writerow([appt_date, doctor_name, t.diagnosis or 'N/A', t.treatment_notes or 'N/A'])

        # send email with attachment
        patient_email = patient.user.email
        html = f"""<html><body><h2>Medical History Export</h2><p>Hi {patient.name},</p><p>Your medical history export is attached.</p></body></html>"""
        msg = Message(subject='Your Medical History Export is Ready', recipients=[patient_email])
        msg.html = html
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        msg.attach(filename, 'text/csv', content)
        mail.send(msg)
        return f"Exported {len(treatments)} records to {filename} and emailed to {patient_email}"

