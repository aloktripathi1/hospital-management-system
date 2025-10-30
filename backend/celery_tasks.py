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
    # daily reminder every 2 minutes (demo mode)
    sender.add_periodic_task(120.0, send_daily_reminders.s(), name='daily-reminders')
    # monthly report every 3 minutes (demo mode)
    sender.add_periodic_task(180.0, generate_monthly_report.s(), name='monthly-reports')

@celery.task
def send_daily_reminders():
    from app import app, mail
    
    try:
        with app.app_context():
            today = date.today()
            appts = Appointment.query.filter_by(appointment_date=today, status='booked').all()
            
            count = 0
            for appt in appts:
                if appt.patient and appt.doctor and appt.patient.user:
                    try:
                        patient_email = appt.patient.user.email
                        patient_name = appt.patient.name
                        doctor_name = appt.doctor.name
                        appointment_time = appt.appointment_time
                        
                        html = f"""
                        <html>
                        <head>
                            <style>
                                body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f8f9fa; }}
                                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
                                .header {{ background: linear-gradient(135deg, #006064 0%, #00838F 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; margin: -30px -30px 20px -30px; }}
                                .info-box {{ background-color: #e8f4f8; padding: 15px; border-left: 4px solid #006064; margin: 20px 0; }}
                                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="header">
                                    <h2 style="margin: 0;">🏥 Appointment Reminder</h2>
                                </div>
                                <p>Hi <strong>{patient_name}</strong>,</p>
                                <p>This is a friendly reminder that you have an appointment scheduled for <strong>TODAY</strong>:</p>
                                <div class="info-box">
                                    <p style="margin: 5px 0;"><strong>👨‍⚕️ Doctor:</strong> Dr. {doctor_name}</p>
                                    <p style="margin: 5px 0;"><strong>⏰ Time:</strong> {appointment_time}</p>
                                    <p style="margin: 5px 0;"><strong>📅 Date:</strong> {today}</p>
                                </div>
                                <p><strong>⚠️ Please arrive 10 minutes early.</strong></p>
                                <p>If you need to reschedule, please contact us as soon as possible.</p>
                                <div class="footer">
                                    <p>This is an automated message from Hospital Management System.</p>
                                </div>
                            </div>
                        </body>
                        </html>
                        """
                        
                        msg = Message(
                            subject=f"Appointment Reminder - {today}",
                            recipients=[patient_email],
                            html=html
                        )
                        mail.send(msg)
                        print(f"✅ Reminder sent to {patient_email}: Dr. {doctor_name} at {appointment_time}")
                        count += 1
                    except Exception as e:
                        print(f"❌ Failed to send reminder to {patient_email}: {str(e)}")
                        continue
            
            return f"✅ Sent {count} daily reminders for {today}"
    except Exception as e:
        print(f"❌ Error in send_daily_reminders: {str(e)}")
        return f"❌ Error: {str(e)}"

