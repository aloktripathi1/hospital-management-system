#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000/api"

def test_slot_generation():
    # Session to maintain cookies
    session = requests.Session()
    
    print("=== Testing Hospital Management System Slot Generation ===")
    
    # 1. Test doctor login
    print("1. Logging in as doctor...")
    login_data = {
        "username": "dr_smith",
        "password": "doctor123"
    }
    
    response = session.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login Response: {response.status_code}")
    print(f"Login Data: {response.text}")
    
    if response.status_code != 200:
        print("❌ Login failed!")
        return
        
    login_result = response.json()
    if not login_result.get('success'):
        print("❌ Login unsuccessful!")
        return
    
    print("✅ Login successful!")
    
    # 2. Test slot generation
    print("\n2. Testing slot generation...")
    
    # Generate slots for next week (now 2-hour slots from 9:00 to 9:00 next day)
    start_date = datetime.now().date() + timedelta(days=1)
    end_date = start_date + timedelta(days=6)
    
    slot_data = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "start_time": "09:00",
        "end_time": "21:00",  # 9 AM to 9 PM for 2-hour slots
        "break_periods": [
            {
                "start_time": "13:00", 
                "end_time": "14:00"   # 1 hour lunch break
            }
        ]
    }
    
    print(f"Slot Data: {json.dumps(slot_data, indent=2)}")
    print("Note: Now using 2-hour slots instead of 30-minute slots")
    print("Expected slots per day: 9AM-1PM (2 slots) + 2PM-9PM (3.5 slots) = ~5 slots per day")
    
    response = session.post(f"{BASE_URL}/doctor/set-slots", json=slot_data)
    print(f"Slot Generation Response: {response.status_code}")
    print(f"Slot Generation Data: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Slot generation successful!")
            print(f"Created {result['data']['slots_created']} slots")
            slots_per_day = result['data']['slots_created'] / 7
            print(f"Average slots per day: {slots_per_day:.1f}")
        else:
            print("❌ Slot generation failed!")
            print(f"Error: {result.get('message')}")
    else:
        print("❌ Slot generation request failed!")
    
    # 3. Test getting available slots (patient perspective)
    print("\n3. Testing patient login and getting available slots...")
    
    # Logout first
    session.post(f"{BASE_URL}/auth/logout")
    
    # Login as patient
    patient_login = {
        "username": "patient1",
        "password": "patient123"
    }
    
    response = session.post(f"{BASE_URL}/auth/login", json=patient_login)
    if response.status_code == 200 and response.json().get('success'):
        print("✅ Patient login successful!")
        
        # Get available slots
        doctor_id = 1  # Assuming dr_smith has id 1
        test_date = start_date.strftime('%Y-%m-%d')
        
        response = session.get(f"{BASE_URL}/patient/available-slots?doctor_id={doctor_id}&date={test_date}")
        print(f"Available Slots Response: {response.status_code}")
        print(f"Available Slots Data: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Available slots retrieved successfully!")
                slots = result['data']['slots']
                print(f"Found {len(slots)} slots")
                for slot in slots[:5]:  # Show first 5 slots
                    print(f"  - {slot['time']} ({slot['status']})")
            else:
                print("❌ Failed to get available slots!")
                print(f"Error: {result.get('message')}")
        else:
            print("❌ Available slots request failed!")
    else:
        print("❌ Patient login failed!")

if __name__ == "__main__":
    test_slot_generation()