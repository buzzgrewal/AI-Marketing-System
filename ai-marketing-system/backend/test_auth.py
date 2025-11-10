#!/usr/bin/env python3
"""Test script to verify authentication is working"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration"""
    print("Testing registration...")

    # Create test user data
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "password123"
    }

    # Send registration request
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=user_data
    )

    if response.status_code == 201:
        print("✅ Registration successful!")
        print(f"Response: {response.json()}")
        return True
    elif response.status_code == 400:
        print("⚠️ User already exists (this is okay if testing multiple times)")
        return True
    else:
        print(f"❌ Registration failed!")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_login():
    """Test user login"""
    print("\nTesting login...")

    # Login with test credentials
    login_data = {
        "username": "testuser",
        "password": "password123"
    }

    # Send as form data (OAuth2PasswordRequestForm expects form data)
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data=login_data
    )

    if response.status_code == 200:
        print("✅ Login successful!")
        token_data = response.json()
        print(f"Access token received: {token_data['access_token'][:20]}...")
        return token_data['access_token']
    else:
        print(f"❌ Login failed!")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    print("\nTesting protected endpoint...")

    # Try to access current user endpoint
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )

    if response.status_code == 200:
        print("✅ Protected endpoint access successful!")
        print(f"User data: {response.json()}")
        return True
    else:
        print(f"❌ Protected endpoint access failed!")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Authentication System Test")
    print("=" * 50)

    # Test registration
    if not test_registration():
        print("\n⚠️ Registration test failed, but continuing...")

    # Test login
    token = test_login()
    if not token:
        print("\n❌ Login failed - cannot continue with protected endpoint test")
        sys.exit(1)

    # Test protected endpoint
    if not test_protected_endpoint(token):
        print("\n❌ Protected endpoint test failed")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("✅ All tests passed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()