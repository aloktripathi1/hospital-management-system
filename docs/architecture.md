# Project Architecture

This document explains how different parts of the project work together.

## How Everything Connects

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                            │
│                     http://localhost:3000                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTP Requests
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND SERVER                             │
│                   (Python HTTP Server)                           │
│                      Port: 3000                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Static Files: HTML, CSS, JavaScript (Vue.js)           │   │
│  │  - index.html                                            │   │
│  │  - assets/js/app.js                                      │   │
│  │  - assets/js/modules/*.js                                │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ AJAX/Fetch API Calls
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND SERVER                              │
│                     (Flask REST API)                             │
│                      Port: 5000                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Routes:                                                 │   │
│  │  - /api/auth/*      (Authentication)                     │   │
│  │  - /api/admin/*     (Admin operations)                   │   │
│  │  - /api/doctor/*    (Doctor operations)                  │   │
│  │  - /api/patient/*   (Patient operations)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────┬────────────┬──────────────┬────────────────────┬──────────┘
      │            │              │                    │
      │            │              │                    │
      ▼            ▼              ▼                    ▼
┌──────────┐ ┌──────────┐  ┌──────────┐      ┌─────────────────┐
│ SQLite   │ │  Redis   │  │  Celery  │      │    MailHog      │
│ Database │ │  Cache   │  │  Queue   │      │ (Email Testing) │
│          │ │          │  │          │      │                 │
│ - Users  │ │ Sessions │  │ Tasks:   │      │ SMTP: 1025      │
│ - Doctors│ │ & Cache  │  │ - Emails │      │ Web:  8025      │
│ - Patient│ │          │  │ - Report │      │                 │
│ - Appts  │ │Port:6379 │  │          │      │                 │
│ - Treats │ │          │  │          │      │                 │
└──────────┘ └──────────┘  └────┬─────┘      └────────▲────────┘
                                 │                     │
                                 │ Sends Email Jobs    │
                                 └─────────────────────┘
```

## Main Components

### 1. Frontend (What users see)
- **Location:** `frontend/` folder
- **What it does:** Shows the website to users
- **Main files:**
  - `index.html` - The main webpage
  - `custom.css` - Styling (colors, fonts, layout)
  - `js/app.js` - Main JavaScript file
  - `js/admin.js` - Admin dashboard code
  - `js/doctor.js` - Doctor dashboard code
  - `js/patient.js` - Patient dashboard code
  - `js/api.js` - Talks to backend
- **Runs on:** http://localhost:3000

### 2. Backend (Brain of the app)
- **Location:** `backend/` folder
- **What it does:** Handles all the logic and data
- **Main files:**
  - `app.py` - Main Flask server
  - `routes/` - Different API endpoints
    - `auth.py` - Login/Register
    - `admin.py` - Admin features
    - `doctor.py` - Doctor features
    - `patient.py` - Patient features
  - `models/` - Database table definitions
  - `database.py` - Database connection
- **Runs on:** http://localhost:5000

### 3. Database (Where data is stored)
- **Type:** SQLite (simple file-based database)
- **Location:** `backend/instance/hospital.db`
- **What's stored:**
  - User accounts (admin, doctors, patients)
  - Doctor information (name, specialization, experience)
  - Patient information (name, age, medical history)
  - Appointments (who, when, status)
  - Treatment records (diagnosis, medicines, notes)
  - Doctor availability (morning/evening slots)

### 4. Background Jobs (Celery)
- **What it does:** Sends emails in background
- **Tasks:**
  - Appointment confirmation emails
  - Appointment reminder emails (24 hours before)
  - Monthly reports for doctors
- **Needs:** Redis to be running

### 5. Redis (Message Queue)
- **What it does:** Helps Celery send background tasks
- **Runs on:** Port 6379
- **Not required** for basic app, only for emails

## How Things Work Together

### Example: Patient Books an Appointment

1. Patient fills form and clicks "Book Appointment"
2. Frontend (JavaScript) sends data to Backend
3. Backend checks if slot is available
4. Backend saves appointment in Database
5. Backend sends confirmation email (via Celery)
6. Frontend shows success message to patient
7. Doctor can see the new appointment in their dashboard

### Example: Doctor Updates Treatment

1. Doctor clicks on appointment
2. Doctor fills diagnosis, medicines, notes
3. Frontend sends data to Backend
4. Backend saves treatment record in Database
5. Backend marks appointment as "completed"
6. Patient can see treatment history in their dashboard

## UI Design

The app uses a **dark professional theme** with:
- **Primary Color:** Dark slate (#0f172a)
- **Accent Color:** Gold gradient for highlights
- **Modern Design:** Rounded corners, shadows, smooth animations
- **Responsive:** Works on desktop and mobile

### Key Features:
- Professional hero section on homepage
- Modern login/register pages with branding
- Clean dashboards for admin, doctor, patient
- Modal confirmations (instead of ugly alerts)
- Icons from Bootstrap Icons
- Smooth transitions and hover effects

## User Roles

### Admin
- Manage doctors (add, edit, blacklist)
- Manage patients (edit, blacklist, view history)
- View all appointments
- Reschedule/cancel appointments
- See overall statistics

### Doctor
- View assigned patients
- Manage appointments
- Update treatment records (diagnosis, prescription, notes)
- Mark appointments as completed
- Set availability (morning/evening slots)
- View patient treatment history

### Patient
- Book appointments with available doctors
- View upcoming appointments
- View treatment history
- Update profile information
- Cancel appointments

## Data Flow

```
┌──────────┐
│  ADMIN   │
└────┬─────┘
     │ Creates/Manages
     ▼
┌──────────┐     Schedules      ┌──────────┐
│  DOCTOR  │◄──────────────────►│AVAILABILITY│
└────┬─────┘                    └──────────┘
     │                                ▲
     │ Treats                         │
     ▼                                │
┌──────────┐     Books          ┌────┴──────┐
│ PATIENT  │────────────────────►│APPOINTMENT│
└────┬─────┘                    └────┬──────┘
     │                               │
     │ Has                           │ Contains
     ▼                               ▼
┌──────────┐                    ┌──────────┐
│TREATMENT │◄───────────────────│ DOCTOR   │
│ RECORD   │   Creates          │          │
└──────────┘                    └──────────┘
```

## 🔐 Security Flow

```
1. User Login
   └─> POST /api/auth/login
       └─> Verify credentials
           └─> Create session
               └─> Store in Redis
                   └─> Return session cookie

2. Authenticated Request
   └─> Send with session cookie
       └─> Decorator checks session
           └─> Verify role
               └─> Allow/Deny access
```

## ⚡ Background Task Flow

```
1. Trigger Event (e.g., appointment booked)
   └─> Backend creates task
       └─> Push to Redis queue
           └─> Celery worker picks up
               └─> Execute task
                   └─> Send email via MailHog
                       └─> Task complete
```

## 🚀 Startup Sequence

### Using tmux:

```
1. start_tmux.sh executed
   │
   ├─> Window 0: redis-server starts
   │   └─> Port 6379 open
   │
   ├─> Window 1: docker run mailhog
   │   └─> Ports 1025, 8025 open
   │
   ├─> Window 2: python3 app.py
   │   └─> Port 5000 open
   │   └─> Connects to Redis
   │   └─> Creates database tables
   │
   ├─> Window 3: celery worker
   │   └─> Connects to Redis
   │   └─> Ready for tasks
   │
   └─> Window 4: http.server
       └─> Port 3000 open
       └─> Serves frontend files

All services ready! ✅
```

## 📊 Port Mapping

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Frontend | 3000 | HTTP | Serve static files |
| Backend | 5000 | HTTP | REST API |
| Redis | 6379 | TCP | Message broker & cache |
| MailHog SMTP | 1025 | SMTP | Receive emails |
| MailHog Web | 8025 | HTTP | View emails |

## 🔧 Technology Stack

### Frontend
- **Vue.js 3** - Reactive framework
- **Bootstrap 5** - UI components
- **Bootstrap Icons** - Icons
- **Vanilla JS** - No build tools needed

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-CORS** - Cross-origin requests
- **Werkzeug** - Password hashing

### Background Tasks
- **Celery** - Task queue
- **Redis** - Message broker
- **MailHog** - Email testing

### Database
- **SQLite** - File-based database

## 📝 Notes

- All services run on localhost
- No internet connection required after initial setup
- All emails are caught by MailHog (not sent externally)
- Redis is used for both Celery and session storage
- Frontend is pure HTML/CSS/JS (no build process)

---

**This architecture provides:**
✅ Separation of concerns
✅ Scalable background processing  
✅ Secure authentication
✅ Real-time email testing
✅ Easy development setup
