# ⚡ Quick Start - Viva Demo in 5 Minutes

## 🚀 Start All Services

```bash
# Terminal 1 - Redis
redis-server

# Terminal 2 - MailHog
mailhog

# Terminal 3 - Flask
cd backend && python3 app.py

# Terminal 4 - Celery Worker
cd backend && celery -A celery_tasks.celery worker --loglevel=info --pool=solo

# Terminal 5 - Celery Beat
cd backend && celery -A celery_tasks.celery beat --loglevel=info
```

## 🌐 Open in Browser

1. **MailHog (Main Demo Window):** http://localhost:8025
2. **Hospital App:** http://localhost:5000

## 🎯 Quick Demo Steps

### 1. Daily Reminder (1 min)
```bash
# Create patient with email: patient@example.com
# Create appointment for TODAY with status "booked"
# Wait 2 min OR run: python3 trigger_tasks.py (option 1)
# Check MailHog - Email appears!
```

### 2. CSV Export (2 min) ⭐ MAIN DEMO
```bash
cd backend
python3 trigger_tasks.py
# Choose option 3
# Enter patient ID: 1
# Check MailHog - Email with CSV attachment!
# Show file: ls -lh exports/
# Open CSV to show medical history
```

### 3. Monthly Report (1 min)
```bash
# Run: python3 trigger_tasks.py (option 2)
# Check MailHog - Report with statistics!
```

## ✅ What to Show

1. MailHog web interface (real emails!)
2. Professional HTML formatting
3. CSV file attached to email
4. CSV opened in Excel (complete medical history)
5. Celery worker processing logs

## 🎤 Key Points

- "Real SMTP emails, not console prints"
- "Asynchronous background processing"
- "CSV with complete patient history"
- "Production-ready with error handling"
- "Scalable architecture with Redis & Celery"

## 📧 Email Features

✅ HTML formatted
✅ Professional styling
✅ File attachments
✅ Automated scheduling
✅ Visible in MailHog web UI

---

**REMEMBER:** Open MailHog (http://localhost:8025) FIRST - that's what you'll show!
