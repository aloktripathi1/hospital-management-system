# Hospital Management System - WSL Multi-Terminal Setup Guide

This guide will help you run the complete Hospital Management System on Windows WSL with separate terminals for each service.

## Prerequisites

1. **WSL2** installed on Windows
2. **Ubuntu** (or any Linux distro) running in WSL
3. **Python 3.8+** installed
4. **Node.js** (optional, for live-server)
5. **Redis** installed
6. **Docker** (for MailHog)

## Quick Setup Commands

Run these commands first in your main terminal to install dependencies:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Redis
sudo apt install redis-server -y

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Node.js and npm (optional - for live-server)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install live-server globally (optional)
sudo npm install -g live-server
```

## Project Setup (First Time Only)

In your project directory:

```bash
cd /workspaces/hospital-management-system

# Install Python dependencies
cd backend
pip3 install -r requirements.txt

# Initialize the database
python3 init_db.py

cd ..
```

## Running the Application - Multi-Terminal Setup

You'll need **5 separate terminals** (or tmux panes) to run all services. Here's how to set them up:

---

### **Terminal 1: Redis Server**

```bash
# Start Redis server
redis-server

# To verify Redis is running, open another terminal and run:
# redis-cli ping
# It should return: PONG
```

**Expected Output:**
```
                _._                                                  
           _.-``__ ''-._                                             
      _.-``    `.  `_.  ''-._           Redis 6.0.16 (00000000/0) 64 bit
  .-`` .-```.  ```\/    _.,_ ''-._                                  
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
 |    `-._   `._    /     _.-'    |     PID: xxxxx
  `-._    `-._  `-./  _.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |           http://redis.io        
  `-._    `-._`-.__.-'_.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |                                  
  `-._    `-._`-.__.-'_.-'    _.-'                                   
      `-._    `-.__.-'    _.-'                                       
          `-._        _.-'                                           
              `-.__.-'                                               

Server initialized
Ready to accept connections
```

---

### **Terminal 2: MailHog (Email Testing)**

```bash
# Start MailHog using Docker
docker run -d -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog

# To check if it's running:
docker ps | grep mailhog

# To view logs:
docker logs -f mailhog
```

**Access MailHog Web UI:**
- Open browser: http://localhost:8025
- All emails sent by the application will appear here

**To stop MailHog:**
```bash
docker stop mailhog
docker rm mailhog
```

---

### **Terminal 3: Flask Backend Server**

```bash
cd /workspaces/hospital-management-system/backend

# Start the Flask application
python3 app.py

# Alternative with debug mode:
# FLASK_ENV=development python3 app.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: xxx-xxx-xxx
```

**Backend will be running on:** http://localhost:5000

---

### **Terminal 4: Celery Worker (Background Tasks)**

```bash
cd /workspaces/hospital-management-system/backend

# Start Celery worker
celery -A celery_tasks.celery worker --loglevel=info

# For Windows WSL, you might need to add the pool parameter:
# celery -A celery_tasks.celery worker --loglevel=info --pool=solo
```

**Expected Output:**
```
 -------------- celery@hostname v5.x.x
---- **** ----- 
--- * ***  * -- Linux-x.x.x-x-generic
-- * - **** --- 
- ** ---------- [config]
- ** ---------- .> app:         celery_tasks:0x7f...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 4 (solo)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . celery_tasks.send_appointment_confirmation
  . celery_tasks.send_appointment_reminder
  . celery_tasks.send_monthly_report

[2025-10-31 10:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-10-31 10:00:00,000: INFO/MainProcess] celery@hostname ready.
```

---

### **Terminal 5: Frontend Server**

**Option A: Using Python HTTP Server (Simple)**
```bash
cd /workspaces/hospital-management-system/frontend

# Start a simple HTTP server
python3 -m http.server 3000
```

**Option B: Using Live-Server (Better - Auto-reload)**
```bash
cd /workspaces/hospital-management-system/frontend

# Start live-server
live-server --port=3000 --host=0.0.0.0
```

**Option C: Using VS Code Live Server Extension**
- Install "Live Server" extension in VS Code
- Right-click on `index.html`
- Select "Open with Live Server"

**Frontend will be running on:** http://localhost:3000

---

## Testing Background Jobs (Optional)

In a **6th terminal**, you can trigger background tasks:

```bash
cd /workspaces/hospital-management-system/backend

# Send test emails
python3 trigger_tasks.py
```

---

## Using tmux for Multiple Terminals (Advanced)

If you prefer to manage all terminals in one window using `tmux`:

### Install tmux:
```bash
sudo apt install tmux -y
```

### Create a tmux session with all services:

Create a script called `start_all.sh`:

```bash
#!/bin/bash

# Create new tmux session
tmux new-session -d -s hospital

# Window 0: Redis
tmux rename-window -t hospital:0 'Redis'
tmux send-keys -t hospital:0 'redis-server' C-m

# Window 1: MailHog
tmux new-window -t hospital:1 -n 'MailHog'
tmux send-keys -t hospital:1 'docker run -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog' C-m

# Window 2: Backend
tmux new-window -t hospital:2 -n 'Backend'
tmux send-keys -t hospital:2 'cd /workspaces/hospital-management-system/backend && python3 app.py' C-m

# Window 3: Celery
tmux new-window -t hospital:3 -n 'Celery'
tmux send-keys -t hospital:3 'cd /workspaces/hospital-management-system/backend && celery -A celery_tasks.celery worker --loglevel=info --pool=solo' C-m

# Window 4: Frontend
tmux new-window -t hospital:4 -n 'Frontend'
tmux send-keys -t hospital:4 'cd /workspaces/hospital-management-system/frontend && python3 -m http.server 3000' C-m

# Attach to the session
tmux attach-session -t hospital
```

Make it executable and run:
```bash
chmod +x start_all.sh
./start_all.sh
```

### tmux Navigation:
- **Switch windows:** `Ctrl+b` then `0-4` (window number)
- **Next window:** `Ctrl+b` then `n`
- **Previous window:** `Ctrl+b` then `p`
- **Detach from session:** `Ctrl+b` then `d`
- **Reattach to session:** `tmux attach -t hospital`
- **Kill session:** `tmux kill-session -t hospital`

---

## Quick Start Script (All-in-One)

Create a file called `quick_start.sh` in the project root:

```bash
#!/bin/bash

echo "==================================="
echo "Hospital Management System Startup"
echo "==================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Redis is running
if ! pgrep -x "redis-server" > /dev/null; then
    echo -e "${YELLOW}Starting Redis...${NC}"
    redis-server &
    sleep 2
fi
echo -e "${GREEN}✓ Redis is running${NC}"

# Check if MailHog is running
if ! docker ps | grep -q mailhog; then
    echo -e "${YELLOW}Starting MailHog...${NC}"
    docker run -d -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog
    sleep 2
fi
echo -e "${GREEN}✓ MailHog is running${NC}"

echo ""
echo "==================================="
echo "Now start these in separate terminals:"
echo "==================================="
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend && python3 app.py"
echo ""
echo "Terminal 2 - Celery Worker:"
echo "  cd backend && celery -A celery_tasks.celery worker --loglevel=info --pool=solo"
echo ""
echo "Terminal 3 - Frontend:"
echo "  cd frontend && python3 -m http.server 3000"
echo ""
echo "==================================="
echo "Access Points:"
echo "==================================="
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}Backend API:${NC} http://localhost:5000"
echo -e "${GREEN}MailHog UI:${NC} http://localhost:8025"
echo "==================================="
```

Make it executable and run:
```bash
chmod +x quick_start.sh
./quick_start.sh
```

---

## Stopping All Services

Create a `stop_all.sh` script:

```bash
#!/bin/bash

echo "Stopping all services..."

# Stop Redis
pkill redis-server

# Stop MailHog
docker stop mailhog 2>/dev/null
docker rm mailhog 2>/dev/null

# Kill Python and Celery processes
pkill -f "python3 app.py"
pkill -f "celery"
pkill -f "http.server"

echo "All services stopped!"
```

Make it executable:
```bash
chmod +x stop_all.sh
./stop_all.sh
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000 (Backend)
sudo lsof -i :5000
sudo kill -9 <PID>

# Find process using port 3000 (Frontend)
sudo lsof -i :3000
sudo kill -9 <PID>

# Find process using port 6379 (Redis)
sudo lsof -i :6379
sudo kill -9 <PID>
```

### Redis Connection Issues
```bash
# Test Redis connection
redis-cli ping

# Check Redis status
sudo systemctl status redis

# Restart Redis
sudo systemctl restart redis
```

### Celery Not Starting
```bash
# Make sure Redis is running first
redis-cli ping

# Check Celery version compatibility
pip3 show celery

# Try running with solo pool
celery -A celery_tasks.celery worker --loglevel=info --pool=solo
```

### MailHog Not Accessible
```bash
# Check if Docker is running
docker ps

# Check MailHog logs
docker logs mailhog

# Restart MailHog
docker restart mailhog
```

---

## Default Login Credentials

After running `init_db.py`, you can login with:

### Admin
- **Username:** admin
- **Password:** admin123

### Sample Doctor
- **Username:** (check the database or create via admin panel)
- **Password:** (set during creation)

### Sample Patient
- **Username:** (check the database or create via registration)
- **Password:** (set during registration)

---

## Verification Checklist

✅ Redis is running (port 6379)  
✅ MailHog is running (ports 1025, 8025)  
✅ Backend Flask server is running (port 5000)  
✅ Celery worker is running and connected to Redis  
✅ Frontend is served (port 3000)  
✅ Can access http://localhost:3000 in browser  
✅ Can login as admin/doctor/patient  
✅ Emails appear in MailHog UI at http://localhost:8025  

---

## Quick Reference

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 5000 | http://localhost:5000 |
| Redis | 6379 | - |
| MailHog SMTP | 1025 | - |
| MailHog Web UI | 8025 | http://localhost:8025 |

---

## Support

For issues or questions, refer to:
- `WSL_SETUP_GUIDE.md` - Initial WSL setup
- `MAILHOG_CELERY_SETUP.md` - Email and background tasks setup
- `STUDENT_GUIDE.md` - Application usage guide

---

**Happy Coding! 🚀**
