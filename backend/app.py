# =================== IMPORTS SECTION ===================
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os
from celery import Celery
from database import db

# =================== FLASK APPLICATION SETUP SECTION ===================

# Create Flask application instance
main_app = Flask(__name__, static_folder='../frontend/assets', static_url_path='/static')

# =================== APPLICATION CONFIGURATION SECTION ===================

# Set application secret key for sessions
main_app.config['SECRET_KEY'] = 'hospital-management-secret-key-2024'

# Configure database connection (SQLite)
main_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
main_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Redis for background tasks
main_app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
main_app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# =================== EXTENSIONS INITIALIZATION SECTION ===================

# Initialize database with application
db.init_app(main_app)

# Enable Cross-Origin Resource Sharing (CORS)
CORS(main_app)

# =================== CELERY BACKGROUND TASKS SETUP SECTION ===================

def setup_celery_with_flask(flask_app):
    # Create Celery instance with Flask app configuration
    celery_instance = Celery(
        flask_app.import_name,
        backend=flask_app.config['CELERY_RESULT_BACKEND'],
        broker=flask_app.config['CELERY_BROKER_URL']
    )
    
    # Update Celery configuration with Flask config
    celery_instance.conf.update(flask_app.config)
    
    # Create custom task class that works with Flask context
    class FlaskContextTask(celery_instance.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)
    
    # Set the custom task class
    celery_instance.Task = FlaskContextTask
    return celery_instance

# Initialize Celery with Flask app
background_tasks_celery = setup_celery_with_flask(main_app)

# Export commonly used variables for other modules
app = main_app  # For backward compatibility with existing imports
celery = background_tasks_celery  # For backward compatibility with existing imports

# =================== MODELS AND ROUTES IMPORTS SECTION ===================

# Import all database models after database initialization
from models import *
from routes import *

# =================== BLUEPRINTS REGISTRATION SECTION ===================

# Register authentication routes
main_app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Register admin management routes
main_app.register_blueprint(admin_bp, url_prefix='/api/admin')

# Register doctor functionality routes
main_app.register_blueprint(doctor_bp, url_prefix='/api/doctor')

# Register patient functionality routes
main_app.register_blueprint(patient_bp, url_prefix='/api/patient')

# =================== MAIN ROUTES SECTION ===================

@main_app.route('/')
def serve_homepage():
    # Serve the main frontend page
    return send_from_directory('../frontend', 'index.html')

# =================== DATABASE SETUP SECTION ===================

def create_database_tables():
    # Create all database tables and setup default admin user
    with main_app.app_context():
        # Create all database tables
        db.create_all()
        
        # Create default admin user only
        setup_default_admin_user()

def setup_default_admin_user():
    # Check if admin user already exists
    existing_admin = User.query.filter_by(role='admin').first()
    
    # Create admin user only if it doesn't exist
    if existing_admin is None:
        # Create new admin user
        new_admin_user = User(
            username='admin',
            email='admin@hospital.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        
        # Add admin user to database
        db.session.add(new_admin_user)
        db.session.commit()
        
        # Print confirmation message
        print("Default admin user created: admin/admin123")

# =================== APPLICATION STARTUP SECTION ===================

if __name__ == '__main__':
    # Create database tables when running directly
    create_database_tables()
    
    # Start the Flask application in debug mode
    main_app.run(debug=True, port=5000)