@celery.task
def generate_monthly_report():
    from app import app, mail
    
    try:
        with app.app_context():
            now = datetime.now()
            # calculate previous month
            first_day_current = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_day_previous = first_day_current - timedelta(days=1)
            first_day_previous = last_day_previous.replace(day=1)
            
            docs = Doctor.query.filter_by(is_active=True).all()
            
            count = 0
            for doc in docs:
                if not doc.user:
                    continue
                
                try:
                    # get previous month's completed appointments
                    appts = Appointment.query.filter(
                        Appointment.doctor_id == doc.id,
                        Appointment.appointment_date >= first_day_previous.date(),
                        Appointment.appointment_date <= last_day_previous.date(),
                        Appointment.status == 'completed'
                    ).all()
                    
                    # get previous month's treatments
                    treatments = Treatment.query.join(Appointment).filter(
                        Appointment.doctor_id == doc.id,
                        Treatment.created_at >= first_day_previous,
                        Treatment.created_at <= last_day_previous
                    ).all()
                    
                    unique_patients = len(set([a.patient_id for a in appts if a.patient_id]))
                    
                    html = f"""
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f8f9fa; }}
                            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
                            .header {{ background: linear-gradient(135deg, #006064 0%, #00838F 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; margin: -30px -30px 20px -30px; }}
                            .summary {{ background-color: #e8f4f8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                            .stat-box {{ display: inline-block; margin: 10px 20px 10px 0; }}
                            .stat-number {{ font-size: 32px; font-weight: bold; color: #006064; }}
                            .stat-label {{ color: #666; font-size: 14px; }}
                            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                            th, td {{ border: 1px solid #ddd; padding: 12px 8px; text-align: left; }}
                            th {{ background-color: #006064; color: white; font-weight: bold; }}
                            tr:nth-child(even) {{ background-color: #f8f9fa; }}
                            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <div class="header">
                                <h1 style="margin: 0;">📊 Monthly Activity Report</h1>
                                <p style="margin: 10px 0 0 0;">Dr. {doc.name} - {doc.specialization}</p>
                            </div>
                            
                            <h2>Report Period: {first_day_previous.strftime('%B %Y')}</h2>
                            
                            <div class="summary">
                                <h3 style="margin-top: 0;">Summary Statistics</h3>
                                <div class="stat-box">
                                    <div class="stat-number">{len(appts)}</div>
                                    <div class="stat-label">Total Appointments</div>
                                </div>
                                <div class="stat-box">
                                    <div class="stat-number">{len(treatments)}</div>
                                    <div class="stat-label">Total Treatments</div>
                                </div>
                                <div class="stat-box">
                                    <div class="stat-number">{unique_patients}</div>
                                    <div class="stat-label">Unique Patients</div>
                                </div>
                            </div>
                            
                            <h3>📅 Recent Appointments</h3>
                            <table>
                                <tr>
                                    <th>Date</th>
                                    <th>Patient</th>
                                    <th>Time</th>
                                    <th>Status</th>
                                </tr>
                    """
                    
                    for a in appts[:15]:
                        patient_name = a.patient.name if a.patient else 'N/A'
                        html += f"""
                                <tr>
                                    <td>{a.appointment_date}</td>
                                    <td>{patient_name}</td>
                                    <td>{a.appointment_time}</td>
                                    <td><span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 4px;">{a.status}</span></td>
                                </tr>
                        """
                    
                    html += """
                            </table>
                            
                            <h3>💊 Recent Treatments</h3>
                            <table>
                                <tr>
                                    <th>Date</th>
                                    <th>Patient</th>
                                    <th>Visit Type</th>
                                    <th>Diagnosis</th>
                                </tr>
                    """
                    
                    for t in treatments[:15]:
                        patient_name = t.appointment.patient.name if t.appointment and t.appointment.patient else 'N/A'
                        diagnosis = (t.diagnosis[:60] + '...') if t.diagnosis and len(t.diagnosis) > 60 else (t.diagnosis or 'N/A')
                        html += f"""
                                <tr>
                                    <td>{t.created_at.strftime('%Y-%m-%d')}</td>
                                    <td>{patient_name}</td>
                                    <td>{t.visit_type or 'N/A'}</td>
                                    <td>{diagnosis}</td>
                                </tr>
                        """
                    
                    html += f"""
                            </table>
                            
                            <div class="footer">
                                <p>This is an automated monthly report from Hospital Management System.</p>
                                <p>Generated on {now.strftime('%B %d, %Y at %I:%M %p')}</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    doctor_email = doc.user.email
                    subject = f"Monthly Activity Report - {first_day_previous.strftime('%B %Y')}"
                    
                    msg = Message(
                        subject=subject,
                        recipients=[doctor_email],
                        html=html
                    )
                    mail.send(msg)
                    
                    print(f"✅ Monthly report sent to Dr. {doc.name} ({doctor_email})")
                    count += 1
                except Exception as e:
                    print(f"❌ Failed to send report to Dr. {doc.name}: {str(e)}")
                    continue
            
            return f"✅ Generated and sent {count} monthly reports for {first_day_previous.strftime('%B %Y')}"
    except Exception as e:
        print(f"❌ Error in generate_monthly_report: {str(e)}")
        return f"❌ Error: {str(e)}"

@celery.task
def export_patient_history_csv(patient_id):
    from app import app, mail
    
    try:
        with app.app_context():
            patient = Patient.query.get(patient_id)
            if not patient or not patient.user:
                return f"❌ Patient {patient_id} not found or has no user account"
            
            # get all treatments for this patient
            treatments = Treatment.query.join(Appointment).filter(
                Appointment.patient_id == patient_id
            ).order_by(Treatment.created_at.desc()).all()
            
            # create exports directory
            exports_dir = os.path.join(os.path.dirname(__file__), 'exports')
            os.makedirs(exports_dir, exist_ok=True)
            
            # generate csv filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"patient_{patient_id}_history_{timestamp}.csv"
            filepath = os.path.join(exports_dir, filename)
            
            # write csv file
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['user_id', 'username', 'doctor', 'appointment_date', 'diagnosis', 'treatment', 'next_visit']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for t in treatments:
                    doctor_name = t.appointment.doctor.name if t.appointment and t.appointment.doctor else 'N/A'
                    appt_date = str(t.appointment.appointment_date) if t.appointment else 'N/A'
                    
                    writer.writerow({
                        'user_id': patient.user_id,
                        'username': patient.user.username if patient.user else 'N/A',
                        'doctor': doctor_name,
                        'appointment_date': appt_date,
                        'diagnosis': t.diagnosis or 'N/A',
                        'treatment': t.treatment_notes or 'N/A',
                        'next_visit': 'N/A'
                    })
            
            patient_email = patient.user.email
            
            # send email with csv attachment
            html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f8f9fa; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
                    .header {{ background: linear-gradient(135deg, #006064 0%, #00838F 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; margin: -30px -30px 20px -30px; }}
                    .info-box {{ background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                    .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2 style="margin: 0;">📄 Medical History Export Ready</h2>
                    </div>
                    <p>Hi <strong>{patient.name}</strong>,</p>
                    <p>Your medical history export has been completed successfully!</p>
                    <div class="info-box">
                        <p style="margin: 5px 0;"><strong>📊 Total Records:</strong> {len(treatments)}</p>
                        <p style="margin: 5px 0;"><strong>📁 File:</strong> {filename}</p>
                        <p style="margin: 5px 0;"><strong>🕒 Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                    <p>Please find your complete treatment history attached to this email as a CSV file.</p>
                    <p>You can open this file with Excel, Google Sheets, or any spreadsheet application.</p>
                    <div class="footer">
                        <p>This is an automated message from Hospital Management System.</p>
                        <p>If you did not request this export, please contact us immediately.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject="Your Medical History Export is Ready",
                recipients=[patient_email],
                html=html
            )
            
            # attach csv file
            with open(filepath, 'r', encoding='utf-8') as f:
                msg.attach(filename, "text/csv", f.read())
            
            mail.send(msg)
            
            print(f"✅ CSV exported and emailed to {patient.name} ({patient_email})")
            print(f"   File: {filepath}")
            print(f"   Records: {len(treatments)}")
            
            
            return f"✅ Exported {len(treatments)} records to {filename} and sent email to {patient_email}"
    
    except Exception as e:
        print(f"❌ Error in export_patient_history_csv: {str(e)}")
        return f"❌ Error: {str(e)}"

