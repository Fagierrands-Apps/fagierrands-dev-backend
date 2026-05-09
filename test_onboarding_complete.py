#!/usr/bin/env python3
"""
Test all onboarding endpoints for Fagi Errands Backend
"""
import requests
import json
import time

BASE_URL = "https://fagierrands-dev-backend.onrender.com"
TEST_PHONE = "+254712345678"  # Change this to your test phone
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPass123!"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")

def test_register():
    """Test user registration"""
    print("\n🔵 TEST 1: REGISTER USER")
    url = f"{BASE_URL}/api/accounts/register/"
    data = {
        "phone_number": TEST_PHONE,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "password2": TEST_PASSWORD,
        "first_name": "Test",
        "last_name": "User",
        "user_type": "client"
    }
    
    response = requests.post(url, json=data)
    print_response("REGISTER RESPONSE", response)
    
    if response.status_code == 201:
        print("✅ Registration successful!")
        return True
    else:
        print("❌ Registration failed!")
        return False

def test_resend_otp():
    """Test resend OTP"""
    print("\n🔵 TEST 2: RESEND OTP")
    url = f"{BASE_URL}/api/accounts/resend-otp/"
    data = {
        "phone_number": TEST_PHONE
    }
    
    response = requests.post(url, json=data)
    print_response("RESEND OTP RESPONSE", response)
    
    if response.status_code == 200:
        print("✅ OTP resent successfully!")
        return True
    else:
        print("❌ Resend OTP failed!")
        return False

def test_verify_phone(otp_code):
    """Test phone verification"""
    print("\n🔵 TEST 3: VERIFY PHONE")
    url = f"{BASE_URL}/api/accounts/verify-phone/"
    data = {
        "phone_number": TEST_PHONE,
        "otp": otp_code
    }
    
    response = requests.post(url, json=data)
    print_response("VERIFY PHONE RESPONSE", response)
    
    if response.status_code == 200:
        print("✅ Phone verified successfully!")
        return response.json()
    else:
        print("❌ Phone verification failed!")
        return None

def test_login():
    """Test user login"""
    print("\n🔵 TEST 4: LOGIN")
    url = f"{BASE_URL}/api/accounts/login/"
    data = {
        "phone_number": TEST_PHONE,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(url, json=data)
    print_response("LOGIN RESPONSE", response)
    
    if response.status_code == 200:
        print("✅ Login successful!")
        return response.json()
    else:
        print("❌ Login failed!")
        return None

def test_forgot_password():
    """Test forgot password (request OTP)"""
    print("\n🔵 TEST 5: FORGOT PASSWORD (Request OTP)")
    url = f"{BASE_URL}/api/accounts/forgot-password/"
    data = {
        "phone_number": TEST_PHONE
    }
    
    response = requests.post(url, json=data)
    print_response("FORGOT PASSWORD RESPONSE", response)
    
    if response.status_code == 200:
        print("✅ Password reset OTP sent!")
        return True
    else:
        print("❌ Forgot password failed!")
        return False

def test_reset_password(otp_code):
    """Test password reset"""
    print("\n🔵 TEST 6: RESET PASSWORD")
    url = f"{BASE_URL}/api/accounts/reset-password/"
    new_password = "NewPass123!"
    data = {
        "phone_number": TEST_PHONE,
        "otp": otp_code,
        "new_password": new_password,
        "confirm_password": new_password
    }
    
    response = requests.post(url, json=data)
    print_response("RESET PASSWORD RESPONSE", response)
    
    if response.status_code == 200:
        print("✅ Password reset successful!")
        return True
    else:
        print("❌ Password reset failed!")
        return False

def check_textpie_config():
    """Check TextPie SMS configuration"""
    print("\n🔵 CHECKING TEXTPIE CONFIGURATION")
    print("="*60)
    print("Please verify these environment variables are set on Render:")
    print("1. TEXTPIE_API_KEY")
    print("2. TEXTPIE_SENDER_ID (should be 'FagiErrands')")
    print("="*60)

def main():
    print("\n" + "="*60)
    print("FAGI ERRANDS ONBOARDING TESTS")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Phone: {TEST_PHONE}")
    print(f"Test Email: {TEST_EMAIL}")
    print("="*60)
    
    # Check configuration
    check_textpie_config()
    
    # Test 1: Register
    if not test_register():
        print("\n⚠️  Registration failed. User might already exist.")
        print("Continuing with other tests...")
    
    time.sleep(2)
    
    # Test 2: Resend OTP
    test_resend_otp()
    
    print("\n" + "="*60)
    print("⏸️  PAUSED - CHECK YOUR PHONE FOR OTP")
    print("="*60)
    otp = input("Enter the OTP code you received: ").strip()
    
    # Test 3: Verify Phone
    verify_result = test_verify_phone(otp)
    
    if verify_result:
        time.sleep(2)
        
        # Test 4: Login
        login_result = test_login()
        
        if login_result:
            time.sleep(2)
            
            # Test 5: Forgot Password
            test_forgot_password()
            
            print("\n" + "="*60)
            print("⏸️  PAUSED - CHECK YOUR PHONE FOR PASSWORD RESET OTP")
            print("="*60)
            reset_otp = input("Enter the password reset OTP: ").strip()
            
            # Test 6: Reset Password
            test_reset_password(reset_otp)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)
    print("\nIf you didn't receive SMS:")
    print("1. Check Render environment variables (TEXTPIE_API_KEY, TEXTPIE_SENDER_ID)")
    print("2. Check Render logs for SMS sending errors")
    print("3. Verify TextPie account has credits")
    print("4. Verify 'FagiErrands' sender ID is approved")
    print("="*60)

if __name__ == "__main__":
    main()
