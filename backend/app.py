from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from celery import Celery
from database import db
import time
import os
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='../frontend/assets', static_url_path='/static')

# flask config
app.config['SECRET_KEY'] = 'hospital-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital-management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# celery config
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_TASK_SERIALIZER'] = 'json'
app.config['CELERY_ACCEPT_CONTENT'] = ['json']
app.config['CELERY_RESULT_SERIALIZER'] = 'json'

# Development Mode
app.config['DEBUG'] = True

# =================== SIMPLE CACHE & DATABASE SETUP ===================
# Simple cache - just a dictionary
cache = {}

db.init_app(app)
CORS(app)

# celery setup
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

# =================== BLUEPRINTS REGISTRATION ===================
from models import *
from routes import *

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
app.register_blueprint(patient_bp, url_prefix='/api/patient')

# =================== ROUTES ===================

# =================== ROUTES ===================
@app.route('/download/<filename>')  
def download_file(filename):
    return send_from_directory('.', filename)

# =================== ERROR HANDLERS ===================

@app.errorhandler(404)
def not_found(error):
    # Return JSON for API routes, HTML for others
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'message': f'Endpoint not found: {request.path}'
        }), 404
    # For non-API routes, serve the frontend
    return send_from_directory('../frontend', 'index.html')

@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

@app.route('/')
def home():
    return send_from_directory('../frontend', 'index.html')

# Catch-all route for frontend routing (must be last)
@app.route('/<path:path>')
def serve_frontend(path):
    # Serve static files if they exist
    frontend_path = os.path.join('../frontend', path)
    if os.path.exists(frontend_path) and os.path.isfile(frontend_path):
        return send_from_directory('../frontend', path)
    # Otherwise serve index.html for client-side routing
    return send_from_directory('../frontend', 'index.html')

# =================== DATABASE INITIALIZATION ===================

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

# =================== APPLICATION ENTRY POINT ===================
if __name__ == '__main__':
    setup_db()
    app.run(debug=True, port=5000)

# =================== APPLICATION ENTRY POINT ===================
if __name__ == '__main__':
    setup_db()
    app.run(debug=True, port=5000)

if __name__ == '__main__':
    setup_db()
    app.run(debug=True, port=5000)