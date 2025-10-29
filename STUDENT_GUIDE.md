# Student Implementation Guide - Hospital Management System

## 📚 Simple Implementation for Students

This guide explains the implemented backend jobs, caching, and async tasks in a student-friendly way.

---

## 🔄 Background Jobs (Celery Tasks)

### What is Celery?
Celery is a simple task queue system that lets you run tasks in the background without blocking your main application.

### Setup
1. **Redis** is required (acts as message broker)
2. **Celery Worker** runs the background tasks
3. **Celery Beat** schedules periodic tasks

### How to Run

```bash
# Terminal 1: Start Flask app
cd backend
python app.py

# Terminal 2: Start Celery Worker (runs background tasks)
cd backend
celery -A celery_tasks worker --loglevel=info

# Terminal 3: Start Celery Beat (runs scheduled tasks)
cd backend
celery -A celery_tasks beat --loglevel=info
```

---

## 📋 Implemented Features

### 1. Daily Reminders (Scheduled Job)

**Purpose:** Send reminders to patients every morning about today's appointments

**Location:** `backend/celery_tasks.py` - `send_daily_reminders()` function

**Schedule:** Runs automatically at 8:00 AM every day

**How it works:**
1. Celery Beat triggers the task at 8 AM
2. Task queries database for today's booked appointments
3. For each appointment, creates a reminder message
4. Prints the message (can be replaced with email/SMS)

**Code:**
```python
@celery.task
def send_daily_reminders():
    # Get appointments for today
    appts = Appointment.query.filter_by(
        appointment_date=date.today(), 
        status='booked'
    ).all()
    
    # Send reminder for each appointment
    for appt in appts:
        print(f"Reminder: {appt.patient.name} has appointment with Dr. {appt.doctor.name}")
```

**To customize schedule:** Edit `celery.conf.beat_schedule` in `celery_tasks.py`:
```python
'schedule': crontab(hour=8, minute=0),  # 8:00 AM
# Change to: crontab(hour=10, minute=30)  # 10:30 AM
```

---

### 2. Monthly Reports (Scheduled Job)

**Purpose:** Generate monthly activity report for each doctor

**Location:** `backend/celery_tasks.py` - `generate_monthly_report()` function

**Schedule:** Runs on 1st day of every month at midnight

**How it works:**
1. Celery Beat triggers the task on 1st of month
2. Gets all active doctors from database
3. For each doctor, collects:
   - Completed appointments this month
   - Treatments provided this month
   - Patient count
4. Generates HTML report
5. Prints report (can be emailed to doctor)

**Report includes:**
- Total appointments
- Total treatments
- Unique patients count
- Detailed appointment and treatment tables

**Code:**
```python
@celery.task
def generate_monthly_report():
    # Get start of current month
    month_start = datetime.now().replace(day=1)
    
    # For each doctor
    for doc in Doctor.query.all():
        # Get this month's appointments
        appts = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.appointment_date >= month_start
        ).all()
        
        # Generate HTML report
        html = make_html_report(doc, appts)
        print(html)  # In production: send_email(html)
```

---

### 3. CSV Export (User-Triggered Async Job)

**Purpose:** Export patient's complete medical history to CSV file

**Location:** `backend/celery_tasks.py` - `export_patient_history_csv()` function

**Trigger:** Patient clicks "Export Full History" button in Medical History tab

**How it works:**
1. Patient clicks export button
2. Frontend calls `/api/patient/export-history`
3. Backend triggers Celery task asynchronously
4. Task runs in background:
   - Queries all patient treatments
   - Creates CSV file with all records
   - Saves to `exports/` folder
5. Returns task ID to patient

**CSV includes:**
- Patient ID and Name
- Doctor Name
- Appointment Date
- Visit Type
- Symptoms
- Diagnosis
- Treatment Given
- Prescription
- Notes

**Code:**
```python
@celery.task
def export_patient_history_csv(patient_id):
    # Get patient data
    treatments = Treatment.query.join(Appointment).filter(
        Appointment.patient_id == patient_id
    ).all()
    
    # Write CSV
    with open(f'patient_{patient_id}_history.csv', 'w') as f:
        f.write("Patient ID,Name,Doctor,Date,Diagnosis...\n")
        for t in treatments:
            f.write(f"{patient_id},{patient.name},...\n")
```

---

## 💾 Caching (Performance Optimization)

### What is Caching?
Storing frequently accessed data in memory to avoid repeated database queries.

### Simple Implementation

**Location:** `backend/routes/admin.py` - `dashboard_stats()` function

**How it works:**
1. When admin requests dashboard stats:
   - Check if cached data exists
   - Check if cache is still fresh (< 5 minutes old)
   - If yes, return cached data (fast!)
   - If no, query database and cache result

**Benefits:**
- Reduces database load
- Faster response times
- Improves app performance

