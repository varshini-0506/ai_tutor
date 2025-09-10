#!/usr/bin/env python3
"""
Simple CORS test script to verify backend CORS configuration
"""

import requests
import json

def test_cors():
    """Test CORS configuration with the deployed backend"""
    
    base_url = "https://ai-tutor-backend-m4rr.onrender.com"
    
    # Test 1: Simple GET request
    print("Testing simple GET request...")
    try:
        response = requests.get(f"{base_url}/api/test-cors")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        print("✅ GET request successful")
    except Exception as e:
        print(f"❌ GET request failed: {e}")
    
    # Test 2: OPTIONS preflight request
    print("\nTesting OPTIONS preflight request...")
    try:
        response = requests.options(f"{base_url}/api/test-cors")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print("✅ OPTIONS request successful")
    except Exception as e:
        print(f"❌ OPTIONS request failed: {e}")
    
    # Test 3: POST request with headers
    print("\nTesting POST request with headers...")
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': 'https://test-frontend.onrender.com'
        }
        data = {"test": "data"}
        response = requests.post(f"{base_url}/api/test-cors", 
                               headers=headers, 
                               json=data)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        print("✅ POST request successful")
    except Exception as e:
        print(f"❌ POST request failed: {e}")

if __name__ == "__main__":
    test_cors()
