from celery import Celery
from celery.schedules import crontab
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
    # daily reminder at 7:30 AM every day
    sender.add_periodic_task(
        crontab(hour=7, minute=30),
        send_daily_reminders.s()
    )
    # monthly report on the 1st of every month at 8:00 AM
    sender.add_periodic_task(
        crontab(day_of_month=1, hour=8, minute=0),
        generate_monthly_report.s()
    )

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
            
            content = f"""
                <p>Hi {patient_name},</p>
                <p>You have an appointment today with <strong>Dr. {doctor_name}</strong> at <strong>{appointment_time}</strong>.</p>
                <p>Please arrive 10 minutes early to complete any necessary paperwork.</p>
            """
            html = get_email_template("Appointment Reminder", content)
            
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
            content = f"""
                <p><strong>Dr. {doc.name}</strong> - {doc.specialization}</p>
                <p>Period: {first_day_current.strftime('%B %Y')}</p>
                
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Total Appointments:</strong> {len(appts)}</p>
                    <p style="margin: 5px 0;"><strong>Total Treatments:</strong> {len(treatments)}</p>
                </div>

                <h3>Recent Appointments</h3>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Patient</th>
                        <th>Time</th>
                    </tr>"""
            for a in appts[:10]:
                pname = a.patient.name if a.patient else 'N/A'
                content += f"<tr><td>{a.appointment_date}</td><td>{pname}</td><td>{a.appointment_time}</td></tr>"
            content += "</table>"
            
            html = get_email_template("Monthly Activity Report", content)

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
            writer.writerow(['Sr. No', 'Date', 'Doctor', 'Visit Type', 'Diagnosis', 'Medicines', 'Treatment Notes'])
            for idx, t in enumerate(treatments, 1):
                doctor_name = t.appointment.doctor.name if t.appointment and t.appointment.doctor else 'N/A'
                appt_date = str(t.appointment.appointment_date) if t.appointment else 'N/A'
                visit_type = t.visit_type or 'General'
                diagnosis = t.diagnosis or 'N/A'
                medicines = t.prescription or 'N/A'
                notes = t.treatment_notes or 'N/A'
                writer.writerow([idx, appt_date, doctor_name, visit_type, diagnosis, medicines, notes])

        # send email with attachment
        patient_email = patient.user.email
        
        content = f"""
            <p>Hi {patient.name},</p>
            <p>Your medical history export has been generated successfully.</p>
            <p>Please find the attached CSV file containing your complete medical records.</p>
            <p>If you did not request this export, please contact support immediately.</p>
        """
        html = get_email_template("Medical History Export", content)
        
        msg = Message(subject='Your Medical History Export is Ready', recipients=[patient_email])
        msg.html = html
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        msg.attach(filename, 'text/csv', content)
        mail.send(msg)
        return f"Exported {len(treatments)} records to {filename} and emailed to {patient_email}"

def get_email_template(title, content):
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .header {{ background: #2c3e50; color: #fff; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; color: #333; line-height: 1.6; }}
            .footer {{ background: #eee; padding: 10px; text-align: center; font-size: 12px; color: #777; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>{title}</h2>
            </div>
            <div class="content">
                {content}
                <p style="margin-top: 30px;">Regards,<br>MediHub Support Team</p>
            </div>
            <div class="footer">
                <p>&copy; MediHub</p>
            </div>
        </div>
    </body>
    </html>
    """

