# MailHog + Celery Setup Guide

## 🎯 Complete Integration Guide for Hospital Management System

This guide shows how to run Celery with Redis and MailHog for email testing.

---

## 📋 What's Included

### ✅ Three Background Jobs Implemented:

1. **Daily Reminder Email** - Sends appointment reminders to patients
2. **Monthly Activity Report** - Sends monthly statistics to doctors
3. **User-Triggered CSV Export** - Exports patient history with email notification

---

## 🔧 Prerequisites

### 1. Install MailHog

**On Ubuntu/Debian (WSL):**
```bash
# Download MailHog
wget https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64
chmod +x MailHog_linux_amd64
sudo mv MailHog_linux_amd64 /usr/local/bin/mailhog
```

**On macOS:**
```bash
brew install mailhog
```

**On Windows:**
Download from: https://github.com/mailhog/MailHog/releases

### 2. Verify Redis is Running
```bash
redis-cli ping
# Should return: PONG
```

If not running:
```bash
redis-server
```

---

## 🚀 Running the Application

You need **5 terminal windows**:

### Terminal 1: Redis Server
```bash
redis-server
```

### Terminal 2: MailHog
```bash
mailhog
```

**Expected output:**
```
[HTTP] Binding to address: 0.0.0.0:8025
[SMTP] Binding to address: 0.0.0.0:1025
```

**Web UI:** http://localhost:8025

### Terminal 3: Flask Backend
```bash
cd /workspaces/hospital-management-system/backend
python3 app.py
```

### Terminal 4: Celery Worker
```bash
cd /workspaces/hospital-management-system/backend
celery -A celery_tasks.celery worker --loglevel=info --pool=solo
```

**Expected output:**
```
[tasks]
  . celery_tasks.export_patient_history_csv
  . celery_tasks.generate_monthly_report
  . celery_tasks.send_daily_reminders

celery@hostname ready.
```

### Terminal 5: Celery Beat (Scheduler)
```bash
cd /workspaces/hospital-management-system/backend
celery -A celery_tasks.celery beat --loglevel=info
```

**Expected output:**
```
Scheduler: Sending due task daily-reminders (celery_tasks.send_daily_reminders)
Scheduler: Sending due task monthly-reports (celery_tasks.generate_monthly_report)
```

---

## 📧 Testing Email Functionality

### 1. View MailHog Web Interface

Open your browser:
```
http://localhost:8025
```

You'll see all emails sent by the system!

### 2. Test Daily Reminders

**Setup:**
1. Login as admin (`admin` / `admin123`)
2. Create a patient with email: `patient@example.com`
3. Create an appointment for **TODAY** with status **"booked"**

**Verify:**
- Wait 2 minutes (or trigger manually)
- Check MailHog inbox
- You should see: **"Appointment Reminder - {date}"**

### 3. Test Monthly Reports

**Setup:**
1. Make sure you have active doctors with email addresses
2. Create completed appointments for previous month

**Verify:**
- Wait 3 minutes (or trigger manually)
- Check MailHog inbox for doctors
- You should see: **"Monthly Activity Report - {month}"**

### 4. Test CSV Export (Manual Trigger)

**From Python Shell:**
```bash
cd /workspaces/hospital-management-system/backend
python3
```

```python
from celery_tasks import export_patient_history_csv
from app import app

# Trigger export for patient ID 1
with app.app_context():
    result = export_patient_history_csv.delay(1)
    print(result.id)
```

**Verify:**
- Check MailHog inbox
- Email subject: **"Your Medical History Export is Ready"**
- CSV file should be attached
- Check `backend/exports/` folder for CSV file

---

## 📊 Schedule Configuration

### Current Settings (Demo Mode)

In `celery_tasks.py`:
```python
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Runs every 2 minutes
    sender.add_periodic_task(120.0, send_daily_reminders.s(), name='daily-reminders')
    
    # Runs every 3 minutes
    sender.add_periodic_task(180.0, generate_monthly_report.s(), name='monthly-reports')
```

