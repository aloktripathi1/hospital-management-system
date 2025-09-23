import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hospital-management-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Redis configuration for Celery
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class CeleryConfig:
    broker_url = 'redis://localhost:6379/0'
    result_backend = 'redis://localhost:6379/0'
    task_serializer = 'json'
    accept_content = ['json']
    result_serializer = 'json'
    timezone = 'UTC'
    enable_utc = True
    
    # Task routing
    task_routes = {
        'backend.tasks.celery_tasks.send_appointment_reminder': {'queue': 'reminders'},
        'backend.tasks.celery_tasks.generate_monthly_report': {'queue': 'reports'},
        'backend.tasks.celery_tasks.export_patient_history': {'queue': 'exports'},
        'backend.tasks.celery_tasks.daily_appointment_reminders': {'queue': 'daily'},
    }
    
    # Beat schedule for periodic tasks
    beat_schedule = {
        'daily-reminders': {
            'task': 'backend.tasks.celery_tasks.daily_appointment_reminders',
            'schedule': 60.0 * 60.0 * 24.0,  # Run daily at midnight
        },
    }

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
