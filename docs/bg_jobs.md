# Background Jobs (Email System)

This explains how the app sends emails automatically using Celery.

## What is Celery?

Celery is a tool that runs tasks in the background without slowing down the main app. Think of it like hiring someone to send emails while you focus on other work.

## Why Do We Need It?

Sending emails takes time. If we send them directly when a patient books an appointment, the patient would have to wait. With Celery, we:
1. Save the appointment instantly
2. Tell Celery "send this email when you can"
3. Show success message to patient immediately
4. Celery sends email in background

## How It's Organized

The Celery code is in `backend/celery_tasks/` folder:

```
celery_tasks/
├── __init__.py          # Main Celery setup (creates celery app)
├── imports.py           # Imports all task files
├── email.py             # Appointment confirmation emails
├── reminders.py         # Daily reminder emails (for today's appointments)
├── reports.py           # Monthly reports for doctors
└── email_template.py    # HTML email template functions
```

## Email Tasks

### 1. Appointment Confirmation
**File:** `celery_tasks/email.py`
**When:** Right after patient books appointment
**What:** Sends email to patient with appointment details

### 2. Daily Reminders
**File:** `celery_tasks/reminders.py`
**When:** Every day at 8 AM
**What:** Sends reminder to patients who have appointments today

### 3. Monthly Reports
**File:** `celery_tasks/reports.py`
**When:** 1st day of every month
**What:** Sends report to doctors with their monthly appointment summary

## How to Test

1. Book an appointment as a patient
2. Check terminal where Celery worker is running
3. You should see logs like:
   ```
   [2024-01-15 10:30:00,123: INFO/MainProcess] Task celery_tasks.email.send_appointment_confirmation[...] received
   [2024-01-15 10:30:01,456: INFO/ForkPoolWorker-1] Task celery_tasks.email.send_appointment_confirmation[...] succeeded
   ```

## Email Configuration

Emails are sent using Gmail SMTP. Configuration in `backend/celery_tasks/__init__.py`:

```python
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # From environment
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # From environment
```

**Note:** For Gmail, you need to use an "App Password" (not your regular password). Google this: "Gmail app password for less secure apps"

## Testing Without Real Emails

If you don't want to set up Gmail, Celery will still work but emails won't actually send. The app will function normally, you just won't receive email notifications.

To test properly:
- Use MailHog (fake email server)
- Check Celery logs to see if tasks are running
- Look for success/error messages in terminal

**Implementation:**
- ✅ **Checks for scheduled appointments**: Queries `Appointment.query.filter_by(appointment_date=today, status='booked')`
- ✅ **Sends email alerts**: Uses Gmail SMTP via Flask-Mail
- ✅ **HTML email format**: Simple HTML with patient name, doctor name, appointment time
- ✅ **Scheduled timing**: Runs every 2 minutes (demo mode) - configurable to daily at specific time
- ✅ **Uses app context**: `with app.app_context():`

**Configuration:**
```python
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Send reminders every 2 minutes (for demo)
    sender.add_periodic_task(120.0, send_daily_reminders.s())
    # Send monthly reports on 1st of every month at 9 AM
    sender.add_periodic_task(
        crontab(day_of_month='1', hour=9, minute=0),
        send_monthly_reports.s()
    )
```

**Email Method:** Gmail SMTP (configured in `celery_tasks/__init__.py`)
- Mail server: smtp.gmail.com:587
- Uses TLS encryption
- Credentials from environment variables (MAIL_USERNAME, MAIL_PASSWORD)

---

### b. Scheduled Job - Monthly Activity Report
**Location:** `backend/celery_tasks.py` (lines 51-97)

**Implementation:**
- ✅ **Creates HTML report**: Uses HTML tables for appointments
- ✅ **Includes required data**:
  - All appointments for the month (filtered by `status='completed'`)
  - Doctor information (name, specialization)
  - Diagnosis and treatment information (from Treatment model)
  - Patient names and appointment times
- ✅ **Sends via email**: HTML email to doctor's email address
- ✅ **Scheduled timing**: Runs every 3 minutes (demo mode) - configurable to 1st of month
- ✅ **Calculates previous month**: Proper date arithmetic for report period
- ✅ **Uses app context**: `with app.app_context():`

**Configuration:**
```python
sender.add_periodic_task(180.0, generate_monthly_report.s())  # 180s = 3 min demo
```

**Report Contents:**
- Doctor name and specialization
- Report period (e.g., "October 2025")
- Total appointments count
- Total treatments count
- Table of recent appointments with date, patient, time

