#!/usr/bin/env python3
"""
Test script for FagiErrands authentication endpoints.
Tests phone verification enforcement, login security, and session management.

Usage:
    python3 test_auth_endpoints.py
"""

import requests
import json
import time
from datetime import datetime
import sys

BASE_URL = "https://fagierrands-dev-backend.onrender.com"

# Test user credentials
TEST_PHONE = "+254712345678"
TEST_PASSWORD = "TestPassword123!"
TEST_EMAIL = "test@example.com"

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def log_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def log_error(msg):
    print(f"{RED}✗ {msg}{RESET}")


def log_info(msg):
    print(f"{BLUE}ℹ {msg}{RESET}")


def log_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")


def test_register():
    """Test user registration"""
    print("\n" + "="*60)
    print("TEST 1: User Registration")
    print("="*60)
    
    url = f"{BASE_URL}/api/accounts/register/"
    
    data = {
        "username": "testuser123",
        "phone_number": TEST_PHONE,
        "password": TEST_PASSWORD,
        "password2": TEST_PASSWORD,
        "first_name": "Test",
        "last_name": "User",
        "email": TEST_EMAIL
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            log_success("Registration successful")
            return True
        else:
            log_error(f"Registration failed: {response.json()}")
            return False
    except Exception as e:
        log_error(f"Registration error: {str(e)}")
        return False


def test_access_profile_unverified(token):
    """Test accessing profile without phone verification - should fail"""
    print("\n" + "="*60)
    print("TEST 2: Access Profile Without Verification (Should FAIL)")
    print("="*60)
    
    url = f"{BASE_URL}/api/accounts/profile/"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 403:
            log_success("Correctly blocked unverified user from profile access")
            return True
        else:
            log_error(f"Should have returned 403, got {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False


def test_access_user_detail_unverified(token):
    """Test accessing user detail without verification - should fail"""
    print("\n" + "="*60)
    print("TEST 3: Access User Detail Without Verification (Should FAIL)")
    print("="*60)
    
    url = f"{BASE_URL}/api/accounts/user/"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 403:
            log_success("Correctly blocked unverified user from user detail access")
            return True
        elif response.status_code == 200:
            log_warning("User detail endpoint allows unverified users - may need fixing")
            return False
        else:
            print(f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False


def test_resend_otp():
    """Test resend OTP endpoint"""
    print("\n" + "="*60)
    print("TEST 4: Resend OTP")
    print("="*60)
    
    url = f"{BASE_URL}/api/accounts/resend-otp/"
    
    data = {"phone_number": TEST_PHONE}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Should return 200 with generic message (don't reveal if phone exists)
        if response.status_code == 200:
            log_success("Resend OTP returned generic message")
            return True
        else:
            log_warning(f"Resend OTP returned {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False


def test_verify_phone_wrong_otp():
    """Test verify phone with wrong OTP - should fail"""
    print("\n" + "="*60)
    print("TEST 5: Verify Phone with Wrong OTP (Should FAIL)")
    print("="*60)
    
    url = f"{BASE_URL}/api/accounts/verify-phone/"
    
    data = {
        "phone_number": TEST_PHONE,
        "otp": "0000"  # Wrong OTP
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            log_success("Correctly rejected wrong OTP")
            return True
        else:
            log_error(f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False


def test_login_wrong_password():
    """Test login with wrong password - should fail"""
    print("\n" + "="*60)
    print("TEST 6: Login with Wrong Password (Should FAIL)")
    print("="*60)
    
    url = f"{BASE_URL}/api/accounts/login/"
    
    data = {
        "phone_number": TEST_PHONE,
        "password": "WrongPassword123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            log_success("Correctly rejected wrong password")
            return True
        else:
            log_error(f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False


def test_login_unverified_user():
    """Test login with unverified user - should fail"""
    print("\n" + "="*60)
    print("TEST 7: Login Unverified User (Should FAIL)")
    print("="*60)
    
    url = f"{BASE_URL}/api/accounts/login/"
    
    data = {
        "phone_number": TEST_PHONE,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            if "verified" in response.json().get("error", "").lower():
                log_success("Correctly rejected unverified user login")
                return True
        
        log_error(f"Expected 400 with verification error")
        return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False


def test_token_refresh():
    """Test token refresh endpoint"""
    print("\n" + "="*60)
    print("TEST 8: Token Refresh")
    print("="*60)
    
    # First need to get a valid token
    url = f"{BASE_URL}/api/accounts/token/"
    
    data = {
        "phone_number": TEST_PHONE,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            log_warning("Could not get initial token (user may not be verified)")
            return False
        
        token_data = response.json()
        refresh_token = token_data.get("refresh")
        
        # Now test refresh
        refresh_url = f"{BASE_URL}/api/accounts/token/refresh/"
        refresh_data = {"refresh": refresh_token}
        
        refresh_response = requests.post(refresh_url, json=refresh_data)
        print(f"Refresh Status: {refresh_response.status_code}")
        print(f"Response: {json.dumps(refresh_response.json(), indent=2)}")
        
        if refresh_response.status_code == 200:
            log_success("Token refresh successful")
            return True
        else:
            log_error(f"Token refresh failed")
            return False
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False


def test_failed_login_attempts():
    """Test failed login attempt tracking"""
    print("\n" + "="*60)
    print("TEST 9: Failed Login Attempt Tracking")
    print("="*60)
    
    url = f"{BASE_URL}/api/accounts/login/"
    
    failed_attempts = 0
    locked_out = False
    
    for i in range(7):
        data = {
            "phone_number": TEST_PHONE,
            "password": f"WrongPassword{i}"
        }
        
        try:
            response = requests.post(url, json=data)
            status = response.status_code
            
            if status == 429:
                locked_out = True
                log_warning(f"Attempt {i+1}: Account locked (429)")
                break
            elif status == 401:
                failed_attempts += 1
                error_msg = response.json().get("error", "")
                log_warning(f"Attempt {i+1}: Failed login - {error_msg}")
            else:
                log_info(f"Attempt {i+1}: Status {status}")
        except Exception as e:
            log_error(f"Error on attempt {i+1}: {str(e)}")
    
    if locked_out:
        log_success("Account lockout working correctly")
        return True
    else:
        log_warning("Expected account lockout after failed attempts")
        return False


def test_generic_error_messages():
    """Test that error messages are generic (no user enumeration)"""
    print("\n" + "="*60)
    print("TEST 10: Generic Error Messages (No Enumeration)")
    print("="*60)
    
    # Test with non-existent phone
    url = f"{BASE_URL}/api/accounts/verify-phone/"
    
    data = {
        "phone_number": "+999999999999",  # Non-existent
        "otp": "0000"
    }
    
    try:
        response = requests.post(url, json=data)
        error_msg = response.json().get("error", "")
        
        print(f"Response for non-existent phone: {error_msg}")
        
        # Should not contain "not found" or other revealing messages
        if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
            log_error("Error message reveals user does not exist - enumeration vulnerability!")
            return False
        else:
            log_success("Generic error message (no user enumeration)")
            return True
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}FagiErrands Auth Endpoints Test Suite{RESET}")
    print(f"{BLUE}Target: {BASE_URL}{RESET}")
    print(f"{BLUE}Time: {datetime.now().isoformat()}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = {}
    
    # Run tests
    results["Registration"] = test_register()
    
    # Try to get unverified token for testing
    try:
        url = f"{BASE_URL}/api/accounts/token/"
        data = {"phone_number": TEST_PHONE, "password": TEST_PASSWORD}
        response = requests.post(url, json=data)
        if response.status_code == 200:
            token = response.json().get("access")
            results["Profile Access (Unverified)"] = test_access_profile_unverified(token)
            results["User Detail (Unverified)"] = test_access_user_detail_unverified(token)
        else:
            log_warning("Could not get token for unverified tests (user may already be verified)")
    except Exception as e:
        log_warning(f"Skipped unverified tests: {str(e)}")
    
    results["Resend OTP"] = test_resend_otp()
    results["Wrong OTP"] = test_verify_phone_wrong_otp()
    results["Wrong Password"] = test_login_wrong_password()
    results["Unverified Login"] = test_login_unverified_user()
    results["Token Refresh"] = test_token_refresh()
    results["Failed Login Tracking"] = test_failed_login_attempts()
    results["Generic Error Messages"] = test_generic_error_messages()
    
    # Print summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{status} - {test_name}")
    
    print(f"\n{BLUE}Results: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        log_success(f"All {total} tests passed!")
        return 0
    else:
        log_error(f"{total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
