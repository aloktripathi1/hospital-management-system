from flask import Blueprint, request, jsonify, session
from database import db
from models import User, Patient, Doctor, Appointment, Treatment, DoctorAvailability
from datetime import datetime, date, time, timedelta
from decorators import patient_required, patient_or_admin_required

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/dashboard', methods=['GET'])
@patient_required
def get_dashboard():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    if patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient profile not found',
            'errors': ['Profile not found']
        }), 404
    
    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.appointment_date >= date.today(),
        Appointment.status == 'booked'
    ).count()
    
    total = Appointment.query.filter_by(patient_id=patient.id).count()
    
    doctors = db.session.query(Appointment.doctor_id).filter_by(
        patient_id=patient.id
    ).distinct().count()
    
    return jsonify({
        'success': True,
        'message': 'Dashboard data retrieved',
        'data': {
            'patient': patient.to_dict(),
            'upcoming_appointments': upcoming,
            'total_appointments': total,
            'doctors_visited': doctors
        }
    })

@patient_bp.route('/departments', methods=['GET'])
@patient_or_admin_required
def get_departments():
    from models import Department
    
    departments = Department.query.filter_by(is_active=True).all()
    
    data = []
    
    for dept in departments:
        doctors = Doctor.query.filter_by(
            department_id=dept.id, 
            is_active=True
        ).all()
        
        docs = []
        
        for doc in doctors:
            info = {
                'id': doc.id,
                'name': doc.name,
                'department': dept.name
            }
            docs.append(info)
        
        dept_info = {
            'id': dept.id,
            'name': dept.name,
            'description': dept.description,
            'doctor_count': len(docs),
            'doctors': docs
        }
        data.append(dept_info)
    
    return jsonify({
        'success': True,
        'message': 'Departments retrieved successfully',
        'data': {
            'departments': data
        }
    })

@patient_bp.route('/available-slots', methods=['GET'])
@patient_required
def get_available_slots():
    doctor_id = request.args.get('doctor_id')
    date_str = request.args.get('date')
    
    if not doctor_id:
        return jsonify({
            'success': False,
            'message': 'Doctor ID is required',
            'errors': ['Missing doctor_id']
        }), 400
    
    if not date_str:
        return jsonify({
            'success': False,
            'message': 'Date is required',
            'errors': ['Missing date']
        }), 400
    
    apt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    available = Appointment.query.filter_by(
        doctor_id=doctor_id,
        appointment_date=apt_date,
        status='available'
    ).order_by(Appointment.appointment_time.asc()).all()
    
    booked = Appointment.query.filter_by(
        doctor_id=doctor_id,
        appointment_date=apt_date,
        status='booked'
    ).order_by(Appointment.appointment_time.asc()).all()
    
    total = len(available) + len(booked)
    if total == 0:
        day = apt_date.weekday()
        avail = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=day,
            is_available=True
        ).first()
        
        if avail:
            start = avail.start_time
            end = avail.end_time
        else:
            start = time(9, 0)
            end = time(17, 0)
        
        slot_time = start
        while slot_time < end:
            slot = Appointment(
                doctor_id=doctor_id,
                patient_id=None,
                appointment_date=apt_date,
                appointment_time=slot_time,
                status='available',
                notes=''
            )
            db.session.add(slot)
            
            slot_dt = datetime.combine(apt_date, slot_time)
            next_dt = slot_dt + timedelta(hours=2)
            slot_time = next_dt.time()
        
        db.session.commit()
        
        available = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=apt_date,
            status='available'
        ).order_by(Appointment.appointment_time.asc()).all()

    slots = []
    
    for slot in available:
        start_dt = datetime.combine(apt_date, slot.appointment_time)
        end_dt = start_dt + timedelta(hours=2)
        end_time = end_dt.time()
        
        info = {
            'id': slot.id,
            'time': f"{slot.appointment_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
            'start_time': slot.appointment_time.strftime('%H:%M'),
            'end_time': end_time.strftime('%H:%M'),
            'status': 'available',
            'patient_id': None
        }
        slots.append(info)
    
    for slot in booked:
        start_dt = datetime.combine(apt_date, slot.appointment_time)
        end_dt = start_dt + timedelta(hours=2)
        end_time = end_dt.time()
        
        info = {
            'id': slot.id,
            'time': f"{slot.appointment_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
            'start_time': slot.appointment_time.strftime('%H:%M'),
            'end_time': end_time.strftime('%H:%M'),
            'status': 'booked',
            'patient_id': slot.patient_id
        }
        slots.append(info)
    
    return jsonify({
        'success': True,
        'message': 'Available slots retrieved successfully',
        'data': {
            'slots': slots,
            'date': apt_date.isoformat(),
            'doctor_id': doctor_id
        }
    })

