from flask import Blueprint, request, jsonify, session
from database import db
from models import User, Doctor, Patient, Appointment, Treatment, DoctorAvailability
from datetime import datetime, date, time, timedelta
from decorators import doctor_required

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard', methods=['GET'])
@doctor_required
def get_dashboard():
    try:
        user_id = session.get('user_id')
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({
                'success': False,
                'message': 'Doctor profile not found',
                'errors': ['Profile not found']
            }), 404
        
        # Get today's appointments
        today_appointments = Appointment.query.filter_by(
            doctor_id=doctor.id,
            appointment_date=date.today()
        ).count()
        
        # Get upcoming appointments
        upcoming_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= date.today(),
            Appointment.status == 'booked'
        ).count()
        
        # Get total patients treated
        total_patients = db.session.query(Appointment.patient_id).filter_by(
            doctor_id=doctor.id
        ).distinct().count()
        
        return jsonify({
            'success': True,
            'message': 'Dashboard data retrieved',
            'data': {
                'doctor': doctor.to_dict(),
                'today_appointments': today_appointments,
                'upcoming_appointments': upcoming_appointments,
                'total_patients': total_patients
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get dashboard data',
            'errors': [str(e)]
        }), 500

@doctor_bp.route('/appointments', methods=['GET'])
@doctor_required
def get_appointments():
    try:
        user_id = session.get('user_id')
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({
                'success': False,
                'message': 'Doctor profile not found',
                'errors': ['Profile not found']
            }), 404
        
        # Get appointments with optional date filter
        date_filter = request.args.get('date')
        status_filter = request.args.get('status')
        
        query = Appointment.query.filter_by(doctor_id=doctor.id)
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter_by(appointment_date=filter_date)
            except ValueError:
                pass
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        appointments = query.order_by(
            Appointment.appointment_date.asc(),
            Appointment.appointment_time.asc()
        ).all()
        
        return jsonify({
            'success': True,
            'message': 'Appointments retrieved successfully',
            'data': {
                'appointments': [appointment.to_dict() for appointment in appointments]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get appointments',
            'errors': [str(e)]
        }), 500

@doctor_bp.route('/patients', methods=['GET'])
@doctor_required
def get_patients():
    try:
        user_id = session.get('user_id')
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({
                'success': False,
                'message': 'Doctor profile not found',
                'errors': ['Profile not found']
            }), 404
        
        # Get unique patients who have appointments with this doctor
        patients = db.session.query(Patient).join(Appointment).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().all()
        
        return jsonify({
            'success': True,
            'message': 'Patients retrieved successfully',
            'data': {
                'patients': [patient.to_dict() for patient in patients]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get patients',
            'errors': [str(e)]
        }), 500

@doctor_bp.route('/patient-history', methods=['POST'])
@doctor_required
def add_patient_history():
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
        appointment_id = data.get('appointment_id')
        
        if not appointment_id:
            return jsonify({
                'success': False,
                'message': 'Appointment ID is required',
                'errors': ['Missing appointment_id']
            }), 400
        
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            doctor_id=doctor.id
        ).first()
        
        if not appointment:
            return jsonify({
                'success': False,
                'message': 'Appointment not found',
                'errors': ['Appointment not found']
            }), 404
        
        # Create treatment record
        treatment = Treatment(
            appointment_id=appointment_id,
            diagnosis=data.get('diagnosis', ''),
            prescription=data.get('prescription', ''),
            visit_type=data.get('visit_type', 'consultation'),
            symptoms=data.get('symptoms', ''),
            treatment_notes=data.get('treatment_notes', '')
        )
        
        db.session.add(treatment)
        
        # Update appointment status
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
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update patient history',
            'errors': [str(e)]
        }), 500

