# 🏥 Hospital Management System

A simple web app for managing hospital appointments, doctors, and patients.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.3-green)
![Vue.js](https://img.shields.io/badge/vue.js-3.x-success)

## What is this project?

This is a hospital management system I built for managing appointments between doctors and patients. It has three types of users:
- **Admin** - Manages doctors and patients
- **Doctors** - View appointments and update treatment records
- **Patients** - Book appointments and view medical history

## Why I made this

Most hospitals still use paper registers or complicated software. I wanted to make something simple that:
- Lets patients book appointments online
- Helps doctors see their schedule easily
- Gives admins control over everything
- Keeps all medical records in one place

## Features

### For Patients
- Register and login
- Book appointments (choose doctor, date, time slot)
- View appointment history
- See treatment records (diagnosis, medicines prescribed)
- Cancel appointments

### For Doctors
- View today's appointments
- See assigned patients
- Update treatment details (diagnosis, prescription, notes)
- Mark appointments as completed
- Set availability (morning/evening slots for next 7 days)

### For Admin
- Add/edit/blacklist doctors
- Edit/blacklist patients
- View all appointments
- Reschedule or cancel any appointment
- See appointment history for any doctor or patient
- Dashboard with statistics

## Tech Stack

**Frontend:**
- HTML, CSS, JavaScript
- Vue.js 3 (loaded from CDN)
- Bootstrap 5 for styling
- Professional dark theme (#0f172a)

**Backend:**
- Python Flask
- SQLite database
- SQLAlchemy (ORM)
- JWT for authentication

**Background Jobs:**
- Celery (for sending emails)
- Redis (message broker)

## Project Structure

```
hospital-management-system/
├── backend/
│   ├── models/              # Database tables
│   ├── routes/              # API endpoints
│   │   ├── auth.py         # Login/Register
│   │   ├── admin.py        # Admin features
│   │   ├── doctor.py       # Doctor features
│   │   └── patient.py      # Patient features
│   ├── celery_tasks/       # Email sending tasks
│   ├── app.py              # Main Flask app
│   ├── database.py         # Database setup
│   └── seed_db.py          # Create sample data
├── frontend/
│   ├── js/
│   │   ├── app.js          # Main Vue app
│   │   ├── admin.js        # Admin dashboard
│   │   ├── doctor.js       # Doctor dashboard
│   │   ├── patient.js      # Patient dashboard
│   │   └── api.js          # API calls
│   ├── custom.css          # Styling
│   └── index.html          # Main page
└── docs/                    # Documentation
```

## How to Run

### Quick Start (Just 2 steps!)

1. **Start Backend**
```bash
cd backend
pip install -r requirements.txt
python seed_db.py          # Creates database with sample data
python app.py              # Starts server at http://localhost:5000
```

2. **Start Frontend**
```bash
cd frontend
python -m http.server 3000  # Opens at http://localhost:3000
```

That's it! Open http://localhost:3000 in your browser.

### Login Credentials

After running `seed_db.py`, you can login as:

**Admin:**
- Username: `admin`
- Password: `admin123`

**Doctors:**
- Username: `dr_sharma` / `dr_verma` / `dr_patel` / `dr_singh` / `dr_kumar`
- Password: `doctor123`

**Patients:**
- Username: `patient1` / `patient2` / `patient3` ... (up to patient10)
- Password: `patient123`

### Optional: Email Notifications

If you want email features (appointment confirmations, reminders):

1. Install and start Redis
2. Run Celery worker
3. Run Celery beat (for scheduled tasks)

See `docs/setup.md` for detailed instructions.

## Database Tables

- **users** - Login credentials for all users
- **doctors** - Doctor profiles (name, specialization, experience, fees)
- **patients** - Patient info (name, age, gender, medical history)
- **appointments** - Booking records (date, time, status)
- **treatments** - Treatment records (diagnosis, prescription, notes)
- **doctor_availability** - Doctor schedule slots (morning/evening)

## Screenshots

### Homepage
Modern hero section with professional dark theme

### Login/Register
Clean branded login page with stats

### Admin Dashboard
Manage doctors, patients, and appointments

### Doctor Dashboard
View appointments and update treatments

### Patient Dashboard
Book appointments and view history

## What I Learned

- Building REST APIs with Flask
- User authentication with JWT
- Frontend development with Vue.js
- Database design and relationships
- Background job processing with Celery
- UI/UX design principles

## Future Improvements

- [ ] Email/SMS notifications (code is ready, just need SMTP setup)
- [ ] Payment integration for consultation fees
- [ ] Video consultation feature
- [ ] Prescription PDF download
- [ ] Mobile app version

## Documentation

Check the `docs/` folder for more details:
- `setup.md` - Detailed setup instructions
- `architecture.md` - How everything works together
- `bg_jobs.md` - Email system explanation

## Contributing

Feel free to fork this project and make improvements! Some ideas:
- Add more specializations
- Improve UI design
- Add more features (lab reports, pharmacy, etc.)

## Contact

Made by [Your Name]
- GitHub: [@aloktripathi1](https://github.com/aloktripathi1)

## License

MIT License - Feel free to use this for your college projects!
