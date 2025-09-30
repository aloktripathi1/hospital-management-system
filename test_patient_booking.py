#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000/api"

def test_patient_booking():
    # Session to maintain cookies
    session = requests.Session()
    
    print("=== Testing Patient Appointment Booking ===")
    
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
    
    # 2. Get departments
    print("\n2. Getting departments...")
    response = session.get(f"{BASE_URL}/patient/departments")
    print(f"Departments Response: {response.status_code}")
    
    if response.status_code == 200:
        departments_result = response.json()
        if departments_result.get('success'):
            departments = departments_result['data']['departments']
            print(f"✅ Found {len(departments)} departments")
            for dept in departments[:3]:  # Show first 3
                print(f"  - {dept['name']}")
        else:
            print("❌ Failed to get departments")
            return
    else:
        print("❌ Departments request failed!")
        return
    
    # 3. Get doctors by specialization
    print("\n3. Getting doctors for Cardiology...")
    cardiology_dept = next((d for d in departments if d['name'] == 'Cardiology'), None)
    
    if not cardiology_dept:
        print("❌ Cardiology department not found!")
        return
        
    response = session.get(f"{BASE_URL}/patient/doctors?specialization=Cardiology")
    print(f"Doctors Response: {response.status_code}")
    
    if response.status_code == 200:
        doctors_result = response.json()
        if doctors_result.get('success'):
            doctors = doctors_result['data']['doctors']
            print(f"✅ Found {len(doctors)} cardiology doctors")
            for doctor in doctors:
                print(f"  - Dr. {doctor['name']} (ID: {doctor['id']})")
        else:
            print("❌ Failed to get doctors")
            return
    else:
        print("❌ Doctors request failed!")
        return
    
    if not doctors:
        print("❌ No doctors found!")
        return
        
    # 4. Get available slots for first doctor
    doctor = doctors[0]
    test_date = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"\n4. Getting available slots for Dr. {doctor['name']} on {test_date}...")
    response = session.get(f"{BASE_URL}/patient/available-slots?doctor_id={doctor['id']}&date={test_date}")
    print(f"Available Slots Response: {response.status_code}")
    
    if response.status_code == 200:
        slots_result = response.json()
        if slots_result.get('success'):
            slots = slots_result['data']['slots']
            available_slots = [s for s in slots if s['status'] == 'available']
            print(f"✅ Found {len(available_slots)} available slots (2-hour each)")
            for slot in available_slots[:3]:  # Show first 3
                print(f"  - {slot['time']} (ID: {slot['id']})")
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
        
    # 5. Try to book an appointment
    first_slot = available_slots[0]
    print(f"\n5. Booking appointment for {first_slot['time']} on {test_date}...")
    
    booking_data = {
        "doctor_id": doctor['id'],
        "appointment_date": test_date,
        "appointment_time": first_slot['time'],
        "notes": "Test booking with 2-hour slots"
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
            print(f"Time Slot: {appointment['appointment_time']} (2-hour duration)")
        else:
            print("❌ Failed to book appointment!")
            print(f"Error: {booking_result.get('message')}")
    else:
        print("❌ Booking request failed!")

if __name__ == "__main__":
    test_patient_booking()
