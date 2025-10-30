from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_mail import Mail
from werkzeug.security import generate_password_hash
from celery import Celery
from database import db
from dotenv import load_dotenv
import time
import os
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__, static_folder='../frontend/assets', static_url_path='/static')

# flask config
app.config['SECRET_KEY'] = 'hospital-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital-management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# email config for mailhog
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 1025))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'False') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', None)
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', None)
app.config['MAIL_DEFAULT_SENDER'] = ('Hospital Management', os.getenv('MAIL_DEFAULT_SENDER', 'noreply@hospital.com'))

# celery config
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_TASK_SERIALIZER'] = 'json'
app.config['CELERY_ACCEPT_CONTENT'] = ['json']
app.config['CELERY_RESULT_SERIALIZER'] = 'json'
app.config['DEBUG'] = True

# initialize extensions
db.init_app(app)
CORS(app)
mail = Mail(app)

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

# register blueprints
from models import *
from routes import *

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
app.register_blueprint(patient_bp, url_prefix='/api/patient')

# routes
@app.route('/download/<filename>')  
def download_file(filename):
    return send_from_directory('.', filename)

# error handlers
@app.errorhandler(404)
def not_found(error):
    # return json for api routes, html for others
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'message': f'Endpoint not found: {request.path}'
        }), 404
    # for non-api routes, serve the frontend
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

# catch-all route for frontend routing (must be last)
@app.route('/<path:path>')
def serve_frontend(path):
    # serve static files if they exist
    frontend_path = os.path.join('../frontend', path)
    if os.path.exists(frontend_path) and os.path.isfile(frontend_path):
        return send_from_directory('../frontend', path)
    # otherwise serve index.html for client-side routing
    return send_from_directory('../frontend', 'index.html')

# database initialization
def setup_db():
    with app.app_context():
        db.create_all()
        
        # create admin if not exists
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

# application entry point
if __name__ == '__main__':
    setup_db()
    app.run(debug=True, port=5000)