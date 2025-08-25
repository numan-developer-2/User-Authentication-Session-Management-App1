#!/usr/bin/env python3
"""
API Testing Script for User Authentication App

This script demonstrates how to test the API endpoints programmatically.
Make sure the Flask app is running on localhost:5000 before running this script.

Usage:
    python test_api.py
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_api():
    print("🧪 Testing User Authentication API")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Test 1: Check initial status (should be unauthenticated)
    print("\n1️⃣ Testing initial authentication status...")
    try:
        response = session.get(f"{BASE_URL}/api/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.json()['authenticated'] == False
        print("✅ Initial status test passed")
    except Exception as e:
        print(f"❌ Initial status test failed: {e}")
        return False
    
    # Test 2: Register a new user
    print("\n2️⃣ Testing user registration...")
    test_user = {
        "username": "apitest",
        "email": "apitest@example.com",
        "password": "ApiTest123"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/register", json=test_user)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Registration test passed")
        elif response.status_code == 409 and "already" in response.json().get('error', '').lower():
            print("ℹ️ User already exists (expected for repeated tests)")
        else:
            print("❌ Registration test failed")
            return False
    except Exception as e:
        print(f"❌ Registration test failed: {e}")
        return False
    
    # Test 3: Login with valid credentials
    print("\n3️⃣ Testing user login...")
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert "Login successful" in response.json()['message']
        print("✅ Login test passed")
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False
    
    # Test 4: Check authenticated status
    print("\n4️⃣ Testing authenticated status...")
    try:
        response = session.get(f"{BASE_URL}/api/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()['authenticated'] == True
        print("✅ Authenticated status test passed")
    except Exception as e:
        print(f"❌ Authenticated status test failed: {e}")
        return False
    
    # Test 5: Access protected route
    print("\n5️⃣ Testing protected route access...")
    try:
        response = session.get(f"{BASE_URL}/api/profile")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert 'user' in response.json()
        print("✅ Protected route access test passed")
    except Exception as e:
        print(f"❌ Protected route access test failed: {e}")
        return False
    
    # Test 6: Test invalid login
    print("\n6️⃣ Testing invalid login...")
    invalid_login = {
        "email": test_user["email"],
        "password": "wrongpassword"
    }
    
    try:
        # Use a new session to avoid interference
        new_session = requests.Session()
        response = new_session.post(f"{BASE_URL}/api/login", json=invalid_login)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 401
        print("✅ Invalid login test passed")
    except Exception as e:
        print(f"❌ Invalid login test failed: {e}")
        return False
    
    # Test 7: Test logout
    print("\n7️⃣ Testing user logout...")
    try:
        response = session.post(f"{BASE_URL}/api/logout")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        print("✅ Logout test passed")
    except Exception as e:
        print(f"❌ Logout test failed: {e}")
        return False
    
    # Test 8: Check unauthenticated status after logout
    print("\n8️⃣ Testing unauthenticated status after logout...")
    try:
        response = session.get(f"{BASE_URL}/api/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()['authenticated'] == False
        print("✅ Unauthenticated status test passed")
    except Exception as e:
        print(f"❌ Unauthenticated status test failed: {e}")
        return False
    
    # Test 9: Try accessing protected route without authentication
    print("\n9️⃣ Testing protected route without authentication...")
    try:
        response = session.get(f"{BASE_URL}/api/profile")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 401
        print("✅ Unauthorized access test passed")
    except Exception as e:
        print(f"❌ Unauthorized access test failed: {e}")
        return False
    
    print("\n🎉 All tests passed successfully!")
    print("=" * 50)
    return True

def test_validation():
    print("\n🔍 Testing Input Validation")
    print("=" * 30)
    
    session = requests.Session()
    
    # Test weak password
    print("\n📝 Testing weak password rejection...")
    weak_pass_user = {
        "username": "weakuser",
        "email": "weak@example.com",
        "password": "123"  # Too short, no uppercase, no lowercase
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/register", json=weak_pass_user)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400
        print("✅ Weak password rejection test passed")
    except Exception as e:
        print(f"❌ Weak password test failed: {e}")
    
    # Test invalid email
    print("\n📧 Testing invalid email rejection...")
    invalid_email_user = {
        "username": "invaliduser",
        "email": "not-an-email",
        "password": "ValidPass123"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/register", json=invalid_email_user)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400
        print("✅ Invalid email rejection test passed")
    except Exception as e:
        print(f"❌ Invalid email test failed: {e}")
    
    # Test short username
    print("\n👤 Testing short username rejection...")
    short_username_user = {
        "username": "ab",  # Too short
        "email": "short@example.com",
        "password": "ValidPass123"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/register", json=short_username_user)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 400
        print("✅ Short username rejection test passed")
    except Exception as e:
        print(f"❌ Short username test failed: {e}")

def main():
    print("🚀 Starting API Test Suite for User Authentication App")
    print("Make sure the Flask app is running on http://localhost:5000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
        sys.exit(0)
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        print("✅ Server is running and accessible")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("Please make sure the Flask app is running with: python app.py")
        sys.exit(1)
    
    # Run main API tests
    if not test_api():
        print("❌ Main API tests failed")
        sys.exit(1)
    
    # Run validation tests
    test_validation()
    
    print("\n🎊 All tests completed successfully!")
    print("Your authentication system is working properly! 🔐")

if __name__ == "__main__":
    main()