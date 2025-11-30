# 🏥 Hospital Management System (HMS)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.3-green)
![Vue.js](https://img.shields.io/badge/vue.js-3.x-success)

## 📋 Project Overview

The **Hospital Management System (HMS)** is a comprehensive web-based application designed to streamline the operational workflows of healthcare facilities. It provides a unified platform for **Administrators**, **Doctors**, and **Patients** to manage appointments, medical records, and hospital resources efficiently.

This system replaces manual paperwork with a digital solution, ensuring data accuracy, faster retrieval of patient history, and seamless scheduling.

---

## 🎯 Motivation

Healthcare facilities often struggle with appointment conflicts, lost patient records, and inefficient doctor scheduling. This project aims to solve these problems by providing:
*   **Centralized Data:** A single source of truth for patient and doctor information.
*   **Conflict-Free Scheduling:** Intelligent slot management to prevent double-booking.
*   **Accessibility:** A patient portal for self-service booking and history viewing.
*   **Efficiency:** Automated administrative tasks to reduce workload on staff.

---

## ✨ Key Features

### 🔐 Authentication & Security
*   **Role-Based Access Control (RBAC):** Distinct portals for Admins, Doctors, and Patients.
*   **Secure Login:** JWT-based authentication and password hashing.

### 👨‍💼 Admin Portal
*   **Dashboard Analytics:** Real-time stats on doctors, patients, and appointments.
*   **User Management:** Add/Edit/Blacklist doctors and patients.
*   **Appointment Oversight:** View, reschedule, or cancel any appointment.
*   **History Tracking:** View comprehensive appointment history for any doctor or patient.

### 👨‍⚕️ Doctor Portal
*   **Schedule Management:** View upcoming appointments and manage availability.
*   **Patient Records:** Access patient medical history and past treatments.
*   **Consultation:** Record diagnoses, prescriptions, and treatment notes.

### 🏥 Patient Portal
*   **Easy Booking:** Intuitive 4-step booking process (Department -> Doctor -> Date -> Time).
*   **Smart Slots:** View real-time availability with 1-hour slot precision.
*   **Medical History:** View past appointments, prescriptions, and diagnoses.
*   **Doctor Profiles:** View detailed doctor information (experience, fees, qualifications) via interactive modals before booking.

---

## 🚀 Recent Updates
*   **Enhanced UI/UX:** Implemented Bootstrap Modals for smoother interactions (Rescheduling, Canceling, Doctor Profiles).
*   **Improved Scheduling:** Added 1-hour slot precision and past-time booking constraints.
*   **Admin Controls:** Fixed rescheduling logic and added confirmation dialogs.

## 🏗️ Architecture

The project follows a **Client-Server Architecture** with a RESTful API backend and a reactive frontend.

### Tech Stack
*   **Backend:** Python (Flask)
    *   **ORM:** SQLAlchemy (SQLite)
    *   **Async Tasks:** Celery + Redis (for background jobs like emails)
    *   **Auth:** Flask-JWT-Extended
*   **Frontend:** HTML5, CSS3, JavaScript (Vue.js via CDN), Bootstrap 5
*   **Database:** SQLite (Development).

### System Design
*   **Models:** `User`, `Doctor`, `Patient`, `Appointment`, `Treatment`, `DoctorAvailability`.
*   **API:** REST endpoints serving JSON data.
*   **Frontend:** Single-Page Application (SPA) feel using Vue.js components mounted on HTML templates.

---

## 📂 Project Structure

```bash
hospital-management-system/
├── backend/                # Flask Application
│   ├── models/             # Database Models (User, Doctor, Appointment, etc.)
│   ├── routes/             # API Endpoints (Auth, Admin, Doctor, Patient)
│   ├── app.py              # Application Entry Point
│   ├── database.py         # DB Configuration
│   ├── celery_tasks.py     # Background Tasks
│   └── requirements.txt    # Python Dependencies
├── frontend/               # Client-Side Application
│   ├── js/                 # Vue.js Components (admin.js, patient.js, etc.)
│   ├── css/                # Custom Styles
│   └── index.html          # Main Entry HTML
├── docs/                   # Documentation
├── tests/                  # Unit & Integration Tests
└── API_SHOWCASE.yaml       # API Specification
```

---

## 🚀 Installation Guide

### Prerequisites
*   Python 3.8+
*   Redis (for Celery tasks)
*   Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/hospital-management-system.git
cd hospital-management-system
```

### Step 2: Backend Setup
Create a virtual environment and install dependencies.
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Environment Configuration
Create a `.env` file in the `backend/` directory:
```env
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=sqlite:///hospital.db
JWT_SECRET_KEY=your_jwt_secret
CELERY_BROKER_URL=redis://localhost:6379/0
MAIL_SERVER=smtp.gmail.com
# ... other mail settings
```

### Step 4: Initialize Database
```bash
python init_db.py
```

### Step 5: Run the Application
Start the Flask server:
```bash
python app.py
```
*The API will run at `http://localhost:5000`*

### Step 6: Start Frontend
Since the frontend is static, you can serve it using Python's http server or open `frontend/index.html` directly (though running via the Flask static folder is recommended).
*Access the app at `http://localhost:5000/` (Flask serves the frontend).*

---

## 📖 Usage Instructions

### 1. Admin Access
*   **Login:** Use default credentials (if seeded) or create a superuser via script.
*   **Actions:** Go to "Doctors" tab to onboard new medical staff. Go to "Appointments" to oversee hospital schedule.

### 2. Patient Booking Flow
1.  Register/Login as a Patient.
2.  Click "Book Appointment".
3.  Select Department (e.g., Cardiology).
4.  Choose a Doctor (view profile for details).
5.  Select Date.
6.  Pick an available **1-hour slot** (e.g., 09:00 AM - 10:00 AM).
7.  Confirm Booking.

### 3. Doctor Interaction
1.  Login as Doctor.
2.  Set Availability (Morning/Evening slots).
3.  View "Today's Appointments".
4.  Click "Treat" to add diagnosis and prescription.

---

## 🧪 Testing

Run the test suite to ensure system stability.
```bash
cd tests
pytest
```

---

## 🗺️ Roadmap

*   [x] Core Appointment Booking
*   [x] Admin Dashboard & Analytics
*   [x] Doctor History & Profiles
*   [x] 1-Hour Slot System
*   [ ] Email/SMS Notifications (Integration ready)
*   [ ] Payment Gateway Integration
*   [ ] Pharmacy Management Module
*   [ ] Telemedicine Video Integration

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🙏 Acknowledgements

*   **Flask** for the robust backend framework.
*   **Vue.js** for the reactive user interface.
*   **Bootstrap** for the responsive design.
*   **FontAwesome / Bootstrap Icons** for the iconography.
