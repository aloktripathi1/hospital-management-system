#!/bin/bash

# Hospital Management System - tmux Multi-Window Startup Script

SESSION_NAME="hospital"

# Check if tmux session already exists
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "Session '$SESSION_NAME' already exists. Attaching..."
    tmux attach-session -t $SESSION_NAME
    exit 0
fi

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Starting Hospital Management System in tmux..."
echo "Project directory: $PROJECT_DIR"

# Create new tmux session (detached)
tmux new-session -d -s $SESSION_NAME -n Redis

# Window 0: Redis Server
tmux send-keys -t $SESSION_NAME:0 "echo 'Starting Redis Server...'" C-m
tmux send-keys -t $SESSION_NAME:0 "redis-server" C-m

# Window 1: MailHog
tmux new-window -t $SESSION_NAME:1 -n MailHog
tmux send-keys -t $SESSION_NAME:1 "echo 'Starting MailHog...'" C-m
tmux send-keys -t $SESSION_NAME:1 "docker rm mailhog 2>/dev/null; docker run --rm -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog" C-m

# Wait for Redis and MailHog to start
sleep 3

# Window 2: Backend Flask Server
tmux new-window -t $SESSION_NAME:2 -n Backend
tmux send-keys -t $SESSION_NAME:2 "cd $PROJECT_DIR/backend" C-m
tmux send-keys -t $SESSION_NAME:2 "echo 'Starting Flask Backend Server...'" C-m
tmux send-keys -t $SESSION_NAME:2 "python3 app.py" C-m

# Window 3: Celery Worker
tmux new-window -t $SESSION_NAME:3 -n Celery
tmux send-keys -t $SESSION_NAME:3 "cd $PROJECT_DIR/backend" C-m
tmux send-keys -t $SESSION_NAME:3 "echo 'Starting Celery Worker...'" C-m
tmux send-keys -t $SESSION_NAME:3 "sleep 3 && celery -A celery_tasks.celery worker --loglevel=info --pool=solo" C-m

# Window 4: Frontend Server
tmux new-window -t $SESSION_NAME:4 -n Frontend
tmux send-keys -t $SESSION_NAME:4 "cd $PROJECT_DIR/frontend" C-m
tmux send-keys -t $SESSION_NAME:4 "echo 'Starting Frontend Server...'" C-m
tmux send-keys -t $SESSION_NAME:4 "python3 -m http.server 3000" C-m

# Window 5: Control/Logs window
tmux new-window -t $SESSION_NAME:5 -n Control
tmux send-keys -t $SESSION_NAME:5 "cd $PROJECT_DIR" C-m
tmux send-keys -t $SESSION_NAME:5 "clear" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '========================================='" C-m
tmux send-keys -t $SESSION_NAME:5 "echo 'Hospital Management System - Control Panel'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '========================================='" C-m
tmux send-keys -t $SESSION_NAME:5 "echo ''" C-m
tmux send-keys -t $SESSION_NAME:5 "echo 'Access Points:'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  Frontend:    http://localhost:3000'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  Backend API: http://localhost:5000'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  MailHog UI:  http://localhost:8025'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo ''" C-m
tmux send-keys -t $SESSION_NAME:5 "echo 'Windows:'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  0: Redis Server'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  1: MailHog'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  2: Backend (Flask)'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  3: Celery Worker'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  4: Frontend'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  5: Control (current)'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo ''" C-m
tmux send-keys -t $SESSION_NAME:5 "echo 'tmux Commands:'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  Switch windows: Ctrl+b then 0-5'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  Next window: Ctrl+b then n'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  Previous window: Ctrl+b then p'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  Detach session: Ctrl+b then d'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  Kill session: tmux kill-session -t hospital'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo ''" C-m
tmux send-keys -t $SESSION_NAME:5 "echo 'Useful Commands:'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  Test background jobs: cd backend && python3 trigger_tasks.py'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  Check Redis: redis-cli ping'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '  View MailHog logs: docker logs -f mailhog'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '========================================='" C-m

# Select the Backend window to show by default
tmux select-window -t $SESSION_NAME:2

# Attach to the session
echo ""
echo "All services starting in tmux session '$SESSION_NAME'"
echo "Attaching to session in 3 seconds..."
sleep 3

tmux attach-session -t $SESSION_NAME
