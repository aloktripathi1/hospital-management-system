# Setup Guide - Hospital Management System

Hey! This is a simple guide to get the project running on your machine.

## What You Need

- Python 3.8 or higher
- Redis Server (for background tasks)
- A web browser (Chrome, Firefox, etc.)

## Step 1: Backend Setup

First, go to the backend folder and install all the required packages:

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Create Database with Sample Data

Run this script to create the database and add some test data (admin, doctors, patients):

```bash
python seed_db.py
```

This will create:
- 1 Admin account (username: admin, password: admin123)
- 5 Doctors with different specializations
- 10 Patients
- Some sample appointments

## Step 3: Start the Backend Server

Now start the Flask server:

```bash
python app.py
```

Your backend will be running at `http://localhost:5000`

## Step 4: Start Frontend

Open another terminal and go to the frontend folder:

```bash
cd frontend
python -m http.server 3000
```

Your website will open at `http://localhost:3000`

## Step 5: Redis Setup (For Email Notifications)

If you want email notifications to work, install and start Redis:

**Install Redis (Ubuntu/WSL):**
```bash
sudo apt update
sudo apt install redis-server
```

**Start Redis:**
```bash
sudo service redis-server start
```

## Step 6: Start Background Workers (Optional)

These are needed for sending emails and reminders:

**Terminal 1 - Celery Worker:**
```bash
cd backend
celery -A celery_tasks worker --loglevel=info
```

**Terminal 2 - Celery Beat (Scheduler):**
```bash
cd backend
celery -A celery_tasks beat --loglevel=info
```

## Quick Summary

At minimum, you need 2 terminals:
1. **Backend:** `python app.py` (in backend folder)
2. **Frontend:** `python -m http.server 3000` (in frontend folder)

For full features (emails), you need:
3. Redis running in background
4. Celery worker
5. Celery beat

## Login Credentials

After running `seed_db.py`, you can login as:

**Admin:**
- Username: admin
- Password: admin123

**Doctors:**
- Username: dr_sharma / dr_verma / dr_patel / dr_singh / dr_kumar
- Password: doctor123

**Patients:**
- Username: patient1 / patient2 / patient3...
- Password: patient123
