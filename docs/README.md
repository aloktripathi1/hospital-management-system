# Hospital Management System
## Student Academic Project

A simple Hospital Management System built with Flask (Backend) and Vue.js (Frontend) supporting three user roles: Admin, Doctor, and Patient. This project demonstrates basic web development concepts including user authentication, database operations, and role-based access control.

**Project Type**: Academic/Educational  
**Level**: Undergraduate Computer Science  
**Duration**: Semester Project  

## 🎯 Project Overview

This system manages three types of users:
- **Admin**: Manages doctors and patients
- **Doctor**: Views appointments and patient records
- **Patient**: Books appointments and views medical history

## 🛠️ Technologies Used

- **Backend**: Python Flask (Simple web framework)
- **Frontend**: HTML, CSS, JavaScript (Vanilla JS with Bootstrap)
- **Database**: SQLite (File-based database)
- **Background Tasks**: Celery (For notifications)
- **Authentication**: Simple session-based login

## 📁 Complete Project Structure

```
hospital-management-system/
├── backend/                           # Python Flask Backend
│   ├── app.py                        # Main Flask application entry point
│   ├── config.py                     # Application configuration settings
│   ├── database.py                   # Database connection and setup
│   ├── decorators.py                 # Custom decorators for authentication
│   ├── init_db.py                    # Database initialization script
│   ├── requirements.txt              # Python package dependencies
│   │
│   ├── instance/                     # Instance-specific files
│   │   └── hospital-management.db    # SQLite database file
│   │
│   ├── models/                       # Database Models (SQLAlchemy)
│   │   ├── __init__.py              # Models package initialization
│   │   ├── user.py                  # User authentication model
│   │   ├── patient.py               # Patient information model
│   │   ├── doctor.py                # Doctor profile model
│   │   ├── department.py            # Medical departments model
│   │   ├── appointment.py           # Appointment scheduling model
│   │   └── treatment.py             # Treatment records model
│   │
│   ├── routes/                      # API Route Handlers
│   │   ├── __init__.py              # Routes package initialization
│   │   ├── auth.py                  # Authentication endpoints
│   │   ├── admin.py                 # Admin dashboard APIs
│   │   ├── doctor.py                # Doctor functionality APIs
│   │   └── patient.py               # Patient functionality APIs
│   │
│   ├── services/                    # Business Logic Services
│   │   ├── __init__.py              # Services package initialization
│   │   ├── auth_service.py          # Authentication logic
│   │   └── appointment_service.py   # Appointment management logic
│   │
│   └── tasks/                       # Background Task Processing
│       ├── __init__.py              # Tasks package initialization
│       └── celery_tasks.py          # Celery background jobs
│
├── frontend/                         # Web User Interface
│   ├── index.html                   # Main HTML application file
│   │
│   └── assets/                      # Static Assets
│       ├── css/                     # Stylesheets
│       │   └── custom.css           # Custom CSS styles
│       │
│       └── js/                      # JavaScript Files
│           ├── app.js               # Main Vue.js application
│           │
│           ├── modules/             # JavaScript Modules
│           │   ├── admin.js         # Admin dashboard functionality
│           │   ├── doctor.js        # Doctor interface logic
│           │   ├── patient.js       # Patient interface logic
│           │   └── utils.js         # Utility functions
│           │
│           └── services/            # API Service Layer
│               └── api.js           # HTTP API communication
│
├── tests/                           # Test Files
│   └── api/                         # API Integration Tests
│       ├── test_patient_booking.py  # Patient booking test scenarios
│       └── test_slots.py            # Appointment slot testing
│
├── docs/                            # Documentation
│   ├── README.md                    # Main project documentation (this file)
│   ├── FUNCTIONALITY_ASSESSMENT.md  # Feature assessment document
│   └── SIMPLE_STUDENT_IMPLEMENTATION.md  # Implementation notes
│
├── .gitignore                       # Git ignore rules
└── .gitattributes                   # Git attributes configuration
```

### 📂 Directory Explanations

**Backend Structure:**
- `app.py` - Main Flask server that starts the application
- `models/` - Database table definitions using SQLAlchemy ORM
- `routes/` - API endpoints organized by user role (admin, doctor, patient)
- `services/` - Business logic separated from route handlers
- `tasks/` - Background jobs for notifications and reports
- `instance/` - Contains the SQLite database file

