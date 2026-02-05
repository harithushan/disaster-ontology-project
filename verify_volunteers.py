import sys
import os
import json
from app import app

def test_volunteers():
    print("Starting Volunteers Verification...")
    client = app.test_client()
    
    # Test /volunteers endpoint
    print("\nTest: Check /volunteers")
    response = client.get('/volunteers')
    if response.status_code == 200:
        data = response.get_json()
        print(f"Received {len(data)} volunteers")
        if len(data) > 0:
            item = data[0]
            # UI expects: 'name', 'skill_level', 'assigned_shelter', 'contact'
            required_keys = ['name', 'skill_level', 'assigned_shelter', 'contact']
            missing = [key for key in required_keys if key not in item]
            if not missing:
                print("[PASS]: All required keys present in Volunteers endpoint")
            else:
                print(f"[FAIL]: Missing keys in Volunteers endpoint: {missing}")
        else:
            print("[WARN]: No volunteers found to test structure")
    else:
        print(f"[FAIL]: API Error {response.status_code}")

if __name__ == "__main__":
    test_volunteers()