### Production Settings

For production, use crontab schedules:

```python
from celery.schedules import crontab

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Daily at 8 AM
    sender.add_periodic_task(
        crontab(hour=8, minute=0),
        send_daily_reminders.s(),
        name='daily-reminders'
    )
    
    # 1st of every month at midnight
    sender.add_periodic_task(
        crontab(hour=0, minute=0, day_of_month=1),
        generate_monthly_report.s(),
        name='monthly-reports'
    )
```

---

## 🔍 Monitoring & Debugging

### Check Celery Worker Logs

In Terminal 4, you'll see:
```
[2025-10-30 05:15:00] Task celery_tasks.send_daily_reminders[uuid] received
✅ Reminder sent to patient@example.com: Dr. Smith at 10:00 AM
[2025-10-30 05:15:01] Task celery_tasks.send_daily_reminders[uuid] succeeded in 1.2s: '✅ Sent 1 daily reminders for 2025-10-30'
```

### Check MailHog

All emails appear in real-time at: http://localhost:8025

### Check CSV Exports

```bash
ls -lh backend/exports/
```

You should see files like:
```
patient_1_history_20251030_151530.csv
patient_2_history_20251030_152045.csv
```

---

## 🐛 Troubleshooting

### ❌ Issue: "Cannot connect to Redis"
**Solution:**
```bash
# Start Redis
redis-server

# Or check if running
redis-cli ping
```

### ❌ Issue: "Cannot connect to SMTP server"
**Solution:**
```bash
# Start MailHog
mailhog

# Verify it's running on port 1025
netstat -an | grep 1025
```

### ❌ Issue: "No emails showing in MailHog"
**Solution:**
1. Check `.env` file has correct settings:
   ```
   MAIL_SERVER=localhost
   MAIL_PORT=1025
   ```
2. Restart Flask app to reload config
3. Check Celery worker logs for errors

### ❌ Issue: "Task not found"
**Solution:**
```bash
# Restart Celery worker
# Press Ctrl+C in Terminal 4, then:
celery -A celery_tasks.celery worker --loglevel=info --pool=solo
```

### ❌ Issue: "Periodic tasks not running"
**Solution:**
```bash
# Make sure Celery Beat is running (Terminal 5)
celery -A celery_tasks.celery beat --loglevel=info

# Check beat logs for schedule execution
```

### ❌ Issue: "FileNotFoundError: exports directory"
**Solution:**
```bash
mkdir -p backend/exports
```

---

## 📝 Task Details

### 1. Daily Reminder Email

**Function:** `send_daily_reminders()`

**Triggers:** Every 2 minutes (demo) / 8 AM daily (production)

**Logic:**
- Queries appointments for TODAY with status="booked"
- Sends HTML email to each patient
- Includes doctor name, time, and date

**Email Preview:**
```
Subject: Appointment Reminder - 2025-10-30
To: patient@example.com

🏥 Appointment Reminder

Hi John Doe,

This is a friendly reminder that you have an appointment scheduled for TODAY:

👨‍⚕️ Doctor: Dr. Smith
⏰ Time: 10:00 AM
📅 Date: 2025-10-30

⚠️ Please arrive 10 minutes early.
```

---

### 2. Monthly Activity Report

**Function:** `generate_monthly_report()`

**Triggers:** Every 3 minutes (demo) / 1st of month (production)

**Logic:**
- Queries previous month's data for each doctor
- Calculates: appointments, treatments, unique patients
- Generates HTML report with tables
- Sends to doctor's email

**Email Preview:**
```
Subject: Monthly Activity Report - October 2025
To: doctor@hospital.com

📊 Monthly Activity Report
Dr. Smith - Cardiology

Summary Statistics:
Total Appointments: 45
Total Treatments: 38
Unique Patients: 32

[Tables with appointment and treatment details]
```

---

### 3. User-Triggered CSV Export

**Function:** `export_patient_history_csv(patient_id)`

