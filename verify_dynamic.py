import sys
import os
import json
import requests
from app import app

def test_dynamic_features():
    print("Starting Dynamic Features Verification...")
    client = app.test_client()
    
    # 1. Test Organization Add
    print("\n[Test] Add Organization")
    res = client.post('/organizations/add', json={
        "name": "TestRedCross", "contact": "119"
    })
    if res.status_code == 201:
        print("[PASS] Organization added")
    else:
        print(f"[FAIL] Add Org: {res.status_code} - {res.get_data(as_text=True)}")

    # 2. Test Resource Add
    print("\n[Test] Add Resource")
    res = client.post('/resources/add', json={
        "name": "SuperPills", "type": "MedicalResource", "quantity": 500
    })
    if res.status_code == 201:
        print("[PASS] Resource added")
    else:
        print(f"[FAIL] Add Resource: {res.status_code} - {res.get_data(as_text=True)}")

    # 3. Test Location Add (Dynamic)
    print("\n[Test] Add Location (New Province)")
    res = client.post('/locations/add', json={
        "name": "MetaProvince", "type": "Province"
    })
    if res.status_code == 201:
        print("[PASS] Province added")
    else:
        print(f"[FAIL] Add Province: {res.status_code} - {res.get_data(as_text=True)}")

    # 4. Test Volunteer Add
    print("\n[Test] Add Volunteer")
    res = client.post('/volunteers/add', json={
        "name": "Jane Doe", "contact": "999", "skill_level": "Medical"
    })
    if res.status_code == 201:
        print("[PASS] Volunteer added")
    else:
        print(f"[FAIL] Add Volunteer: {res.status_code} - {res.get_data(as_text=True)}")

    # 5. Test Disaster with Dynamic Type
    print("\n[Test] Add Disaster (New Type)")
    res = client.post('/disasters/add', json={
        "name": "KaijuAttack2026",
        "type": "KaijuAttack",
        "severity": "High",
        "create_new_type": True,
        "location": "Colombo" # Assuming Colombo exists
    })
    if res.status_code == 201:
        print("[PASS] Dynamic Type Disaster added")
    else:
        print(f"[FAIL] Add Dynamic Disaster: {res.status_code} - {res.get_data(as_text=True)}")

if __name__ == "__main__":
    test_dynamic_features()
