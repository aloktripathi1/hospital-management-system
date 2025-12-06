# Email Setup Guide - Celery Tasks with Flask-Mail

## 📧 What Was Changed

All Celery tasks now **ACTUALLY SEND EMAILS** instead of just printing messages!

---

## 📝 Modified Files

### 1. **backend/requirements.txt**
Added:
- `Flask-Mail==0.9.1` - For sending emails
- `python-dotenv==1.0.0` - Already existed

### 2. **backend/.env** (NEW FILE)
Email configuration file:
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 3. **backend/app.py**
Added email configuration:
- Import: `from flask_mail import Mail` and `from dotenv import load_dotenv`
- Gmail SMTP setup (smtp.gmail.com, port 587, TLS)
- Load credentials from .env file
- Initialize: `mail = Mail(app)`

### 4. **backend/celery_tasks.py**
Major refactoring:
- **WSL-compatible Celery config** with `broker_connection_retry_on_startup = True`
- **send_email() helper function** - sends HTML emails using Flask-Mail
- **send_daily_reminders()** - Now sends HTML email to patients
- **generate_monthly_report()** - Now sends HTML email to doctors
- **export_patient_history_csv()** - Now sends email with CSV attachment
- **DEMO schedules**: Runs every 2-3 minutes instead of daily/monthly

### 5. **.gitignore**
Added:
- `backend/.env` - Don't commit email credentials
- `celerybeat-schedule*` - Don't commit Celery schedule database

---

## 🚀 Setup Instructions

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Gmail App Password
1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication
3. Go to https://myaccount.google.com/apppasswords
4. Create an "App Password" for "Mail"
5. Copy the 16-character password

### Step 3: Update .env File
Edit `backend/.env`:
```env
MAIL_USERNAME=your-actual-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
```

### Step 4: Start Redis (Required for Celery)
```bash
# On WSL/Linux
redis-server

# Or if using Docker
docker run -d -p 6379:6379 redis
```

### Step 5: Start Celery Worker
```bash
cd backend
celery -A celery_tasks worker --loglevel=info --pool=solo
```

### Step 6: Start Celery Beat (Scheduler)
In a separate terminal:
```bash
cd backend
celery -A celery_tasks beat --loglevel=info
```

### Step 7: Start Flask App
In a separate terminal:
```bash
cd backend
python app.py
```

---

## 📧 Email Features

### 1. Daily Appointment Reminders
- **Runs**: Every 2 minutes (demo mode)
- **Sends to**: Patients with appointments TODAY
- **Email**: HTML formatted reminder with appointment details
- **Subject**: "Appointment Reminder - {date}"

### 2. Monthly Doctor Reports
- **Runs**: Every 3 minutes (demo mode)
- **Sends to**: All active doctors
- **Email**: HTML report with appointments, treatments, patient stats
- **Subject**: "Monthly Activity Report - {month year}"

### 3. Patient History CSV Export
- **Triggered**: Manually via API endpoint
- **Sends to**: Patient who requested export
- **Email**: Includes CSV file as attachment
- **Subject**: "Your Medical History Export"

---

## 🎨 Email Templates

All emails use **inline CSS** for styling:
- Professional blue theme (#007bff)
- Responsive HTML layout
- Clear typography with Arial font
- Highlighted information boxes

---

## 🔧 Switching to Production Mode

Edit `celery_tasks.py` and change the beat_schedule:

**Comment out demo schedules:**
```python
# 'demo-daily-reminders': {...}
# 'demo-monthly-reports': {...}
```

**Uncomment production schedules:**
```python
'send-daily-reminders': {
    'task': 'celery_tasks.send_daily_reminders',
    'schedule': crontab(hour=8, minute=0),  # 8 AM daily
},
'generate-monthly-reports': {
    'task': 'celery_tasks.generate_monthly_report',
    'schedule': crontab(hour=0, minute=0, day_of_month=1),  # 1st of month
},
```

---

## ✅ Testing

1. Make sure you have patients with appointments for TODAY
2. Make sure patients have email addresses in their user accounts
3. Watch the Celery worker logs for email sending confirmations
4. Check your email inbox!

---

## 🐛 Troubleshooting

**Emails not sending?**
- Check .env file has correct Gmail credentials
- Verify Gmail App Password is correct (not regular password)
- Check Celery worker logs for errors
- Make sure Redis is running
- Verify user.email exists for patients/doctors

**Celery not running on Windows?**
- Use WSL (Windows Subsystem for Linux)
- Or use `--pool=solo` flag: `celery -A celery_tasks worker --pool=solo --loglevel=info`

**Redis connection error?**
- Make sure Redis is running: `redis-cli ping` should return "PONG"
- Check Redis is on localhost:6379

---

## 📌 Key Code Changes

### Send Email Helper (celery_tasks.py)
```python
def send_email(subject, recipient, html_body):
    from app import app, mail
    
    with app.app_context():
        msg = Message(subject=subject, recipients=[recipient], html=html_body)
        mail.send(msg)
        print(f"Email sent to {recipient}: {subject}")
```

### WSL-Compatible Celery Config
```python
celery.conf.broker_url = 'redis://localhost:6379/0'
celery.conf.result_backend = 'redis://localhost:6379/0'
celery.conf.broker_connection_retry_on_startup = True
```

---

## 🎯 Simple Student-Level Implementation

- No complex error handling with try/except
- Basic if-else checks only
- Print statements for debugging
- HTML emails with inline styles
- Straightforward code flow
- No over-engineering

---

**Ready to send real emails!** 📨
