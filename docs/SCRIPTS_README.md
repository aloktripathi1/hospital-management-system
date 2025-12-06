# Quick Start Scripts - README

This folder contains several scripts to help you easily run the Hospital Management System with all required services.

## 📁 Available Scripts

### For Linux/WSL Users:

1. **`quick_start.sh`** - Starts Redis and MailHog, shows commands for other services
2. **`start_tmux.sh`** - Starts all services in a single tmux session (recommended)
3. **`stop_all.sh`** - Stops all running services

### For Windows Users:

1. **`start_windows.bat`** - Starts all services in separate Windows Terminal tabs
2. **`stop_windows.bat`** - Stops all services

---

## 🚀 Usage

### Option 1: tmux (Single Terminal - Recommended)

Best for users who want all services in one terminal window with easy tab switching.

```bash
# In WSL terminal
./start_tmux.sh
```

**tmux Controls:**
- Switch tabs: `Ctrl+b` then `0-5` (window number)
- Next tab: `Ctrl+b` then `n`
- Previous tab: `Ctrl+b` then `p`
- Detach (leave running): `Ctrl+b` then `d`
- Reattach later: `tmux attach -t hospital`
- Kill all: `tmux kill-session -t hospital`

---

### Option 2: Manual (Separate Terminals)

If you prefer separate terminal windows:

```bash
# Run this first to start Redis and MailHog
./quick_start.sh

# Then open 3 separate terminals and run:

# Terminal 1:
cd backend && python3 app.py

# Terminal 2:
cd backend && celery -A celery_tasks.celery worker --loglevel=info --pool=solo

# Terminal 3:
cd frontend && python3 -m http.server 3000
```

---

### Option 3: Windows Terminal (Windows Only)

Double-click `start_windows.bat` or run from CMD/PowerShell:

```cmd
start_windows.bat
```

This will open Windows Terminal with tabs for each service.

---

## 🛑 Stopping Services

### Using tmux:
```bash
tmux kill-session -t hospital
```

### Using stop script (Linux/WSL):
```bash
./stop_all.sh
```

### Using Windows:
```cmd
stop_windows.bat
```

Or press `Ctrl+C` in each terminal window.

---

## 🌐 Access Points

Once all services are running:

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:5000 |
| **MailHog UI** | http://localhost:8025 |

---

## ✅ Verification

After starting, verify services are running:

```bash
# Check Redis
redis-cli ping
# Should return: PONG

# Check MailHog
docker ps | grep mailhog
# Should show running container

# Check Backend
curl http://localhost:5000/api/auth/check
# Should return JSON response

# Check Frontend
curl http://localhost:3000
# Should return HTML
```

---

## 🐛 Troubleshooting

### "Port already in use" error

```bash
# Find and kill process using the port
sudo lsof -i :5000  # Replace with your port
sudo kill -9 <PID>
```

### Redis won't start

```bash
# Check if already running
pgrep redis-server

# Kill existing instance
pkill redis-server

# Start manually
redis-server
```

### MailHog won't start

```bash
# Remove existing container
docker rm -f mailhog

# Start fresh
docker run -d -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog
```

### Celery worker fails

```bash
# Make sure Redis is running first
redis-cli ping

# Try with solo pool
celery -A celery_tasks.celery worker --loglevel=info --pool=solo
```

---

## 📖 Full Documentation

For complete setup instructions, see:
- `WSL_MULTI_TERMINAL_GUIDE.md` - Detailed multi-terminal setup
- `WSL_SETUP_GUIDE.md` - Initial WSL configuration
- `MAILHOG_CELERY_SETUP.md` - Email and background tasks
- `STUDENT_GUIDE.md` - Application usage

---

## 🎯 Quick Reference

**First time setup:**
```bash
cd backend
pip3 install -r requirements.txt
python3 init_db.py
cd ..
```

**Daily usage:**
```bash
./start_tmux.sh
```

**When done:**
```bash
./stop_all.sh
```

---

**Happy Coding! 🚀**
