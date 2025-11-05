#!/usr/bin/env python3
"""
Simple test script to verify JWT authentication is working
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_login():
    print("🧪 Testing JWT Login...")
    
    # Test admin login
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "Admin@123"
    })
    
    result = response.json()
    
    if result.get('success'):
        token = result['data']['token']
        print(f"✅ Login successful! Token received: {token[:50]}...")
        
        # Test authenticated request
        print("\n🧪 Testing authenticated request...")
        headers = {"Authorization": f"Bearer {token}"}
        
        me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        me_result = me_response.json()
        
        if me_result.get('success'):
            print(f"✅ Authenticated request successful!")
            print(f"   User: {me_result['data']['user']['username']}")
            print(f"   Role: {me_result['data']['user']['role']}")
        else:
            print(f"❌ Authenticated request failed: {me_result.get('message')}")
            
        # Test admin endpoint
        print("\n🧪 Testing admin-only endpoint...")
        stats_response = requests.get(f"{BASE_URL}/admin/dashboard-stats", headers=headers)
        
        if stats_response.status_code == 200:
            print(f"✅ Admin endpoint accessible!")
        else:
            print(f"❌ Admin endpoint failed with status {stats_response.status_code}")
            
    else:
        print(f"❌ Login failed: {result.get('message')}")

if __name__ == "__main__":
    print("=" * 60)
    print("JWT Authentication Test")
    print("=" * 60)
    print("\nMake sure Flask app is running on http://127.0.0.1:5000\n")
    
    try:
        test_login()
        print("\n" + "=" * 60)
        print("🎉 All JWT tests completed!")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running!")
    except Exception as e:
        print(f"❌ Error: {e}")
