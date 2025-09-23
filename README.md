# Hospital Management System

A comprehensive Hospital Management System built with Flask (Backend) and Vue.js (Frontend) supporting three user roles: Admin, Doctor, and Patient.

## Features

### Admin Dashboard
- Manage registered doctors and patients
- View and manage all appointments
- Add new doctors to the system
- Search functionality for doctors, patients, and departments
- View patient history and treatment records

### Doctor Dashboard
- View upcoming appointments
- Manage assigned patients
- Update patient history and treatment records
- Set availability schedule (7-day calendar view)
- Complete appointments and add diagnoses

### Patient Dashboard
- Browse departments and doctors by specialization
- View doctor profiles and availability
- Book appointments with available doctors
- View upcoming appointments and medical history
- Cancel appointments

## Tech Stack

- **Backend**: Flask REST API with SQLAlchemy ORM
- **Frontend**: Vue.js 3 (CDN version) with Bootstrap 5
- **Database**: SQLite (auto-created programmatically)
- **Caching**: Redis
- **Background Jobs**: Celery with Redis broker
- **Authentication**: JWT tokens

## Project Structure

\`\`\`
hospital_management_system/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── init_db.py             # Database initialization script
│   ├── models/                # Database models
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── doctor.py
│   │   └── appointment.py
│   ├── routes/                # API endpoints
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── doctor.py
│   │   └── patient.py
│   ├── services/              # Business logic
│   │   ├── auth_service.py
│   │   └── appointment_service.py
│   ├── tasks/                 # Celery background tasks
│   │   └── celery_tasks.py
│   └── requirements.txt
├── frontend/
│   ├── index.html             # Main entry point (Jinja2 template)
│   ├── assets/
│   │   ├── css/
│   │   │   └── custom.css
│   │   └── js/
│   │       ├── app.js         # Main Vue application
│   │       ├── components/    # Vue components
│   │       │   ├── Login.js
│   │       │   ├── Register.js
│   │       │   ├── AdminDashboard.js
│   │       │   ├── DoctorDashboard.js
│   │       │   └── PatientDashboard.js
│   │       └── services/
│   │           └── api.js     # API service layer
└── README.md
\`\`\`

## Installation & Setup

### Prerequisites
- Python 3.8+
- Redis server
- Git

### Backend Setup

1. **Clone the repository**
\`\`\`bash
git clone <repository-url>
cd hospital_management_system
\`\`\`

2. **Create virtual environment**
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. **Install dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Start Redis server**
\`\`\`bash
# On Ubuntu/Debian
sudo systemctl start redis-server

# On macOS with Homebrew
brew services start redis

# On Windows, download and run Redis
\`\`\`

5. **Initialize database**
\`\`\`bash
python init_db.py
\`\`\`

6. **Start Flask application**
\`\`\`bash
python app.py
\`\`\`

The backend will be available at `http://localhost:5000`

### Celery Setup (Background Jobs)

1. **Start Celery worker** (in a new terminal)
\`\`\`bash
cd backend
source venv/bin/activate
celery -A app.celery worker --loglevel=info
\`\`\`

2. **Start Celery beat** (for scheduled tasks, in another terminal)
\`\`\`bash
cd backend
source venv/bin/activate
celery -A app.celery beat --loglevel=info
\`\`\`

## Default Login Credentials

### Admin
- **Username**: admin
- **Password**: admin123

### Sample Doctors
- **Username**: dr_smith, **Password**: doctor123
- **Username**: dr_johnson, **Password**: doctor123

### Patient Registration
Patients can register through the registration form on the frontend.

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - Patient registration
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### Admin Endpoints
- `GET /api/admin/dashboard-stats` - Dashboard statistics
- `GET /api/admin/doctors` - List all doctors
- `POST /api/admin/doctors` - Add new doctor
- `PUT /api/admin/doctors/<id>` - Update doctor
- `DELETE /api/admin/doctors/<id>` - Delete/deactivate doctor
- `GET /api/admin/patients` - List all patients
- `GET /api/admin/appointments` - List all appointments

### Doctor Endpoints
- `GET /api/doctor/dashboard` - Doctor dashboard data
- `GET /api/doctor/appointments` - Doctor's appointments
- `GET /api/doctor/patients` - Assigned patients
- `POST /api/doctor/patient-history` - Add patient treatment
- `PUT /api/doctor/availability` - Update availability schedule

### Patient Endpoints
- `GET /api/patient/dashboard` - Patient dashboard data
- `GET /api/patient/departments` - List departments
- `GET /api/patient/doctors` - List doctors by specialization
- `GET /api/patient/appointments` - Patient's appointments
- `POST /api/patient/appointments` - Book appointment
- `DELETE /api/patient/appointments/<id>` - Cancel appointment

## Background Jobs

### Celery Tasks
- **Daily Reminders**: Sends email reminders for next-day appointments
- **Monthly Reports**: Generates monthly performance reports for doctors
- **Patient History Export**: Exports patient treatment history to CSV
- **Appointment Notifications**: Real-time appointment status updates

## Database Schema

### Core Tables
- **users**: Authentication and user roles
- **patients**: Patient information and medical history
- **doctors**: Doctor profiles and specializations
- **appointments**: Appointment scheduling and status
- **treatments**: Treatment records and prescriptions
- **doctor_availability**: Doctor schedule management

## Frontend Architecture

### Vue.js Components
- **Simple CDN-based setup** (no build process required)
- **Component-based architecture** with global registration
- **Bootstrap 5** for responsive UI
- **Role-based navigation** and access control
- **Real-time updates** with API integration

### Key Features
- **Responsive design** works on desktop and mobile
- **Role-based dashboards** with different views for each user type
- **Interactive appointment booking** with availability checking
- **Search and filter** functionality
- **Modal dialogs** for forms and confirmations

## Development Guidelines

### Code Style
- **Student-friendly approach**: Clear, readable code with comments
- **Modular structure**: Separate concerns with blueprints and components
- **Error handling**: Comprehensive try-catch blocks with user feedback
- **Security**: JWT authentication and role-based access control

### Testing
- Manual testing of all user flows
- Role-based access verification
- Appointment booking conflict testing
- Responsive design testing

## Deployment

### Production Setup
1. **Environment Variables**
\`\`\`bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export JWT_SECRET_KEY=your-jwt-secret
export DATABASE_URL=your-database-url
export REDIS_URL=your-redis-url
\`\`\`

2. **Database Migration**
\`\`\`bash
python init_db.py
\`\`\`

3. **Start Services**
\`\`\`bash
# Flask app
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Celery worker
celery -A app.celery worker --loglevel=info

# Celery beat
celery -A app.celery beat --loglevel=info
\`\`\`

## Troubleshooting

### Common Issues
1. **Redis Connection Error**: Ensure Redis server is running
2. **Database Not Found**: Run `python init_db.py` to create tables
3. **JWT Token Expired**: Login again to get new token
4. **Appointment Booking Fails**: Check doctor availability and time conflicts

### Logs
- Flask logs: Check console output
- Celery logs: Check worker and beat process outputs
- Frontend errors: Check browser console

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

This project is for educational purposes. Feel free to use and modify as needed.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check browser console for frontend errors
4. Verify Redis and database connections
\`\`\`

```python file="" isHidden
