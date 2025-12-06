# Windows WSL Setup Guide - Hospital Management System

## 🪟 Running the Project on Windows with WSL

This guide shows you how to run the Hospital Management System with Celery email functionality on Windows using WSL (Windows Subsystem for Linux).

---

## 📋 Prerequisites

### 1. Install WSL2 on Windows
Open PowerShell as Administrator and run:
```powershell
wsl --install
```

Restart your computer when prompted.

### 2. Install Ubuntu on WSL
```powershell
wsl --install -d Ubuntu-22.04
```

Create a username and password when prompted.

### 3. Update WSL Ubuntu
```bash
sudo apt update
sudo apt upgrade -y
```

---

## 🔧 Install Required Software in WSL

### 1. Install Python 3 and pip
```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 2. Install Redis Server
```bash
sudo apt install redis-server -y
```

### 3. Install Git (if not installed)
```bash
sudo apt install git -y
```

---

## 📂 Clone and Setup Project

### 1. Navigate to your project directory
```bash
# Access Windows files from WSL
cd /mnt/c/Users/YourUsername/Documents/

# OR clone from GitHub
git clone https://github.com/aloktripathi1/hospital-management-system.git
cd hospital-management-system
```

### 2. Install Python dependencies
```bash
cd backend
pip3 install -r requirements.txt
```

**If you get any errors**, install packages individually:
```bash
pip3 install Flask==2.3.3
pip3 install Flask-SQLAlchemy==3.0.5
pip3 install Flask-CORS==4.0.0
pip3 install Flask-JWT-Extended==4.5.3
pip3 install Flask-Mail==0.9.1
pip3 install Werkzeug==2.3.7
pip3 install celery==5.3.4
pip3 install redis==5.0.1
pip3 install python-dotenv==1.0.0
```

---

## 📧 Configure Email Settings

### 1. Get Gmail App Password

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already enabled)
3. Go to https://myaccount.google.com/apppasswords
4. Select app: **Mail**
5. Select device: **Other (Custom name)** → Type "Hospital System"
6. Click **Generate**
7. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### 2. Edit .env file
```bash
cd /mnt/c/path/to/hospital-management-system/backend
nano .env
```

Update with your credentials:
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=abcdefghijklmnop
```

Save: `Ctrl+O`, `Enter`, then exit: `Ctrl+X`

---

## 🚀 Running the Application

You need **4 terminal windows** - open them all in WSL:

### Terminal 1: Redis Server
```bash
cd /mnt/c/path/to/hospital-management-system
redis-server
```

**Expected output:**
```
Ready to accept connections on port 6379
```

**Keep this terminal running!**

---

### Terminal 2: Flask Backend (Web Server)
```bash
cd /mnt/c/path/to/hospital-management-system/backend
python3 app.py
```

**Expected output:**
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

**Keep this terminal running!**

---

### Terminal 3: Celery Worker
```bash
cd /mnt/c/path/to/hospital-management-system/backend
celery -A celery_tasks worker --loglevel=info --pool=solo
```

**Note:** The `--pool=solo` flag is **REQUIRED** for Windows/WSL!

**Expected output:**
```
celery@hostname ready.
```

**Keep this terminal running!**

---

### Terminal 4: Celery Beat (Scheduler)
```bash
cd /mnt/c/path/to/hospital-management-system/backend
celery -A celery_tasks beat --loglevel=info
```

**Expected output:**
```
Scheduler: Sending due task demo-daily-reminders
Scheduler: Sending due task demo-monthly-reports
```

**Keep this terminal running!**

---

## 🌐 Access the Application

Open your Windows browser:
```
http://localhost:5000
```

OR

```
http://127.0.0.1:5000
```

---

## 📧 Testing Email Functionality

### 1. Create Test Data
Login as admin:
- Username: `admin`
- Password: `admin123`

### 2. Create a Patient with TODAY's Appointment
1. Go to **Patients** → Add patient with valid email
2. Go to **Appointments** → Create appointment for **TODAY**
3. Make sure appointment status is **"booked"**

### 3. Watch the Emails Being Sent

In **Terminal 3 (Celery Worker)**, you'll see:
```
[2025-10-30 05:15:00] Task celery_tasks.send_daily_reminders
Email sent to patient@example.com: Appointment Reminder - 2025-10-30
```

In **Terminal 4 (Celery Beat)**, you'll see:
```
Scheduler: Sending due task demo-daily-reminders (120.0s)
Scheduler: Sending due task demo-monthly-reports (180.0s)
```

### 4. Check Your Email Inbox
- Patients will receive appointment reminders
- Doctors will receive monthly reports
- All emails are HTML formatted with nice styling!

---

## 🐛 Common Issues & Solutions

