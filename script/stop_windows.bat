@echo off
REM Hospital Management System - Stop All Services (Windows)

echo Stopping all Hospital Management System services...
echo.

REM Stop services in WSL
wsl -d Ubuntu bash -c "pkill redis-server; pkill -f 'python3 app.py'; pkill -f 'celery.*worker'; pkill -f 'http.server'; docker stop mailhog 2>/dev/null; docker rm mailhog 2>/dev/null"

echo.
echo All services stopped!
echo.
pause
