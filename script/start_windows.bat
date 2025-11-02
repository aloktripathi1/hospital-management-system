@echo off
REM Hospital Management System - Windows WSL Launcher
REM This script launches separate Windows Terminal tabs for each service

echo ===================================
echo Hospital Management System
echo Windows WSL Multi-Tab Launcher
echo ===================================
echo.

REM Check if Windows Terminal is available
where wt >nul 2>nul
if %errorlevel% neq 0 (
    echo Windows Terminal not found!
    echo Please install Windows Terminal from Microsoft Store
    echo or run services manually in separate WSL windows.
    pause
    exit /b 1
)

REM Get the WSL project path
set PROJECT_PATH=/workspaces/hospital-management-system

echo Starting services in separate tabs...
echo.

REM Start Windows Terminal with multiple tabs
wt -w 0 ^
    new-tab --title "Redis" -p "Ubuntu" wsl -d Ubuntu -- bash -c "cd %PROJECT_PATH% && echo 'Starting Redis Server...' && redis-server; exec bash" ^
    ; new-tab --title "MailHog" -p "Ubuntu" wsl -d Ubuntu -- bash -c "cd %PROJECT_PATH% && echo 'Starting MailHog...' && docker run --rm -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog; exec bash" ^
    ; new-tab --title "Backend" -p "Ubuntu" wsl -d Ubuntu -- bash -c "cd %PROJECT_PATH%/backend && sleep 3 && echo 'Starting Flask Backend...' && python3 app.py; exec bash" ^
    ; new-tab --title "Celery" -p "Ubuntu" wsl -d Ubuntu -- bash -c "cd %PROJECT_PATH%/backend && sleep 5 && echo 'Starting Celery Worker...' && celery -A celery_tasks.celery worker --loglevel=info --pool=solo; exec bash" ^
    ; new-tab --title "Frontend" -p "Ubuntu" wsl -d Ubuntu -- bash -c "cd %PROJECT_PATH%/frontend && sleep 3 && echo 'Starting Frontend Server...' && python3 -m http.server 3000; exec bash" ^
    ; new-tab --title "Control" -p "Ubuntu" wsl -d Ubuntu -- bash -c "cd %PROJECT_PATH% && echo '=========================================' && echo 'Hospital Management System - Control' && echo '=========================================' && echo '' && echo 'Access Points:' && echo '  Frontend:    http://localhost:3000' && echo '  Backend API: http://localhost:5000' && echo '  MailHog UI:  http://localhost:8025' && echo '' && echo 'All services are starting...' && echo 'Wait 10 seconds for all services to be ready.' && echo '' && exec bash"

echo.
echo ===================================
echo All services are starting!
echo ===================================
echo.
echo Access Points:
echo   Frontend:    http://localhost:3000
echo   Backend API: http://localhost:5000
echo   MailHog UI:  http://localhost:8025
echo.
echo Check each tab for service status.
echo ===================================
