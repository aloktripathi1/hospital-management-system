from app import app
from flask import json

with app.test_client() as client:
    # Login
    login_response = client.post('/api/auth/login', 
        json={'username': 'admin', 'password': 'admin'},
        content_type='application/json')
    
    login_data = json.loads(login_response.data)
    token = login_data['data']['token']
    
    # Get doctors
    response = client.get('/api/admin/doctors',
        headers={'Authorization': f'Bearer {token}'})
    
    data = json.loads(response.data)
    if data['success'] and len(data['data']['doctors']) > 0:
        doctor = data['data']['doctors'][0]
        print('=== DOCTOR DATA ===')
        print(json.dumps(doctor, indent=2))
        print('\n=== KEY CHECK ===')
        print(f"Has 'specialization': {'specialization' in doctor}")
        print(f"Specialization value: {doctor.get('specialization', 'NOT FOUND')}")
    
    # Get appointments
    response = client.get('/api/admin/appointments',
        headers={'Authorization': f'Bearer {token}'})
    
    data = json.loads(response.data)
    if data['success'] and len(data['data']['appointments']) > 0:
        apt = data['data']['appointments'][0]
        print('\n=== APPOINTMENT DATA ===')
        print(json.dumps(apt, indent=2))
        if apt.get('doctor'):
            print('\n=== DOCTOR IN APPOINTMENT ===')
            print(f"Has 'department': {'department' in apt['doctor']}")
            print(f"Department value: {apt['doctor'].get('department', 'NOT FOUND')}")
            print(f"Has 'specialization': {'specialization' in apt['doctor']}")
            print(f"Specialization value: {apt['doctor'].get('specialization', 'NOT FOUND')}")
