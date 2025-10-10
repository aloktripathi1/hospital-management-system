from flask import Blueprint, request, jsonify, session
from database import db
from models import User, Doctor, Patient, Appointment, Treatment, DoctorAvailability
from datetime import datetime, date, time, timedelta
from decorators import doctor_required

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard', methods=['GET'])
@doctor_required
def get_dashboard():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    # Get total appointments for this doctor (excluding available slots)
    total_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.status.in_(['booked', 'cancelled', 'completed'])
    ).count()

    total_patients = db.session.query(Appointment.patient_id).filter_by(
        doctor_id=doctor.id
    ).distinct().count()

    today_appointments = Appointment.query.filter_by(
        doctor_id=doctor.id,
        appointment_date=date.today()
    ).count()
    
    # # Get upcoming appointments for this doctor (booked appointments from today onwards)
    # upcoming_appointments = Appointment.query.filter(
    #     Appointment.doctor_id == doctor.id,
    #     Appointment.appointment_date >= date.today(),
    #     Appointment.status == 'booked'
    # ).count()
    
    return jsonify({
        'success': True,
        'message': 'Dashboard data retrieved',
        'data': {
            'doctor': doctor.to_dict(),
            'today_appointments': today_appointments,
            'total_appointments': total_appointments,
            'total_patients': total_patients
        }
    })

@doctor_bp.route('/patient-history/<int:patient_id>', methods=['GET'])
@doctor_required
def get_patient_history_details(patient_id):
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if doctor is None:
        return jsonify({"error": "Doctor not found"}), 404
    
    patient = Patient.query.get(patient_id)
    
    if patient is None:
        return jsonify({"error": "Patient not found"}), 404
    
    appointments = Appointment.query.filter_by(
        patient_id=patient_id
    ).filter(Appointment.status.in_(['booked', 'completed', 'cancelled', 'canceled'])).order_by(Appointment.appointment_date.desc()).all()
    
    history = []
    for apt in appointments:
        formatted_date = apt.appointment_date.strftime('%Y-%m-%d')
        formatted_time = apt.appointment_time.strftime('%H:%M')
        
        treatment = None
        if apt.treatments:
            latest = apt.treatments[-1]
            treatment = {
                'id': latest.id,
                'visit_type': latest.visit_type,
                'diagnosis': latest.diagnosis,
                'prescription': latest.prescription,
                'notes': latest.treatment_notes
            }
        
        apt_doctor = apt.doctor if apt.doctor else None
        doc_info = {
            'name': apt_doctor.name if apt_doctor else 'Unknown',
            'specialization': apt_doctor.specialization if apt_doctor else 'Unknown'
        }
        
        record = {
            'id': apt.id,
            'appointment_date': formatted_date,
            'appointment_time': formatted_time,
            'status': apt.status,
            'doctor': doc_info,
            'treatment': treatment
        }
        history.append(record)
    
    email = patient.user.email if patient.user else 'Not available'
    
    data = {
        'id': patient.id,
        'name': patient.name,
        'email': email,
        'phone': patient.phone,
        'address': patient.address,
        'age': patient.age,
        'gender': patient.gender,
        'medical_history': patient.medical_history,
        'appointments': history
    }
    
    return jsonify(data)

@doctor_bp.route('/appointments', methods=['GET'])
@doctor_required
def get_appointments():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    date_filter = request.args.get('date')
    status_filter = request.args.get('status')
    time_filter = request.args.get('time_filter')
    
    query = Appointment.query.filter_by(doctor_id=doctor.id)
    query = query.filter(Appointment.status.in_(['booked', 'canceled', 'cancelled', 'completed']))
    
    if time_filter == 'today':
        query = query.filter_by(appointment_date=date.today())
    elif time_filter == 'upcoming':
        query = query.filter(Appointment.appointment_date >= date.today())
        query = query.filter(Appointment.status.in_(['booked']))
    elif time_filter == 'completed':
        query = query.filter(Appointment.status == 'completed')
    else:
        from datetime import timedelta
        thirty_days_ago = date.today() - timedelta(days=30)
        query = query.filter(Appointment.appointment_date >= thirty_days_ago)
    
    if date_filter:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        query = query.filter_by(appointment_date=filter_date)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    appointments = query.order_by(
        Appointment.appointment_date.asc(),
        Appointment.appointment_time.asc()
    ).all()
    
    data = []
    for apt in appointments:
        data.append(apt.to_dict())
    
    return jsonify({
        'success': True,
        'message': 'Appointments retrieved successfully',
        'data': {
            'appointments': data
        }
    })

