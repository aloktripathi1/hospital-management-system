#!/usr/bin/env python3
"""
Test script to verify the API fix for the departments endpoint
"""
import requests
import json

# Test the departments endpoint that was causing 403 errors
def test_departments_endpoint():
    base_url = "http://127.0.0.1:5000"
    
    # First login as admin to get session
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    session = requests.Session()
    
    print("Testing API fix for departments endpoint...")
    print("1. Logging in as admin...")
    
    login_response = session.post(f"{base_url}/api/auth/login", json=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("✓ Admin login successful")
        
        # Now test the departments endpoint that was failing
        print("2. Testing /api/patient/departments endpoint...")
        dept_response = session.get(f"{base_url}/api/patient/departments")
        print(f"Departments endpoint status: {dept_response.status_code}")
        
        if dept_response.status_code == 200:
            print("✓ Departments endpoint now works for admin!")
            data = dept_response.json()
            if data.get('success'):
                print(f"✓ Retrieved {len(data.get('data', {}).get('departments', []))} departments")
            else:
                print("✗ Response indicates failure:", data.get('message'))
        elif dept_response.status_code == 403:
            print("✗ Still getting 403 Forbidden error")
        else:
            print(f"✗ Unexpected status code: {dept_response.status_code}")
            
    else:
        print("✗ Admin login failed")
        print("Response:", login_response.text)

if __name__ == "__main__":
    test_departments_endpoint()