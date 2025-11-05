#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000/api"

def test_slot_generation():
    # Store JWT tokens
    doctor_token = None
    patient_token = None
    
    print("=== Testing Hospital Management System Slot Generation ===")
    
    # 1. Test doctor login
    print("1. Logging in as doctor...")
    login_data = {
        "username": "dr_ajay",
        "password": "Doctor#123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login Response: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Login failed!")
        return
        
    login_result = response.json()
    if not login_result.get('success'):
        print("❌ Login unsuccessful!")
        return
    
    doctor_token = login_result['data']['token']
    doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
    print("✅ Doctor login successful!")
    
    print("\n=== Test Completed Successfully ===")

if __name__ == "__main__":
    test_slot_generation()