@doctor_bp.route('/patients', methods=['GET'])
@doctor_required
def get_patients():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    patients = db.session.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == doctor.id
    ).distinct().all()
    
    data = []
    for p in patients:
        data.append(p.to_dict())
    
    return jsonify({
        'success': True,
        'message': 'Patients retrieved successfully',
        'data': {
            'patients': data
        }
    })

@doctor_bp.route('/appointments/<int:appointment_id>/status', methods=['PUT'])
@doctor_required
def update_appointment_status(appointment_id):
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=doctor.id).first()
    
    if appointment is None:
        return jsonify({
            'success': False,
            'message': 'Appointment not found',
            'errors': ['Appointment not found']
        }), 404
    
    data = request.get_json()
    status = data.get('status')
    
    valid = ['completed', 'cancelled', 'booked']
    if status not in valid:
        return jsonify({
            'success': False,
            'message': 'Invalid status',
            'errors': ['Status must be completed, cancelled, or booked']
        }), 400
    
    appointment.status = status
    appointment.updated_at = datetime.utcnow()
    
    if 'notes' in data:
        appointment.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Appointment marked as {status}',
        'data': {
            'appointment': appointment.to_dict()
        }
    })

@doctor_bp.route('/patient-history', methods=['POST'])
@doctor_required
def add_patient_history():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    data = request.get_json()
    apt_id = data.get('appointment_id')
    
    if not apt_id:
        return jsonify({
            'success': False,
            'message': 'Appointment ID is required',
            'errors': ['Missing appointment_id']
        }), 400
    
    appointment = Appointment.query.filter_by(
        id=apt_id,
        doctor_id=doctor.id
    ).first()
    
    if appointment is None:
        return jsonify({
            'success': False,
            'message': 'Appointment not found',
            'errors': ['Appointment not found']
        }), 404
    
    treatment = Treatment(
        appointment_id=apt_id,
        diagnosis=data.get('diagnosis', ''),
        prescription=data.get('prescription', ''),
        visit_type=data.get('visit_type', 'consultation'),
        treatment_notes=data.get('treatment_notes', '')
    )
    
    db.session.add(treatment)
    
    appointment.status = 'completed'
    appointment.notes = data.get('notes', '')
    appointment.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Patient history updated successfully',
        'data': {
            'treatment': treatment.to_dict(),
            'appointment': appointment.to_dict()
        }
    })

@doctor_bp.route('/availability', methods=['GET'])
@doctor_required
def get_availability():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    availability = DoctorAvailability.query.filter_by(doctor_id=doctor.id).all()
    
    data = []
    for avail in availability:
        data.append(avail.to_dict())
    
    return jsonify({
        'success': True,
        'message': 'Availability retrieved successfully',
        'data': {
            'availability': data
        }
    })

@doctor_bp.route('/availability', methods=['PUT'])
@doctor_required
def update_availability():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    data = request.get_json()
    availability = data.get('availability', [])
    
    DoctorAvailability.query.filter_by(doctor_id=doctor.id).delete()
    
    for avail in availability:
        start = datetime.strptime(avail['start_time'], '%H:%M').time()
        end = datetime.strptime(avail['end_time'], '%H:%M').time()
        
        record = DoctorAvailability(
            doctor_id=doctor.id,
            day_of_week=avail['day_of_week'],
            start_time=start,
            end_time=end,
            is_available=avail.get('is_available', True)
        )
        db.session.add(record)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Availability updated successfully',
        'data': {}
    })

