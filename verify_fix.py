import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app import app
import json

def test_api():
    print("Starting API Verification...")
    client = app.test_client()
    
    # Test 1: Check /disasters/type/Flood
    print("\nTest 1: Check /disasters/type/Flood")
    response = client.get('/disasters/type/Flood')
    if response.status_code == 200:
        data = response.get_json()
        print(f"Received {len(data)} items")
        if len(data) > 0:
            item = data[0]
            required_keys = ['location_name', 'date', 'resources', 'type', 'affected_count']
            missing = [key for key in required_keys if key not in item]
            if not missing:
                print("[PASS]: All keys present in Type endpoint")
            else:
                print(f"[FAIL]: Missing keys in Type endpoint: {missing}")
        else:
            print("[WARN]: No floods found to test structure")
    else:
        print(f"[FAIL]: API Error {response.status_code}")

    # Test 2: Check /disasters/severity/High
    print("\nTest 2: Check /disasters/severity/High")
    response = client.get('/disasters/severity/High')
    if response.status_code == 200:
        data = response.get_json()
        print(f"Received {len(data)} items")
        if len(data) > 0:
            item = data[0]
            required_keys = ['location_name', 'date', 'resources', 'type', 'affected_count']
            missing = [key for key in required_keys if key not in item]
            if not missing:
                print("[PASS]: All keys present in Severity endpoint")
            else:
                print(f"[FAIL]: Missing keys in Severity endpoint: {missing}")
        else:
            print("⚠️ WARNING: No high severity disasters found to test structure")
    else:
        print(f"❌ FAILED: API Error {response.status_code}")

if __name__ == "__main__":
    test_api()
