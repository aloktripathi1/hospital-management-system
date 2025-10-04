from flask import Flask, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from celery import Celery
from database import db

# ----------- Flask App Setup -----------
app = Flask(__name__, static_folder='../frontend/assets', static_url_path='/static')

# ----------- Config -----------
app.config['SECRET_KEY'] = 'this-is-a-secret-key-for-hospital-management'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital-management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# ----------- Initialize Extensions -----------
db.init_app(app)
CORS(app)

# ----------- Celery Setup -----------
def make_celery(flask_app):
    celery_app = Celery(
        flask_app.import_name,
        backend=flask_app.config['CELERY_RESULT_BACKEND'],
        broker=flask_app.config['CELERY_BROKER_URL']
    )
    celery_app.conf.update(flask_app.config)
    
    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)
    
    celery_app.Task = ContextTask
    return celery_app

celery = make_celery(app)

# ----------- Import Models and Routes -----------
from models import *
from routes import *

# ----------- register blueprints ----------
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
app.register_blueprint(patient_bp, url_prefix='/api/patient')

# ----------- Main Route -----------
@app.route('/')
def home():
    return send_from_directory('../frontend', 'index.html')

# ----------- Database Setup -----------
def setup_database():
    with app.app_context():
        db.create_all()
        
        # Create admin if not exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@medihub.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin created: admin/admin123")

# ----------- Run App -----------
if __name__ == '__main__':
    setup_database()
    app.run(debug=True, port=5000)