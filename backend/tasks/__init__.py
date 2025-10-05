# Tasks package - Hospital Management System

# Import all celery tasks
from .celery_tasks import send_daily_reminders, generate_monthly_report, export_patient_history_csv

# Make all tasks available when importing from tasks  
__all__ = [
    'send_daily_reminders',
    'generate_monthly_report',
    'export_patient_history_csv'
]