### ❌ Issue: "redis.exceptions.ConnectionError"
**Solution:**
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start it:
redis-server
```

---

### ❌ Issue: "ModuleNotFoundError: No module named 'flask_mail'"
**Solution:**
```bash
cd /mnt/c/path/to/hospital-management-system/backend
pip3 install Flask-Mail==0.9.1
```

---

### ❌ Issue: Celery worker won't start on Windows
**Solution:**
Always use `--pool=solo` flag:
```bash
celery -A celery_tasks worker --loglevel=info --pool=solo
```

---

### ❌ Issue: "SMTPAuthenticationError"
**Solution:**
1. Make sure you're using **App Password**, not your regular Gmail password
2. Check 2-Factor Authentication is enabled on Gmail
3. Verify .env file has correct credentials with no extra spaces

---

### ❌ Issue: Emails not sending
**Solution:**
1. Check Celery Worker logs for errors
2. Verify patient/doctor has email address in database
3. Check appointment date is TODAY
4. Make sure appointment status is "booked"

---

### ❌ Issue: "Permission denied" in WSL
**Solution:**
```bash
# Make sure you're in the right directory
cd /mnt/c/Users/YourUsername/Documents/hospital-management-system

# OR use WSL home directory
cp -r /mnt/c/Users/YourUsername/Documents/hospital-management-system ~
cd ~/hospital-management-system
```

---

## 🔄 Quick Start Script

Create a file `start.sh` in the backend folder:

```bash
#!/bin/bash

# Start Redis
redis-server &

# Wait for Redis to start
sleep 2

# Start Celery Worker
celery -A celery_tasks worker --loglevel=info --pool=solo &

# Wait for worker to start
sleep 3

# Start Celery Beat
celery -A celery_tasks beat --loglevel=info &

# Wait for beat to start
sleep 2

# Start Flask app
python3 app.py
```

Make it executable and run:
```bash
chmod +x start.sh
./start.sh
```

**Note:** This runs everything in background. Check logs for errors.

---

## 🛑 Stopping the Application

### Stop individual terminals:
Press `Ctrl+C` in each terminal

### Kill all processes:
```bash
# Kill Redis
pkill redis-server

# Kill Celery
pkill -f celery

# Kill Flask
pkill -f "python3 app.py"
```

---

## 📊 Demo Schedule (Current Settings)

- **Daily Reminders**: Every **2 minutes** (120 seconds)
- **Monthly Reports**: Every **3 minutes** (180 seconds)

### Switch to Production Schedule

Edit `backend/celery_tasks.py`:

**Comment out demo schedules:**
```python
# 'demo-daily-reminders': {
#     'task': 'celery_tasks.send_daily_reminders',
#     'schedule': 120.0,
# },
# 'demo-monthly-reports': {
#     'task': 'celery_tasks.generate_monthly_report',
#     'schedule': 180.0,
# },
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

## ✅ Verification Checklist

- [ ] WSL2 installed and working
- [ ] Python 3 and pip installed
- [ ] Redis server installed
- [ ] All dependencies installed (`pip3 install -r requirements.txt`)
- [ ] `.env` file created with Gmail credentials
- [ ] Redis server running (Terminal 1)
- [ ] Flask app running (Terminal 2)
- [ ] Celery worker running with `--pool=solo` (Terminal 3)
- [ ] Celery beat running (Terminal 4)
- [ ] Can access `http://localhost:5000` in browser
- [ ] Test patient created with email
- [ ] Test appointment created for TODAY
- [ ] Emails being sent successfully

---

## 🎯 Tips for WSL Users

1. **Access Windows files from WSL:**
   ```bash
   cd /mnt/c/Users/YourUsername/Documents/
   ```

2. **Access WSL files from Windows:**
   ```
   \\wsl$\Ubuntu-22.04\home\username\
   ```

3. **Copy files between Windows and WSL:**
   ```bash
   cp /mnt/c/path/to/file /home/username/destination/
   ```

4. **Edit files with Windows tools:**
   - Use VS Code: Install "Remote - WSL" extension
   - Open folder in WSL: `code .`

5. **Check WSL version:**
   ```bash
   wsl -l -v
   ```

---

## 🔐 Security Notes

- Never commit `.env` file to Git (already in .gitignore)
- Use App Passwords, not regular Gmail password
- Keep your email credentials secure
- Disable 2FA App Password when done testing

---

## 📱 Additional Resources

- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **WSL Documentation:** https://docs.microsoft.com/en-us/windows/wsl/
- **Celery Documentation:** https://docs.celeryq.dev/
- **Redis Documentation:** https://redis.io/docs/

---

**Happy Testing! 🎉**

If you encounter any issues, check the Celery Worker logs first - they show detailed error messages!
