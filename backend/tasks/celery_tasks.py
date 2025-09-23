from celery import Celery
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import os

# Initialize Celery
celery = Celery('hospital_management')
celery.config_from_object('backend.config.CeleryConfig')

@celery.task
def send_appointment_reminder(patient_email, patient_name, doctor_name, appointment_date, appointment_time):
    """Send appointment reminder email to patient"""
    try:
        # Email configuration (using Gmail SMTP for demo)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv('HOSPITAL_EMAIL', 'hospital@example.com')
        sender_password = os.getenv('HOSPITAL_EMAIL_PASSWORD', 'password')
        
        # Create message
        message = MimeMultipart()
        message["From"] = sender_email
        message["To"] = patient_email
        message["Subject"] = "Appointment Reminder - Hospital Management System"
        
        body = f"""
        Dear {patient_name},
        
        This is a reminder for your upcoming appointment:
        
        Doctor: {doctor_name}
        Date: {appointment_date}
        Time: {appointment_time}
        
        Please arrive 15 minutes early for check-in.
        
        If you need to reschedule or cancel, please contact us at least 24 hours in advance.
        
        Best regards,
        Hospital Management Team
        """
        
        message.attach(MimeText(body, "plain"))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, patient_email, text)
        server.quit()
        
        return f"Reminder sent to {patient_email}"
        
    except Exception as e:
        return f"Failed to send reminder: {str(e)}"

@celery.task
def generate_monthly_report(doctor_id, month, year):
    """Generate monthly report for doctor"""
    try:
        from backend.models import Doctor, Appointment, Patient
        from backend.app import db
        
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return "Doctor not found"
        
        # Get appointments for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= start_date.date(),
            Appointment.appointment_date < end_date.date()
        ).all()
        
        # Generate report data
        total_appointments = len(appointments)
        completed_appointments = len([a for a in appointments if a.status == 'completed'])
        cancelled_appointments = len([a for a in appointments if a.status == 'cancelled'])
        
        report_data = {
            'doctor_name': doctor.name,
            'month': f"{month}/{year}",
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'completion_rate': (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
        }
        
        # In a real application, you would save this to a file or database
        return f"Monthly report generated for {doctor.name}: {report_data}"
        
    except Exception as e:
        return f"Failed to generate report: {str(e)}"

@celery.task
def export_patient_history(patient_id):
    """Export patient treatment history to CSV"""
    try:
        from backend.models import Patient, Appointment, Treatment
        import csv
        import io
        
        patient = Patient.query.get(patient_id)
        if not patient:
            return "Patient not found"
        
        # Get patient's treatment history
        appointments = Appointment.query.filter_by(patient_id=patient_id).all()
        
        # Create CSV data
        csv_data = io.StringIO()
        writer = csv.writer(csv_data)
        
        # Write header
        writer.writerow(['Date', 'Doctor', 'Diagnosis', 'Prescription', 'Notes'])
        
        # Write data
        for appointment in appointments:
            treatments = Treatment.query.filter_by(appointment_id=appointment.id).all()
            for treatment in treatments:
                writer.writerow([
                    appointment.appointment_date,
                    appointment.doctor.name if appointment.doctor else 'N/A',
                    treatment.diagnosis,
                    treatment.prescription,
                    appointment.notes
                ])
        
        # In a real application, you would save this file to storage
        csv_content = csv_data.getvalue()
        csv_data.close()
        
        return f"Patient history exported for {patient.name}: {len(csv_content)} characters"
        
    except Exception as e:
        return f"Failed to export history: {str(e)}"

@celery.task
def daily_appointment_reminders():
    """Send daily reminders for next day appointments"""
    try:
        from backend.models import Appointment, Patient, Doctor
        from datetime import date
        
        tomorrow = date.today() + timedelta(days=1)
        
        appointments = Appointment.query.filter(
            Appointment.appointment_date == tomorrow,
            Appointment.status == 'booked'
        ).all()
        
        reminders_sent = 0
        for appointment in appointments:
            if appointment.patient and appointment.doctor:
                send_appointment_reminder.delay(
                    appointment.patient.user.email,
                    appointment.patient.name,
                    appointment.doctor.name,
                    str(appointment.appointment_date),
                    str(appointment.appointment_time)
                )
                reminders_sent += 1
        
        return f"Sent {reminders_sent} appointment reminders for {tomorrow}"
        
    except Exception as e:
        return f"Failed to send daily reminders: {str(e)}"
