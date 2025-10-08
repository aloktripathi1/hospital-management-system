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

## 📁 Project Structure

```
hospital-management-system/
├── backend/                    # Python Flask application
│   ├── app.py                 # Main application file
│   ├── models/                # Database models
│   ├── routes/                # API endpoints
│   └── requirements.txt       # Python dependencies
├── frontend/                   # Web interface
│   ├── index.html             # Main HTML file
│   └── assets/                # CSS and JavaScript files
└── docs/                      # Project documentation
```

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
