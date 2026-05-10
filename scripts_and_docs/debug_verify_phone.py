#!/usr/bin/env python3
"""
Debug script to check user OTP status
"""
import requests
import json

BASE_URL = "https://fagierrands-dev-backend.onrender.com"
PHONE = "+254712345678"  # Change to your test phone

def check_registration():
    """Try to register and see the response"""
    print("\n🔍 Testing Registration...")
    url = f"{BASE_URL}/api/accounts/register/"
    data = {
        "phone_number": PHONE,
        "email": "test@example.com",
        "password": "TestPass123!",
        "password2": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
        "user_type": "client"
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 201

def resend_otp():
    """Resend OTP"""
    print("\n🔍 Resending OTP...")
    url = f"{BASE_URL}/api/accounts/resend-otp/"
    data = {"phone_number": PHONE}
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_verify_with_wrong_otp():
    """Test with obviously wrong OTP to see error"""
    print("\n🔍 Testing with wrong OTP (0000)...")
    url = f"{BASE_URL}/api/accounts/verify-phone/"
    data = {
        "phone_number": PHONE,
        "otp": "0000"
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_verify_with_user_otp():
    """Test with user-provided OTP"""
    print("\n🔍 Testing with your OTP...")
    otp = input("Enter the OTP you received: ").strip()
    
    url = f"{BASE_URL}/api/accounts/verify-phone/"
    data = {
        "phone_number": PHONE,
        "otp": otp
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def main():
    print("="*60)
    print("FAGI ERRANDS - VERIFY PHONE DEBUG")
    print("="*60)
    print(f"Testing with phone: {PHONE}")
    print("="*60)
    
    # Step 1: Try registration
    registered = check_registration()
    
    if not registered:
        print("\n⚠️  User already exists or registration failed")
    
    # Step 2: Resend OTP
    resend_otp()
    
    # Step 3: Test with wrong OTP
    test_verify_with_wrong_otp()
    
    # Step 4: Test with correct OTP
    test_verify_with_user_otp()
    
    print("\n" + "="*60)
    print("DEBUG COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
