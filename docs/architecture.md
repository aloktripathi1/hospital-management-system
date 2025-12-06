# Hospital Management System - Architecture Overview

## 🏗️ System Architecture

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

## 📦 Component Details

### 1. Frontend (Port 3000)
- **Technology:** Vue.js 3 (CDN), Bootstrap 5
- **Purpose:** User interface
- **Files:**
  - `index.html` - Main application page
  - `assets/js/app.js` - Main Vue.js application
  - `assets/js/modules/` - Modular components (admin, doctor, patient)
  - `assets/js/services/api.js` - API communication layer

### 2. Backend (Port 5000)
- **Technology:** Flask (Python)
- **Purpose:** REST API, Business Logic
- **Components:**
  - `app.py` - Main Flask application
  - `routes/` - API endpoints (auth, admin, doctor, patient)
  - `models/` - Database models (SQLAlchemy)
  - `decorators.py` - Authentication & authorization

### 3. Database (SQLite)
- **File:** `instance/hospital.db`
- **Tables:**
  - `users` - Login credentials
  - `patients` - Patient information
  - `doctors` - Doctor profiles
  - `appointments` - Appointment bookings
  - `treatments` - Medical records
  - `doctor_availability` - Doctor schedules

### 4. Redis (Port 6379)
- **Purpose:** 
  - Message broker for Celery
  - Session storage
  - Caching (dashboard stats)
- **Start:** `redis-server`

### 5. Celery Worker
- **Purpose:** Background task processing
- **Tasks:**
  - `send_appointment_confirmation` - Email confirmations
  - `send_appointment_reminder` - 24hr reminders
  - `send_monthly_report` - Doctor reports
- **Start:** `celery -A celery_tasks.celery worker`

### 6. MailHog (Ports 1025, 8025)
- **Purpose:** Email testing
- **SMTP Port:** 1025 (receives emails)
- **Web UI:** 8025 (view emails)
- **Start:** `docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog`

## 🔄 Request Flow

### Example: Patient Books Appointment

```
1. User clicks "Book Appointment" in browser
   └─> Frontend (Vue.js)
       
2. Frontend sends POST to /api/patient/appointments
   └─> Backend (Flask)
       
3. Backend validates and saves to database
   └─> SQLite Database
       
4. Backend queues email task
   └─> Redis Queue
       
5. Celery worker picks up task
   └─> Celery Worker
       
6. Worker sends email via SMTP
   └─> MailHog (catches email)
       
7. Backend returns success response
   └─> Frontend updates UI
       
8. User sees confirmation message
```

## 🌊 Data Flow

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