@doctor_bp.route('/set-slots', methods=['POST'])
@doctor_required
def set_availability_slots():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    data = request.get_json()
    
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
    
    start_time = datetime.strptime(data.get('start_time', '09:00'), '%H:%M').time()
    end_time = datetime.strptime(data.get('end_time', '17:00'), '%H:%M').time()
    
    total = 0
    
    breaks = data.get('break_periods', []) or []
    
    Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date,
        Appointment.status == 'available'
    ).delete(synchronize_session=False)
    
    current = start_date
    while current <= end_date:
        day_start = start_time
        day_end = end_time
        
        daily_breaks = []
        for brk in breaks:
            brk_start = datetime.strptime(brk.get('start_time', '00:00'), '%H:%M').time()
            brk_end = datetime.strptime(brk.get('end_time', '00:00'), '%H:%M').time()
            
            if brk_start < brk_end:
                daily_breaks.append((brk_start, brk_end))
        
        def in_break(check_time):
            for brk_start, brk_end in daily_breaks:
                if brk_start <= check_time < brk_end:
                    return True
            return False
        
        slot_time = day_start
        while slot_time < day_end:
            if not in_break(slot_time):
                slot = Appointment(
                    doctor_id=doctor.id,
                    patient_id=None,
                    appointment_date=current,
                    appointment_time=slot_time,
                    status='available',
                    notes=''
                )
                db.session.add(slot)
                total += 1
            
            next_slot = datetime.combine(current, slot_time) + timedelta(hours=2)
            slot_time = next_slot.time()
        
        current += timedelta(days=1)
    
    db.session.commit()
    
    date_range = f'{start_date} to {end_date}'
    
    return jsonify({
        'success': True,
        'message': f'Created {total} appointment slots',
        'data': {
            'slots_created': total,
            'date_range': date_range
        }
    })

@doctor_bp.route('/profile', methods=['PUT'])
@doctor_required
def update_doctor_profile():
    try:
        user_id = session.get('user_id')
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({
                'success': False,
                'message': 'Doctor profile not found',
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
            doctor.name = data['name']
        if 'specialization' in data:
            doctor.specialization = data['specialization']
        if 'department_id' in data:
            doctor.department_id = data['department_id']
        if 'experience' in data:
            doctor.experience = data['experience']
        if 'qualification' in data:
            doctor.qualification = data['qualification']
        if 'phone' in data:
            doctor.phone = data['phone']
        if 'consultation_fee' in data:
            doctor.consultation_fee = data['consultation_fee']
        
        if 'email' in data:
            doctor.user.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': {
                'doctor': doctor.to_dict()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update profile',
            'errors': [str(e)]
        }), 500

@doctor_bp.route('/available-slots', methods=['GET'])
@doctor_required
def get_available_slots():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    if doctor is None:
        return jsonify({
            'success': False,
            'message': 'Doctor profile not found',
            'errors': ['Profile not found']
        }), 404
    
    try:
        from datetime import date
        slots = Appointment.query.filter_by(
            doctor_id=doctor.id,
            status='available'
        ).filter(Appointment.appointment_date >= date.today()).order_by(
            Appointment.appointment_date.asc(),
            Appointment.appointment_time.asc()
        ).all()
        
        data = []
        for slot in slots:
            data.append({
                'id': slot.id,
                'date': slot.appointment_date.strftime('%Y-%m-%d'),
                'time': slot.appointment_time.strftime('%H:%M'),
                'formatted_display': f"{slot.appointment_date.strftime('%Y-%m-%d')} {slot.appointment_time.strftime('%H:%M')}"
            })
        
        return jsonify({
            'success': True,
            'message': 'Available slots retrieved successfully',
            'data': {
                'slots': data,
                'total_count': len(data)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve available slots',
            'errors': [str(e)]
        }), 500