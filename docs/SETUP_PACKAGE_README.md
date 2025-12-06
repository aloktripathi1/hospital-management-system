# Hospital Management System - Complete Setup Package

## 📦 What's Included

This package includes everything you need to run the Hospital Management System on Windows WSL with proper multi-terminal/multi-service setup.

---

## 📄 Documentation Files

1. **`WSL_MULTI_TERMINAL_GUIDE.md`** ⭐ **START HERE**
   - Complete guide for setting up and running all services
   - Explains each service and how to manage them
   - Troubleshooting tips

2. **`SCRIPTS_README.md`**
   - Quick reference for using the startup scripts
   - Usage examples and commands

3. **`WSL_SETUP_GUIDE.md`**
   - Initial WSL installation and configuration
   - Prerequisites and dependencies

4. **`MAILHOG_CELERY_SETUP.md`**
   - Email testing setup
   - Background tasks configuration

5. **`STUDENT_GUIDE.md`**
   - How to use the application
   - Features and workflows

---

## 🔧 Startup Scripts

### Linux/WSL Scripts:

1. **`start_tmux.sh`** ⭐ **RECOMMENDED**
   - Starts all services in one tmux session
   - Easy window switching
   - Professional development setup
   ```bash
   ./start_tmux.sh
   ```

2. **`quick_start.sh`**
   - Starts Redis and MailHog
   - Shows commands for manual terminal setup
   ```bash
   ./quick_start.sh
   ```

3. **`stop_all.sh`**
   - Stops all running services
   ```bash
   ./stop_all.sh
   ```

### Windows Scripts:

4. **`start_windows.bat`**
   - Windows Terminal multi-tab launcher
   - Double-click to run or use from CMD
   ```cmd
   start_windows.bat
   ```

5. **`stop_windows.bat`**
   - Stops all services from Windows
   ```cmd
   stop_windows.bat
   ```

---

## 🚀 Quick Start (Choose One)

### Method 1: tmux (Recommended for WSL)

```bash
# First time setup
cd backend
pip3 install -r requirements.txt
python3 init_db.py
cd ..

# Start everything
./start_tmux.sh

# When done
tmux kill-session -t hospital
```

### Method 2: Windows Terminal (Recommended for Windows)

```cmd
REM First time setup (in WSL)
cd backend
pip3 install -r requirements.txt
python3 init_db.py
cd ..

REM Start everything (double-click or run from CMD)
start_windows.bat

REM When done
stop_windows.bat
```

### Method 3: Manual Terminals

```bash
# Terminal 1: Setup & Redis
./quick_start.sh

# Terminal 2: Backend
cd backend && python3 app.py

# Terminal 3: Celery
cd backend && celery -A celery_tasks.celery worker --loglevel=info --pool=solo

# Terminal 4: Frontend
cd frontend && python3 -m http.server 3000
```

---

## 🌐 Access Points

After starting all services:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main application UI |
| Backend API | http://localhost:5000 | REST API |
| MailHog UI | http://localhost:8025 | Email testing |

---

## 📋 Service Overview

### Required Services (Must Run):

1. **Redis** (Port 6379)
   - Message broker for Celery
   - Session storage
   - Caching

2. **MailHog** (Ports 1025, 8025)
   - Email testing server
   - View sent emails at http://localhost:8025

3. **Backend** (Port 5000)
   - Flask REST API
   - Handles all business logic

4. **Celery Worker**
   - Processes background tasks
   - Sends emails asynchronously
   - Generates reports

5. **Frontend** (Port 3000)
   - Vue.js application
   - User interface

---

## 🔑 Default Login Credentials

After running `python3 init_db.py`:

### Admin Account
- **Username:** admin
- **Password:** admin123
- **Access:** Full system management

### Creating Other Users
- Doctors: Created by admin through the UI
- Patients: Self-registration or created by admin

---

## ✅ Verification Checklist

Run this after starting services:

```bash
# Check Redis
redis-cli ping                    # Should return: PONG

# Check MailHog
docker ps | grep mailhog         # Should show running container

# Check Backend
curl http://localhost:5000/api/auth/check   # Should return JSON

# Check Frontend
curl http://localhost:3000                   # Should return HTML

# Check Celery
# Look for "ready" message in Celery terminal
```

---

## 🎓 Learning Path

### For Students:

1. **Setup** → Read `WSL_MULTI_TERMINAL_GUIDE.md`
2. **Install** → Follow installation steps
3. **Start** → Use `start_tmux.sh` or `start_windows.bat`
4. **Learn** → Read `STUDENT_GUIDE.md` for features
5. **Demo** → Use `QUICK_VIVA_DEMO.md` for presentation

### For Development:

1. Study the code structure
2. Understand the API endpoints
3. Learn about Celery background tasks
4. Experiment with the email system

---

## 🐛 Common Issues & Solutions

### "Port already in use"
```bash
# Find what's using the port
sudo lsof -i :5000
# Kill the process
sudo kill -9 <PID>
```

### "Cannot connect to Redis"
```bash
# Check if Redis is running
redis-cli ping
# If not, start it
redis-server --daemonize yes
```

### "MailHog not accessible"
```bash
# Restart MailHog
docker stop mailhog && docker rm mailhog
docker run -d -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog
```

### "Celery worker won't start"
```bash
# Use solo pool for WSL
celery -A celery_tasks.celery worker --loglevel=info --pool=solo
```

---

## 📊 Project Structure

```
hospital-management-system/
├── backend/                 # Flask REST API
│   ├── app.py              # Main application
│   ├── celery_tasks.py     # Background tasks
│   ├── database.py         # Database config
│   ├── models/             # Database models
│   └── routes/             # API endpoints
├── frontend/               # Vue.js application
│   ├── index.html          # Main HTML
│   └── assets/             # CSS, JS files
├── docs/                   # Documentation
├── tests/                  # Test files
├── start_tmux.sh          # ⭐ tmux startup
├── start_windows.bat      # ⭐ Windows startup
├── quick_start.sh         # Manual startup helper
├── stop_all.sh            # Shutdown script
└── *.md                   # Documentation files
```

---

## 🎯 Next Steps

1. ✅ Read `WSL_MULTI_TERMINAL_GUIDE.md` for detailed setup
2. ✅ Run `start_tmux.sh` or `start_windows.bat`
3. ✅ Login as admin (admin/admin123)
4. ✅ Explore the system features
5. ✅ Read `STUDENT_GUIDE.md` for usage instructions
6. ✅ Test email functionality with MailHog

---

## 📞 Support & Resources

- **Setup Issues:** See `WSL_MULTI_TERMINAL_GUIDE.md` Troubleshooting section
- **Usage Questions:** See `STUDENT_GUIDE.md`
- **Demo Preparation:** See `QUICK_VIVA_DEMO.md`
- **Email Setup:** See `MAILHOG_CELERY_SETUP.md`

---

## 🎉 You're Ready!

Everything you need is included. Just choose your preferred startup method and you're good to go!

**Recommended for beginners:** `start_tmux.sh` (WSL) or `start_windows.bat` (Windows)

---

**Happy Learning! 🚀**
