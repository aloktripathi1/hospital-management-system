from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from celery import Celery
from database import db

# Initialize Flask app
app = Flask(__name__, template_folder='../frontend', static_folder='../frontend/assets')

# Configuration
app.config['SECRET_KEY'] = 'hospital-management-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
CORS(app)

# Function to make Celery work with Flask app context
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Initialize Celery
celery = make_celery(app)

# Import models and routes after db initialization
from models import *
from routes import *

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
app.register_blueprint(patient_bp, url_prefix='/api/patient')

@app.route('/')
def index():
    return render_template('index.html')

def create_tables():
    """Create all database tables and default admin user"""
    with app.app_context():
        db.create_all()
        create_default_admin()
        create_sample_data()

def create_default_admin():
    """Create default admin user if not exists"""
    if not User.query.filter_by(role='admin').first():
        admin_user = User(
            username='admin',
            email='admin@hospital.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin created: admin/admin123")

def create_sample_data():
    """Create sample doctors and patients for testing"""
    # Sample doctors
    if not Doctor.query.first():
        sample_doctors = [
            {
                'username': 'dr_smith',
                'email': 'dr.smith@hospital.com',
                'password': 'doctor123',
                'name': 'Dr. John Smith',
                'specialization': 'Cardiology',
                'experience': 10
            },
            {
                'username': 'dr_johnson',
                'email': 'dr.johnson@hospital.com',
                'password': 'doctor123',
                'name': 'Dr. Sarah Johnson',
                'specialization': 'Oncology',
                'experience': 8
            }
        ]
        
        for doc_data in sample_doctors:
            user = User(
                username=doc_data['username'],
                email=doc_data['email'],
                password_hash=generate_password_hash(doc_data['password']),
                role='doctor'
            )
            db.session.add(user)
            db.session.flush()
            
            doctor = Doctor(
                user_id=user.id,
                name=doc_data['name'],
                specialization=doc_data['specialization'],
                experience=doc_data['experience']
            )
            db.session.add(doctor)
        
        db.session.commit()
        print("Sample doctors created")

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, port=5000)