**Code:**
```python
cache = {}  # Simple dictionary cache

@app.route('/stats')
def get_stats():
    # Check cache
    if 'stats' in cache:
        cached_data, cached_time = cache['stats']
        # Cache expiry: 5 minutes
        if (datetime.now() - cached_time).seconds < 300:
            return cached_data  # Return cached data
    
    # Cache miss - fetch from database
    stats = calculate_stats()
    cache['stats'] = (stats, datetime.now())
    return stats
```

**Cache Expiry:** 5 minutes (300 seconds)
- After 5 minutes, cache is considered stale
- Fresh data is fetched from database
- New data is cached for next 5 minutes

---

## 🎯 Testing the Features

### Test Daily Reminders

**Option 1: Manual trigger**
```python
# In Python shell
from celery_tasks import send_daily_reminders
result = send_daily_reminders.delay()  # Runs async
print(result.get())  # Wait for result
```

**Option 2: Wait for scheduled time**
- Make sure Celery Beat is running
- Create an appointment for today
- Wait until 8:00 AM
- Check Celery logs for reminder messages

### Test Monthly Reports

**Manual trigger:**
```python
from celery_tasks import generate_monthly_report
result = generate_monthly_report.delay()
print(result.get())
```

### Test CSV Export

1. Login as a patient
2. Go to "Medical History" tab
3. Click "Export Full History" button
4. Check `backend/exports/` folder for CSV file
5. Open CSV in Excel/Spreadsheet to verify data

### Test Caching

1. Login as admin
2. Load dashboard (first time - slow)
3. Check response message: "Dashboard stats retrieved (fresh)"
4. Refresh page within 5 minutes (fast!)
5. Check response message: "Dashboard stats retrieved (from cache)"
6. Wait 5+ minutes and refresh (slow again - cache expired)

---

## 📝 Customization Tips

### Change Reminder Time
```python
# In celery_tasks.py, find:
'schedule': crontab(hour=8, minute=0),  # 8:00 AM
# Change to:
'schedule': crontab(hour=7, minute=30),  # 7:30 AM
```

### Change Cache Duration
```python
# In admin.py, find:
if (datetime.now() - cached_time).total_seconds() < 300:  # 5 minutes
# Change to:
if (datetime.now() - cached_time).total_seconds() < 600:  # 10 minutes
```

### Add Email Notifications

**Install:**
```bash
pip install Flask-Mail
```

**Configure in app.py:**
```python
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'

mail = Mail(app)

def send_email(to, subject, body):
    msg = Message(subject, sender='your-email@gmail.com', recipients=[to])
    msg.html = body
    mail.send(msg)
```

**Use in celery_tasks.py:**
```python
# Replace print(message) with:
send_email(patient.email, "Appointment Reminder", message)
```

---

## ❓ Common Issues

### Redis Connection Error
```
Error: Cannot connect to redis://localhost:6379
```
**Solution:** Make sure Redis is installed and running:
```bash
# Install Redis (Ubuntu)
sudo apt-get install redis-server

# Start Redis
redis-server
```

### Celery Worker Not Running
```
Error: No celery workers available
```
**Solution:** Start celery worker in separate terminal:
```bash
cd backend
celery -A celery_tasks worker --loglevel=info
```

### Tasks Not Running on Schedule
```
Scheduled tasks not executing
```
**Solution:** Make sure Celery Beat is running:
```bash
cd backend
celery -A celery_tasks beat --loglevel=info
```

---

## 🎓 Understanding the Code

### Why Async Tasks?
- CSV generation can take time for large datasets
- Email sending shouldn't block the web request
- Reports are heavy operations that can run in background

### Why Scheduled Tasks?
- Reminders should be sent automatically every day
- Reports should be generated monthly without manual intervention
- Reduces manual work and ensures consistency

### Why Caching?
- Dashboard stats are frequently accessed
- Stats don't change every second
- Reduces unnecessary database queries
- Makes app faster and more efficient

---

## 🚀 Production Considerations

For actual production deployment:

1. **Use proper email service** (SendGrid, AWS SES, SMTP)
2. **Use Redis in production mode** (configure persistence)
3. **Add error handling** for failed tasks
4. **Add retry logic** for network failures
5. **Add logging** to track task execution
6. **Use environment variables** for sensitive config
7. **Monitor task queue** size and performance

---

## 📚 Further Learning

- **Celery Docs:** https://docs.celeryproject.org/
- **Redis Docs:** https://redis.io/documentation
- **Flask-Mail:** https://pythonhosted.org/Flask-Mail/
- **Caching Strategies:** https://en.wikipedia.org/wiki/Cache_replacement_policies

---

**Remember:** This is a simple student-friendly implementation. It demonstrates the concepts clearly without over-engineering. Focus on understanding how background jobs, scheduling, and caching work!
