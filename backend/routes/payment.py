from flask import Blueprint, request, jsonify
from database import db
from models import Appointment, Patient, Doctor
from datetime import datetime
from decorators import patient_required, get_current_user_id
import razorpay
import os

payment_bp = Blueprint('payment', __name__)

# razorpay credentials (demo/test mode)
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'rzp_test_demo')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', 'demo_secret')

# initialize razorpay client
try:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
except:
    razorpay_client = None
    print("Warning: Razorpay client not initialized. Payment features will be disabled.")

# create payment order for appointment
@payment_bp.route('/create-order', methods=['POST'])
@patient_required
def create_payment_order():
    try:
        if not razorpay_client:
            return jsonify({'success': False, 'message': 'Payment service not configured'}), 500
        
        user_id = get_current_user_id()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'success': False, 'message': 'Patient profile not found'}), 404
        
        data = request.get_json()
        
        if not data.get('appointment_id'):
            return jsonify({'success': False, 'message': 'Appointment ID is required'}), 400
        
        appointment = Appointment.query.get(data['appointment_id'])
        
        if not appointment:
            return jsonify({'success': False, 'message': 'Appointment not found'}), 404
        
        if appointment.patient_id != patient.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        doctor = Doctor.query.get(appointment.doctor_id)
        
        if not doctor:
            return jsonify({'success': False, 'message': 'Doctor not found'}), 404
        
        # amount in paise (1 INR = 100 paise)
        amount = int(doctor.consultation_fee * 100)
        
        # create razorpay order
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'apt_{appointment.id}',
            'payment_capture': 1
        }
        
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        return jsonify({
            'success': True,
            'message': 'Payment order created',
            'data': {
                'order_id': razorpay_order['id'],
                'amount': amount,
                'currency': 'INR',
                'key_id': RAZORPAY_KEY_ID,
                'appointment_id': appointment.id,
                'doctor_name': doctor.name,
                'consultation_fee': doctor.consultation_fee
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to create payment order', 'errors': [str(e)]}), 500

# verify payment
@payment_bp.route('/verify', methods=['POST'])
@patient_required
def verify_payment():
    try:
        if not razorpay_client:
            return jsonify({'success': False, 'message': 'Payment service not configured'}), 500
        
        user_id = get_current_user_id()
        patient = Patient.query.filter_by(user_id=user_id).first()
        
        if not patient:
            return jsonify({'success': False, 'message': 'Patient profile not found'}), 404
        
        data = request.get_json()
        
        if not all(k in data for k in ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'appointment_id']):
            return jsonify({'success': False, 'message': 'Missing payment verification data'}), 400
        
        appointment = Appointment.query.get(data['appointment_id'])
        
        if not appointment:
            return jsonify({'success': False, 'message': 'Appointment not found'}), 404
        
        if appointment.patient_id != patient.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # verify signature
        params_dict = {
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        }
        
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # payment verified successfully
            # you can store payment info in appointment or create a separate payment model
            appointment.notes = f"{appointment.notes}\nPaid: ₹{Doctor.query.get(appointment.doctor_id).consultation_fee}"
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Payment verified successfully', 'data': {'payment_id': data['razorpay_payment_id']}})
            
        except razorpay.errors.SignatureVerificationError:
            return jsonify({'success': False, 'message': 'Payment verification failed'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to verify payment', 'errors': [str(e)]}), 500

# get payment details
@payment_bp.route('/payment/<payment_id>', methods=['GET'])
@patient_required
def get_payment_details(payment_id):
    try:
        if not razorpay_client:
            return jsonify({'success': False, 'message': 'Payment service not configured'}), 500
        
        payment = razorpay_client.payment.fetch(payment_id)
        
        return jsonify({'success': True, 'message': 'Payment details retrieved', 'data': {'payment': payment}})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to get payment details', 'errors': [str(e)]}), 500