@patient_bp.route('/doctors', methods=['GET'])
@patient_required
def get_doctors():
    try:
        dept = request.args.get('department')
        
        query = Doctor.query.filter_by(is_active=True)
        
        if dept:
            from models import Department
            query = query.join(Department).filter(Department.name == dept)
        
        doctors = query.all()
        
        return jsonify({
            'success': True,
            'message': 'Doctors retrieved successfully',
            'data': {
                'doctors': [doc.to_dict() for doc in doctors]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get doctors',
            'errors': [str(e)]
        }), 500

@patient_bp.route('/appointments', methods=['GET'])
@patient_required
def get_appointments():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    if patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient profile not found',
            'errors': ['Profile not found']
        }), 404
    
    status = request.args.get('status')
    
    query = Appointment.query.filter_by(patient_id=patient.id)
    
    if status:
        query = query.filter_by(status=status)
    
    appointments = query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).all()
    
    return jsonify({
        'success': True,
        'message': 'Appointments retrieved successfully',
        'data': {
            'appointments': [apt.to_dict() for apt in appointments]
        }
    })

@patient_bp.route('/appointments', methods=['POST'])
@patient_required
def book_appointment():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    if patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient profile not found',
            'errors': ['Profile not found']
        }), 404
    
    data = request.get_json()
    
    if not data.get('doctor_id'):
        return jsonify({
            'success': False,
            'message': 'Doctor ID is required',
            'errors': ['Missing doctor_id']
        }), 400
    
    if not data.get('appointment_date'):
        return jsonify({
            'success': False,
            'message': 'Appointment date is required',
            'errors': ['Missing appointment_date']
        }), 400
    
    if not data.get('appointment_time'):
        return jsonify({
            'success': False,
            'message': 'Appointment time is required',
            'errors': ['Missing appointment_time']
        }), 400
    
    doctor = Doctor.query.get(data['doctor_id'])
    if doctor is None or not doctor.is_active:
        return jsonify({
            'success': False,
            'message': 'Doctor not found or inactive',
            'errors': ['Invalid doctor']
        }), 404
    
    apt_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
    
    time_str = data['appointment_time']
    if '-' in time_str:
        start = time_str.split('-')[0].strip()
        apt_time = datetime.strptime(start, '%H:%M').time()
    else:
        apt_time = datetime.strptime(time_str, '%H:%M').time()
    
    slot = Appointment.query.filter_by(
        doctor_id=data['doctor_id'],
        appointment_date=apt_date,
        appointment_time=apt_time,
        status='available'
    ).first()
    
    if slot is None:
        return jsonify({
            'success': False,
            'message': 'Time slot not available',
            'errors': ['This time slot is not available for booking']
        }), 400
    
    existing = Appointment.query.filter_by(
        patient_id=patient.id,
        appointment_date=apt_date,
        appointment_time=apt_time,
        status='booked'
    ).first()
    
    if existing:
        return jsonify({
            'success': False,
            'message': 'You already have an appointment at this time',
            'errors': ['Time slot already booked']
        }), 400
    
    slot.patient_id = patient.id
    slot.status = 'booked'
    slot.notes = data.get('notes', '')
    slot.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Appointment booked successfully',
        'data': {
            'appointment': slot.to_dict()
        }
    })