**Frontend Structure:**
- `index.html` - Single-page application with all HTML templates
- `assets/js/app.js` - Main Vue.js application with components
- `assets/js/modules/` - Separate JavaScript files for each user role
- `assets/js/services/api.js` - Handles all HTTP requests to backend
- `assets/css/custom.css` - Custom styling on top of Bootstrap

**Supporting Files:**
- `tests/api/` - Python scripts to test API functionality
- `docs/` - Project documentation and development notes
- `requirements.txt` - Lists all Python packages needed
- `.gitignore` - Tells Git which files to ignore (like database files)

## 🚀 How to Run the Project

### Step 1: Install Python Requirements
```bash
# Navigate to the backend folder
cd backend

# Install Python packages
pip install -r requirements.txt
```

### Step 2: Setup Database
```bash
# Create the database tables
python init_db.py
```

### Step 3: Start the Application
```bash
# Run the Flask server
python app.py
```

### Step 4: Access the Application
- Open your web browser
- Go to: `http://localhost:5000`
- The application will load automatically!

## 👤 Login Credentials

### For Testing the System:

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Doctor Account:**
- Username: `dr_smith`
- Password: `doctor123`

**Patient Account:**
- You can register as a new patient
- Or use existing patient accounts created during development

## 🎯 Key Features Implemented

### 1. User Authentication
- Simple login/logout system
- Role-based access (Admin, Doctor, Patient)
- Session management

### 2. Admin Functions
- Add new doctors to the system
- View all patients and appointments  
- Manage user accounts

### 3. Doctor Functions
- View assigned appointments
- Update patient treatment records
- Manage availability schedule

### 4. Patient Functions  
- Browse available doctors
- Book appointments
- View personal medical history
- Cancel appointments

### 5. Background Tasks
- Daily appointment reminders
- Monthly report generation
- CSV export functionality

## 💻 Technical Implementation

### Database Design
- **SQLite Database** (simple file-based storage)
- **5 Main Tables**: Users, Patients, Doctors, Appointments, Treatments
- **Relationships**: Foreign keys connecting related data

### Backend Architecture  
- **Flask Framework**: Lightweight Python web framework
- **SQLAlchemy ORM**: Database operations made simple
- **Route-based API**: Organized endpoints for different functionalities
- **Session Management**: Simple login/logout handling

### Frontend Design
- **HTML Templates**: Server-rendered pages
- **Bootstrap CSS**: Professional styling framework  
- **Vanilla JavaScript**: Client-side interactivity
- **Responsive Design**: Works on mobile and desktop

## 📚 Learning Outcomes

This project demonstrates:

1. **Web Development Fundamentals**
   - HTTP request/response cycle
   - Server-side routing
   - Database integration

2. **Python Programming**
   - Object-oriented design
   - File handling and data processing
   - Error handling and validation

3. **Database Management**
   - Table design and relationships
   - CRUD operations (Create, Read, Update, Delete)
   - Data validation and integrity

4. **User Interface Design**
   - Responsive web design principles
   - Form handling and validation
   - User experience considerations

## 🛠️ How to Modify/Extend

### Adding New Features:
1. **Backend**: Add new routes in the `routes/` folder
2. **Frontend**: Modify HTML templates and JavaScript
3. **Database**: Update models in the `models/` folder

### Common Enhancements Students Can Make:
- Add new user roles (e.g., Nurse, Pharmacist)
- Implement email notifications
- Add appointment calendar view
- Create patient history reports
- Add medicine inventory management

## ⚠️ Important Notes for Students

- **Keep It Simple**: This is designed as a learning project
- **Code Comments**: All major functions are documented
- **Error Handling**: Basic validation is implemented
- **Security**: Basic authentication (suitable for academic use)
- **Database**: All data is stored locally in SQLite file

## 📋 Project Checklist

- ✅ User registration and login
- ✅ Role-based access control  
- ✅ Appointment booking system
- ✅ Patient medical records
- ✅ Doctor availability management
- ✅ Admin dashboard functionality
- ✅ Background task processing
- ✅ Responsive web design

## 🎓 Academic Compliance

This project is designed for educational purposes and demonstrates:
- Basic web development concepts
- Database design principles  
- User interface design
- Simple backend architecture
- Student-appropriate complexity level

**Perfect for**: Computer Science coursework, web development assignments, database projects, and academic presentations.
\`\`\`

```python file="" isHidden
