#!/bin/bash

# Simple startup script for Hospital Management System
# Opens 4 WSL terminals automatically

BACKEND_DIR="$(pwd)/backend"

echo "Starting Hospital Management System..."

# Check if virtual environment exists
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "Virtual environment not found. Setting up for first time..."
    cd "$BACKEND_DIR"
    
    # Create virtual environmen
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    # Activate and install packages
    source venv/bin/activate
    
    # Check if uv is installed
    if command -v uv &> /dev/null; then
        echo "Installing packages using uv..."
        uv pip install -r requirements.txt
    else
        echo "uv not found, installing with pip..."
        pip install uv
        echo "Installing packages using uv..."
        uv pip install -r requirements.txt
    fi
    
    echo "Setup complete!"
    cd ..
fi

echo "Opening 4 terminals..."

# Terminal 1: Redis Server
wt.exe -w 0 nt -d "$BACKEND_DIR" --title "Redis Server" bash -c "echo '=== Redis Server ==='; redis-server; exec bash" \; `
# Terminal 2: Flask App
split-pane -d "$BACKEND_DIR" --title "Flask App" bash -c "echo '=== Flask Application ==='; source venv/bin/activate; python app.py; exec bash" \; `
# Terminal 3: Celery Worker  
split-pane -d "$BACKEND_DIR" --title "Celery Worker" bash -c "echo '=== Celery Worker ==='; source venv/bin/activate; celery -A celery_tasks worker --loglevel=info; exec bash" \; `
# Terminal 4: Celery Beat
split-pane -d "$BACKEND_DIR" --title "Celery Beat" bash -c "echo '=== Celery Beat ==='; source venv/bin/activate; celery -A celery_tasks beat --loglevel=info; exec bash"

echo "Done! Check Windows Terminal for all 4 services."