@patient_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@patient_required
def cancel_appointment(appointment_id):
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    if patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient profile not found',
            'errors': ['Profile not found']
        }), 404
    
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        patient_id=patient.id
    ).first()
    
    if appointment is None:
        return jsonify({
            'success': False,
            'message': 'Appointment not found',
            'errors': ['Appointment not found']
        }), 404
    
    if appointment.status != 'booked':
        return jsonify({
            'success': False,
            'message': 'Cannot cancel this appointment',
            'errors': ['Invalid status']
        }), 400
    
    appointment.status = 'cancelled'
    appointment.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Appointment cancelled successfully',
        'data': {}
    })

@patient_bp.route('/history', methods=['GET'])
@patient_required
def get_history():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    if patient is None:
        return jsonify({
            'success': False,
            'message': 'Patient profile not found',
            'errors': ['Profile not found']
        }), 404
    
    treatments = db.session.query(Treatment).join(Appointment).filter(
        Appointment.patient_id == patient.id
    ).order_by(Treatment.created_at.desc()).all()
    
    # Include appointment and doctor information with each treatment
    treatment_data = []
    for treatment in treatments:
        treatment_dict = treatment.to_dict()
        
        # Get the appointment details
        appointment = Appointment.query.get(treatment.appointment_id)
        if appointment:
            treatment_dict['appointment'] = {
                'id': appointment.id,
                'appointment_date': appointment.appointment_date.isoformat() if appointment.appointment_date else None,
                'appointment_time': str(appointment.appointment_time) if appointment.appointment_time else None,
                'status': appointment.status
            }
            
            # Get doctor information
            if appointment.doctor:
                treatment_dict['doctor'] = {
                    'id': appointment.doctor.id,
                    'name': appointment.doctor.name,
                    'specialization': appointment.doctor.specialization,
                    'department': appointment.doctor.department.name if appointment.doctor.department else None
                }
            else:
                treatment_dict['doctor'] = None
        
        treatment_data.append(treatment_dict)
    
    return jsonify({
        'success': True,
        'message': 'Patient history retrieved successfully',
        'data': {
            'treatments': treatment_data
        }
    })

@patient_bp.route('/doctor/availability/<int:doctor_id>', methods=['GET'])
@patient_required
def get_doctor_availability(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    
    if doctor is None or not doctor.is_active:
        return jsonify({
            'success': False,
            'message': 'Doctor not found or inactive',
            'errors': ['Invalid doctor']
        }), 404
    
    availability = DoctorAvailability.query.filter_by(
        doctor_id=doctor_id,
        is_available=True
    ).all()
    
    return jsonify({
        'success': True,
        'message': 'Doctor availability retrieved successfully',
        'data': {
            'doctor': doctor.to_dict(),
            'availability': [avail.to_dict() for avail in availability]
        }
    })

@patient_bp.route('/export-history', methods=['POST'])
@patient_required
def export_patient_history():
    try:
        user_id = session.get('user_id')
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient profile not found',
                'errors': ['Profile not found']
            }), 404
        
        from tasks.celery_tasks import export_patient_history_csv
        task = export_patient_history_csv.delay(patient.id)
        
        return jsonify({
            'success': True,
            'message': 'CSV export started. You will be notified when ready.',
            'data': {
                'task_id': task.id
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to start CSV export',
            'errors': [str(e)]
        }), 500

@patient_bp.route('/profile', methods=['PUT'])
@patient_required
def update_patient_profile():
    try:
        user_id = session.get('user_id')
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({
                'success': False,
                'message': 'Patient profile not found',
                'errors': ['Profile not found']
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'errors': ['Missing data']
            }), 400
        
        if 'name' in data:
            patient.name = data['name']
        if 'phone' in data:
            patient.phone = data['phone']
        if 'address' in data:
            patient.address = data['address']
        if 'age' in data:
            patient.age = data['age']
        if 'gender' in data:
            patient.gender = data['gender']
        if 'medical_history' in data:
            patient.medical_history = data['medical_history']
        if 'emergency_contact' in data:
            patient.emergency_contact = data['emergency_contact']
        
        if 'email' in data:
            patient.user.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': {
                'patient': patient.to_dict()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update profile',
            'errors': [str(e)]
        }), 500