---

### c. User Triggered Async Job - Export as CSV
**Location:** 
- Task: `backend/celery_tasks.py` (lines 100-137)
- Trigger endpoint: `backend/routes/patient.py` (lines 512-537)
- Frontend button: `frontend/index.html` (line 1485)
- Frontend handler: `frontend/assets/js/app.js` (lines 659-675)

**Implementation:**
- ✅ **CSV export with all required fields**:
  - date (appointment_date)
  - doctor (consulting doctor name)
  - diagnosis
  - treatment_notes
- ✅ **Triggered from patient dashboard**: Button "Export Full History"
- ✅ **Async batch job**: Uses Celery `.delay()` to run in background
- ✅ **Email alert on completion**: Sends email with CSV attachment
- ✅ **CSV file generation**: Saved to `backend/exports/` directory
- ✅ **Uses app context**: `with app.app_context():`

**API Endpoint:**
```
POST /api/patient/export-history
```

**Workflow:**
1. Patient clicks "Export Full History" button
2. Frontend calls `exportPatientHistory()` 
3. Backend triggers async Celery task: `export_patient_history_csv.delay(patient.id)`
4. Returns task_id immediately
5. Celery worker processes in background
6. Generates CSV file
7. Sends email with CSV attachment to patient
8. Returns success message

---

## ✅ PERFORMANCE AND CACHING

### Caching Implementation
**Location:** `backend/routes/admin.py` (lines 17-59)

**Implementation:**
- ✅ **In-memory cache**: Simple dictionary cache in `app.py` (line 38: `cache = {}`)
- ✅ **Cache expiry**: 5 minutes (300 seconds) for admin dashboard stats
- ✅ **Cache key**: `'admin_stats'`
- ✅ **Timestamp-based expiry**: Stores `(data, timestamp)` tuple
- ✅ **Cache invalidation**: Auto-expires after 5 minutes

**Cached Endpoint:**
```python
@admin_bp.route('/dashboard-stats', methods=['GET'])
@admin_required
def dashboard_stats():
    # Check cache first
    if cache_key in cache:
        cached_data, cached_time = cache[cache_key]
        if (datetime.now() - cached_time).total_seconds() < 300:
            return cached_data  # Return from cache
    
    # Fetch from DB if cache miss/expired
    # ... query database ...
    
    # Store in cache with timestamp
    cache[cache_key] = (stats, datetime.now())
```

**Performance Benefits:**
- Reduces database queries for frequently accessed admin dashboard
- 5-minute cache prevents excessive DB hits
- Simple implementation suitable for student project

---

## 📊 SUMMARY

| Requirement | Status | Location | Notes |
|------------|--------|----------|-------|
| **Daily Reminders** | ✅ COMPLETE | `celery_tasks.py:26-48` | Gmail SMTP, HTML emails |
| **Monthly Reports** | ✅ COMPLETE | `celery_tasks.py:51-97` | HTML reports with tables |
| **CSV Export** | ✅ COMPLETE | `celery_tasks.py:100-137` | Async job with email |
| **Dashboard Trigger** | ✅ COMPLETE | `index.html:1485` | Patient dashboard button |
| **Caching** | ✅ COMPLETE | `routes/admin.py:17-59` | 5-min expiry |
| **Cache Expiry** | ✅ COMPLETE | `routes/admin.py:29-30` | Timestamp-based |
| **API Performance** | ✅ COMPLETE | `routes/admin.py` | Cached dashboard stats |

---

## 🔧 CONFIGURATION

### Email Setup (.env file)
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
```

### Celery Beat Schedule (Demo Mode)
```python
# Daily reminders: every 2 minutes
sender.add_periodic_task(120.0, send_daily_reminders.s())

# Monthly reports: every 3 minutes  
sender.add_periodic_task(180.0, generate_monthly_report.s())
```

### Production Schedule (Change to)
```python
from celery.schedules import crontab

# Daily reminders at 8:00 AM
sender.add_periodic_task(
    crontab(hour=8, minute=0),
    send_daily_reminders.s()
)

# Monthly reports on 1st of month at 9:00 AM
sender.add_periodic_task(
    crontab(day_of_month=1, hour=9, minute=0),
    generate_monthly_report.s()
)
```

---

## ✅ ALL REQUIREMENTS MET

**Status:** 100% IMPLEMENTED ✅

All three backend jobs and performance/caching requirements are fully implemented and working.
