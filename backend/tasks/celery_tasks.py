from celery import Celery
from datetime import datetime, date, timedelta
import csv
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import db
from models import User, Patient, Doctor, Appointment, Treatment

# Initialize Celery
celery = Celery('hospital_management')

@celery.task
def send_daily_reminders():
    """Send daily appointment reminders to patients"""
    try:
        today = date.today()
        
        # Get all appointments for today
        appointments = Appointment.query.filter_by(
            appointment_date=today,
            status='booked'
        ).all()
        
        reminders_sent = 0
        
        for appointment in appointments:
            if appointment.patient and appointment.patient.user:
                # In a real application, you would send email/SMS here
                # For demo purposes, we'll just log the reminder
                print(f"Reminder: {appointment.patient.name} has an appointment with {appointment.doctor.name} at {appointment.appointment_time}")
                reminders_sent += 1
        
        return f"Sent {reminders_sent} appointment reminders for {today}"
        
    except Exception as e:
        return f"Error sending reminders: {str(e)}"

@celery.task
def generate_monthly_report():
    """Generate monthly activity report for doctors"""
    try:
        # Get current month
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get all doctors
        doctors = Doctor.query.filter_by(is_active=True).all()
        
        reports_generated = 0
        
        for doctor in doctors:
            # Get appointments for this month
            appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date >= month_start,
                Appointment.status == 'completed'
            ).all()
            
            # Get treatments for this month
            treatments = Treatment.query.join(Appointment).filter(
                Appointment.doctor_id == doctor.id,
                Treatment.created_at >= month_start
            ).all()
            
            # Generate HTML report
            html_report = generate_doctor_report_html(doctor, appointments, treatments, now.month, now.year)
            
            # In a real application, you would send email here
            # For demo purposes, we'll just log the report
            print(f"Monthly report generated for {doctor.name}: {len(appointments)} appointments, {len(treatments)} treatments")
            reports_generated += 1
        
        return f"Generated {reports_generated} monthly reports for {now.strftime('%B %Y')}"
        
    except Exception as e:
        return f"Error generating monthly reports: {str(e)}"

@celery.task
def export_patient_history_csv(patient_id):
    """Export patient treatment history as CSV"""
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return f"Patient with ID {patient_id} not found"
        
        # Get all treatments for this patient
        treatments = Treatment.query.join(Appointment).filter(
            Appointment.patient_id == patient_id
        ).order_by(Treatment.created_at.desc()).all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Patient ID', 'Patient Name', 'Doctor Name', 'Appointment Date', 
            'Visit Type', 'Symptoms', 'Diagnosis', 'Prescription', 'Treatment Notes'
        ])
        
        # Write data
        for treatment in treatments:
            writer.writerow([
                patient.id,
                patient.name,
                treatment.appointment.doctor.name if treatment.appointment.doctor else 'N/A',
                treatment.appointment.appointment_date if treatment.appointment else 'N/A',
                treatment.visit_type,
                treatment.symptoms,
                treatment.diagnosis,
                treatment.prescription,
                treatment.treatment_notes
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        # In a real application, you would save the file and send it to the patient
        # For demo purposes, we'll just log the export
        print(f"CSV export completed for {patient.name}: {len(treatments)} records")
        
        return f"CSV export completed for {patient.name}: {len(treatments)} records"
        
    except Exception as e:
        return f"Error exporting CSV for patient {patient_id}: {str(e)}"

def generate_doctor_report_html(doctor, appointments, treatments, month, year):
    """Generate HTML report for doctor monthly activity"""
    html = f"""
    <html>
    <head>
        <title>Monthly Report - {doctor.name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
            .content {{ margin: 20px 0; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat-box {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; text-align: center; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Monthly Activity Report</h1>
            <h2>Dr. {doctor.name} - {doctor.specialization}</h2>
            <p>Report for {month}/{year}</p>
        </div>
        
        <div class="content">
            <div class="stats">
                <div class="stat-box">
                    <h3>{len(appointments)}</h3>
                    <p>Total Appointments</p>
                </div>
                <div class="stat-box">
                    <h3>{len(treatments)}</h3>
                    <p>Treatments Provided</p>
                </div>
                <div class="stat-box">
                    <h3>{len(set([apt.patient_id for apt in appointments]))}</h3>
                    <p>Unique Patients</p>
                </div>
            </div>
            
            <h3>Recent Appointments</h3>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Patient</th>
                    <th>Time</th>
                    <th>Status</th>
                </tr>
    """
    
    for appointment in appointments[:10]:  # Show last 10 appointments
        html += f"""
                <tr>
                    <td>{appointment.appointment_date}</td>
                    <td>{appointment.patient.name if appointment.patient else 'N/A'}</td>
                    <td>{appointment.appointment_time}</td>
                    <td>{appointment.status}</td>
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
    
    for treatment in treatments[:10]:  # Show last 10 treatments
        html += f"""
                <tr>
                    <td>{treatment.created_at.strftime('%Y-%m-%d')}</td>
                    <td>{treatment.appointment.patient.name if treatment.appointment and treatment.appointment.patient else 'N/A'}</td>
                    <td>{treatment.visit_type}</td>
                    <td>{treatment.diagnosis[:50] if treatment.diagnosis else 'N/A'}...</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
    </body>
    </html>
    """
    
    return html

# Schedule tasks
from celery.schedules import crontab

celery.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.celery_tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),  # Run at 8 AM daily
    },
    'monthly-reports': {
        'task': 'tasks.celery_tasks.generate_monthly_report',
        'schedule': crontab(0, 0, day_of_month=1),  # Run on 1st of every month
    },
}