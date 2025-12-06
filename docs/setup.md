# Simple Setup Guide

This guide provides instructions to set up the backend, Redis, and Celery workers.

## Prerequisites

- Python 3.8+
- Redis Server

## 1. Backend Setup

Navigate to the backend directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Run the Flask application:

```bash
python app.py
```

The backend will start on `http://localhost:5000`.

## 2. Redis Setup

Ensure Redis is installed and running.

**Install Redis (Ubuntu/WSL):**
```bash
sudo apt update
sudo apt install redis-server
```

**Start Redis:**
```bash
sudo service redis-server start
```

## 3. Celery Worker Setup

Open a new terminal, navigate to the `backend` directory, and start the Celery worker:

```bash
cd backend
celery -A celery_tasks worker --loglevel=info
```

## 4. Celery Beat Setup (Scheduled Tasks)

Open another terminal, navigate to the `backend` directory, and start Celery Beat:

```bash
cd backend
celery -A celery_tasks beat --loglevel=info
```

## Summary of Terminals

You will need 3 separate terminals running:

1.  **Terminal 1:** Flask Backend (`python app.py`)
2.  **Terminal 2:** Celery Worker (`celery -A celery_tasks worker ...`)
3.  **Terminal 3:** Celery Beat (`celery -A celery_tasks beat ...`)

Ensure Redis is running in the background.
