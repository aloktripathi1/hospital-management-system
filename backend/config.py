import os
from datetime import timedelta

class Config:
    SECRET_KEY = 'hospital-secret-key-123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    REDIS_URL = 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

class DevConfig(Config):
    DEBUG = True

class CeleryConfig:
    broker_url = 'redis://localhost:6379/0'
    result_backend = 'redis://localhost:6379/0'
    task_serializer = 'json'
    accept_content = ['json']
    result_serializer = 'json'
    
    task_routes = {
        'backend.tasks.celery_tasks.send_appointment_reminder': {'queue': 'reminders'},
        'backend.tasks.celery_tasks.export_patient_history': {'queue': 'exports'},
    }

config = {
    'development': DevConfig,
    'default': DevConfig
}