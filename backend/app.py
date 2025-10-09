from flask import Flask, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from celery import Celery
from database import db
import time
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='../frontend/assets', static_url_path='/static')

app.config['SECRET_KEY'] = 'this-is-a-secret-key-for-hospital-management'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital-management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Simple cache - just a dictionary
cache = {}

db.init_app(app)
CORS(app)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

from models import *
from routes import *

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
app.register_blueprint(patient_bp, url_prefix='/api/patient')

@app.route('/download/<filename>')  
def download_file(filename):
    return send_from_directory('.', filename)

@app.route('/')
def home():
    return send_from_directory('../frontend', 'index.html')

def setup_db():
    with app.app_context():
        db.create_all()
        
        # Create admin if not exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@medihub.com',
                password_hash=generate_password_hash('admin'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin created: admin/admin")

if __name__ == '__main__':
    setup_db()
    app.run(debug=True, port=5000)