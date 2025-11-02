#!/usr/bin/env python3

import requests
import json
import sys

# Test API endpoints
BASE_URL = "http://127.0.0.1:5000"

def test_auth():
    print("🧪 Testing Authentication APIs")
    print("=" * 50)
    
    # Test admin login
    print("1. Testing Admin Login...")
    login_data = {
        "username": "admin",
        "password": "Admin@123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json=login_data,
                               headers={"Content-Type": "application/json"})
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Admin login SUCCESS")
                return response.cookies
            else:
                print("   ❌ Admin login FAILED")
                print(f"   Error: {result.get('message', 'Unknown error')}")
        else:
            print("   ❌ Admin login FAILED - HTTP Error")
            
    except Exception as e:
        print(f"   ❌ Admin login FAILED - Exception: {e}")
    
    return None

def test_admin_apis(cookies):
    if not cookies:
        print("   ⏭️  Skipping admin API tests - no valid session")
        return
        
    print("\n2. Testing Admin APIs...")
    
    endpoints = [
        "/api/admin/dashboard-stats",
        "/api/admin/doctors", 
        "/api/admin/patients",
        "/api/admin/appointments",
        "/api/admin/departments"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", cookies=cookies)
            print(f"   {endpoint}: {response.status_code} - {'✅' if response.status_code == 200 else '❌'}")
            if response.status_code != 200:
                print(f"      Error: {response.text[:100]}")
        except Exception as e:
            print(f"   {endpoint}: ❌ Exception: {e}")

def test_doctor_auth():
    print("\n3. Testing Doctor Authentication...")
    login_data = {
        "username": "dr_ajay",
        "password": "Doctor#123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json=login_data,
                               headers={"Content-Type": "application/json"})
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Doctor login SUCCESS")
                return response.cookies
            else:
                print("   ❌ Doctor login FAILED")
                print(f"   Error: {result.get('message', 'Unknown error')}")
        else:
            print("   ❌ Doctor login FAILED - HTTP Error")
            
    except Exception as e:
        print(f"   ❌ Doctor login FAILED - Exception: {e}")
    
    return None

def test_patient_auth():
    print("\n4. Testing Patient Authentication...")
    login_data = {
        "username": "arjun87",
        "password": "Patient#123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json=login_data,
                               headers={"Content-Type": "application/json"})
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Patient login SUCCESS")
                return response.cookies
            else:
                print("   ❌ Patient login FAILED")
                print(f"   Error: {result.get('message', 'Unknown error')}")
        else:
            print("   ❌ Patient login FAILED - HTTP Error")
            
    except Exception as e:
        print(f"   ❌ Patient login FAILED - Exception: {e}")
    
    return None

if __name__ == "__main__":
    print("🏥 Hospital Management System - API Testing")
    print("=" * 60)
    
    # Test server health
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        sys.exit(1)
    
    # Run tests
    admin_cookies = test_auth()
    test_admin_apis(admin_cookies)
    test_doctor_auth()
    test_patient_auth()
    
    print("\n" + "=" * 60)
    print("🏁 API Testing Complete")