**Triggers:** Manual API call or admin action

**Logic:**
- Queries all treatments for patient
- Creates CSV file in `exports/` folder
- Sends email with CSV attachment
- Columns: user_id, username, doctor, appointment_date, diagnosis, treatment, next_visit

**Email Preview:**
```
Subject: Your Medical History Export is Ready
To: patient@example.com

📄 Medical History Export Ready

Hi Jane Doe,

Your medical history export has been completed successfully!

📊 Total Records: 12
📁 File: patient_1_history_20251030_151530.csv
🕒 Generated: October 30, 2025 at 03:15 PM

[CSV file attached]
```

**CSV Format:**
```csv
user_id,username,doctor,appointment_date,diagnosis,treatment,next_visit
1,jane_doe,Dr. Smith,2025-09-15,Flu,Rest and fluids,N/A
1,jane_doe,Dr. Jones,2025-08-10,Check-up,All normal,N/A
```

---

## 🧪 Manual Testing Commands

### Trigger Tasks Manually (Python Shell)

```bash
cd backend
python3
```

```python
from celery_tasks import send_daily_reminders, generate_monthly_report, export_patient_history_csv
from app import app

# Test daily reminders
with app.app_context():
    result = send_daily_reminders.delay()
    print(result.get())

# Test monthly report
with app.app_context():
    result = generate_monthly_report.delay()
    print(result.get())

# Test CSV export for patient ID 1
with app.app_context():
    result = export_patient_history_csv.delay(1)
    print(result.get())
```

### Check Task Results

```python
from celery.result import AsyncResult
from celery_tasks import celery

# Get result by task ID
result = AsyncResult('task-id-here', app=celery)
print(result.state)
print(result.result)
```

---

## 📂 File Structure

```
backend/
├── app.py                    # Flask app with Mail config
├── celery_tasks.py           # All 3 Celery tasks
├── .env                      # MailHog configuration
├── exports/                  # CSV export directory
│   ├── .gitkeep
│   └── patient_*_history_*.csv
└── requirements.txt          # Dependencies
```

---

## ✅ Configuration Files

### .env
```env
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USE_SSL=False
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@hospital.com
```

### app.py (Email Config)
```python
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 1025))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_DEFAULT_SENDER'] = ('Hospital Management', os.getenv('MAIL_DEFAULT_SENDER', 'noreply@hospital.com'))
```

---

## 🎓 Student Notes

### Key Concepts Demonstrated:

1. **Asynchronous Task Processing** - Background jobs don't block main app
2. **Scheduled Tasks** - Periodic jobs run automatically
3. **Email Integration** - HTML emails with attachments
4. **CSV Generation** - Export data programmatically
5. **Error Handling** - Try-except blocks for robustness
6. **MailHog Testing** - No real email needed for development

### Production Considerations:

- Use real SMTP server (Gmail, SendGrid, AWS SES)
- Implement proper error logging
- Add retry logic for failed tasks
- Monitor task queue length
- Set up task result expiration
- Use environment variables for all config

---

## 🔗 Useful URLs

- **MailHog Web UI:** http://localhost:8025
- **Flask App:** http://localhost:5000
- **Redis:** localhost:6379
- **Celery Flower (optional monitoring):** Install with `pip install flower`, run with `celery -A celery_tasks.celery flower`

---

## 📚 Additional Commands

### Stop All Services

```bash
# Kill Redis
pkill redis-server

# Kill MailHog
pkill mailhog

# Kill Celery
pkill -f celery

# Kill Flask
pkill -f "python3 app.py"
```

### Clear Celery Queue

```bash
celery -A celery_tasks.celery purge
```

### Inspect Celery Workers

```bash
celery -A celery_tasks.celery inspect active
celery -A celery_tasks.celery inspect scheduled
celery -A celery_tasks.celery inspect stats
```

---

**All Set! Start testing with MailHog! 📧**

Check http://localhost:8025 to see all your emails in real-time!