@doctor_bp.route('/patient-history/<int:patient_id>', methods=['GET'])
@doctor_required
def get_patient_history(patient_id):
    try:
        user_id = session.get('user_id')
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({
                'success': False,
                'message': 'Doctor profile not found',
                'errors': ['Profile not found']
            }), 404
        
        # Get patient's treatment history with this doctor
        treatments = db.session.query(Treatment).join(Appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.doctor_id == doctor.id
        ).order_by(Treatment.created_at.desc()).all()
        
        patient = Patient.query.get(patient_id)
        
        return jsonify({
            'success': True,
            'message': 'Patient history retrieved successfully',
            'data': {
                'patient': patient.to_dict() if patient else None,
                'treatments': [treatment.to_dict() for treatment in treatments]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get patient history',
            'errors': [str(e)]
        }), 500

@doctor_bp.route('/availability', methods=['GET'])
@doctor_required
def get_availability():
    try:
        user_id = session.get('user_id')
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        
        if not doctor:
            return jsonify({
                'success': False,
                'message': 'Doctor profile not found',
                'errors': ['Profile not found']
            }), 404
        
        availability = DoctorAvailability.query.filter_by(doctor_id=doctor.id).all()
        
        return jsonify({
            'success': True,
            'message': 'Availability retrieved successfully',
            'data': {
                'availability': [avail.to_dict() for avail in availability]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to get availability',
            'errors': [str(e)]
        }), 500

@doctor_bp.route('/availability', methods=['PUT'])
@doctor_required
def update_availability():
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
        availability_data = data.get('availability', [])
        
        # Clear existing availability
        DoctorAvailability.query.filter_by(doctor_id=doctor.id).delete()
        
        # Add new availability
        for avail in availability_data:
            availability = DoctorAvailability(
                doctor_id=doctor.id,
                day_of_week=avail['day_of_week'],
                start_time=datetime.strptime(avail['start_time'], '%H:%M').time(),
                end_time=datetime.strptime(avail['end_time'], '%H:%M').time(),
                is_available=avail.get('is_available', True)
            )
            db.session.add(availability)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Availability updated successfully',
            'data': {}
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update availability',
            'errors': [str(e)]
        }), 500

@doctor_bp.route('/set-slots', methods=['POST'])
@doctor_required
def set_availability_slots():
    """Create 2-hour appointment slots for a specific date range"""
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
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
        start_time = datetime.strptime(data.get('start_time', '09:00'), '%H:%M').time()
        end_time = datetime.strptime(data.get('end_time', '17:00'), '%H:%M').time()
        
        slots_created = 0
        
        # Optional break periods
        break_periods = data.get('break_periods', []) or []

        # Clear existing available slots in this date range to avoid duplicates
        Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date,
            Appointment.status == 'available'
        ).delete(synchronize_session=False)

        # Generate slots for each day in the range
        current_date = start_date
        while current_date <= end_date:
            # Always use provided time window for simplicity
            slot_start = start_time
            slot_end = end_time
            
            # Build excluded break windows as time tuples for the day
            day_breaks = []
            for br in break_periods:
                try:
                    bt = datetime.strptime(br.get('start_time','00:00'), '%H:%M').time()
                    et = datetime.strptime(br.get('end_time','00:00'), '%H:%M').time()
                    if bt < et:
                        day_breaks.append((bt, et))
                except Exception:
                    continue

            # Helper to check if a time is inside any break
            def in_break(t: time) -> bool:
                for bt, et in day_breaks:
                    if bt <= t < et:
                        return True
                return False

            # Create 2-hour slots excluding breaks
            current_time = slot_start
            while current_time < slot_end:
                if not in_break(current_time):
                    slot = Appointment(
                        doctor_id=doctor.id,
                        patient_id=None,
                        appointment_date=current_date,
                        appointment_time=current_time,
                        status='available',
                        notes=''
                    )
                    db.session.add(slot)
                    slots_created += 1

                # Move to next 2-hour slot
                current_time = (datetime.combine(current_date, current_time) + timedelta(hours=2)).time()
            
            current_date += timedelta(days=1)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Created {slots_created} appointment slots',
            'data': {
                'slots_created': slots_created,
                'date_range': f'{start_date} to {end_date}'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to create appointment slots',
            'errors': [str(e)]
        }), 500
