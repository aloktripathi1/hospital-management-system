#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000/api"

def test_patient_booking():
    # Session to maintain cookies
    session = requests.Session()
    
    print("=== Testing Patient Appointment Booking (2-Slot System) ===")
    
    # 1. Login as patient
    print("1. Logging in as patient...")
    login_data = {
        "username": "patient1",
        "password": "patient123"
    }
    
    response = session.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login Response: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Login failed!")
        return
        
    login_result = response.json()
    if not login_result.get('success'):
        print("❌ Login unsuccessful!")
        return
    
    print("✅ Patient login successful!")
    
    # 2. Get all doctors
    print("\n2. Getting all doctors...")
    response = session.get(f"{BASE_URL}/patient/doctors")
    print(f"Doctors Response: {response.status_code}")
    
    if response.status_code == 200:
        doctors_result = response.json()
        if doctors_result.get('success'):
            doctors = doctors_result['data']['doctors']
            print(f"✅ Found {len(doctors)} doctors")
            for doctor in doctors[:3]:  # Show first 3
                print(f"  - Dr. {doctor['name']} ({doctor['specialization']}, ID: {doctor['id']})")
        else:
            print("❌ Failed to get doctors")
            return
    else:
        print("❌ Doctors request failed!")
        return
    
    if not doctors:
        print("❌ No doctors found!")
        return
        
    # 3. Get available slots for first doctor (2-slot system: morning/evening)
    doctor = doctors[0]
    test_date = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"\n3. Getting available slots for Dr. {doctor['name']} on {test_date}...")
    print("Note: Using 2-slot system - Morning (9AM-1PM) and Evening (3PM-7PM)")
    response = session.get(f"{BASE_URL}/patient/available-slots?doctor_id={doctor['id']}&date={test_date}")
    print(f"Available Slots Response: {response.status_code}")
    
    if response.status_code == 200:
        slots_result = response.json()
        if slots_result.get('success'):
            slots = slots_result['data']['slots']
            available_slots = [s for s in slots if s['status'] == 'available']
            print(f"✅ Found {len(available_slots)} available slots")
            for slot in available_slots:
                print(f"  - {slot['display']} ({slot['slot_type']})")
        else:
            print("❌ Failed to get available slots")
            print(f"Error: {slots_result.get('message')}")
            return
    else:
        print("❌ Available slots request failed!")
        return
    
    if not available_slots:
        print("❌ No available slots found!")
        return
        
    # 4. Try to book an appointment
    first_slot = available_slots[0]
    print(f"\n4. Booking appointment for {first_slot['display']} on {test_date}...")
    
    booking_data = {
        "doctor_id": doctor['id'],
        "appointment_date": test_date,
        "appointment_time": first_slot['appointment_time'],  # Either "09:00" or "15:00"
        "notes": "Test booking with 2-slot system (morning/evening)"
    }
    
    print(f"Booking Data: {json.dumps(booking_data, indent=2)}")
    
    response = session.post(f"{BASE_URL}/patient/appointments", json=booking_data)
    print(f"Booking Response: {response.status_code}")
    print(f"Booking Data: {response.text}")
    
    if response.status_code == 200:
        booking_result = response.json()
        if booking_result.get('success'):
            print("✅ Appointment booked successfully!")
            appointment = booking_result['data']['appointment']
            print(f"Appointment ID: {appointment['id']}")
            print(f"Time Slot: {first_slot['display']}")
            print(f"Appointment Time: {appointment['appointment_time']}")
        else:
            print("❌ Failed to book appointment!")
            print(f"Error: {booking_result.get('message')}")
    else:
        print("❌ Booking request failed!")

if __name__ == "__main__":
    test_patient_booking()
