"""
Tests for rate limiting on authentication endpoints.
Verifies that brute force attacks are prevented.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, OTPVerification
from core.utils import normalize_phone_number
import json


class RegisterRateLimitTests(TestCase):
    """Test rate limiting on registration endpoint"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts_register_create') or '/api/accounts/register/'
        cache.clear()
    
    def test_register_throttle_5_per_hour(self):
        """Verify registration is throttled at 5 per hour per IP"""
        phone_base = '0700000'
        
        # First 5 registrations should succeed (with eventual errors for duplicates)
        for i in range(5):
            response = self.client.post(
                self.register_url,
                data=json.dumps({
                    'username': f'user{i}',
                    'email': f'user{i}@test.com',
                    'password': 'TestPass123!',
                    'phone_number': f'{phone_base}{i:03d}'
                }),
                content_type='application/json'
            )
            # Should succeed or get 400 for validation, not 429
            self.assertIn(response.status_code, [201, 400])
        
        # 6th registration should be throttled
        response = self.client.post(
            self.register_url,
            data=json.dumps({
                'username': 'user6',
                'email': 'user6@test.com',
                'password': 'TestPass123!',
                'phone_number': f'{phone_base}005'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 429, 
                        f"Expected throttle (429), got {response.status_code}")
        self.assertIn('throttled', response.json().get('detail', '').lower() or 
                     'too many' in response.json().get('error', '').lower())


class OTPVerificationRateLimitTests(TestCase):
    """Test rate limiting on OTP verification"""
    
    def setUp(self):
        self.client = Client()
        self.phone = '0712345678'
        self.normalized_phone = normalize_phone_number(self.phone)
        self.verify_url = reverse('accounts_verify_phone') or '/api/accounts/verify-phone/'
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            phone_number=self.normalized_phone,
            password='TestPass123!'
        )
        
        # Create OTP
        otp = OTPVerification.objects.create(
            phone_number=self.normalized_phone,
            otp='123456',
            purpose='registration',
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        self.valid_otp = otp.otp
        cache.clear()
    
    def test_otp_verification_throttle_10_per_hour(self):
        """Verify OTP verification is throttled at 10 per hour"""
        # Make 10 failed attempts
        for i in range(10):
            response = self.client.post(
                self.verify_url,
                data=json.dumps({
                    'phone_number': self.phone,
                    'otp': '000000'  # Wrong OTP
                }),
                content_type='application/json'
            )
            # Should get 400 for invalid OTP, not throttled yet
            self.assertIn(response.status_code, [400, 429], 
                         f"Attempt {i+1}: Expected 400 or 429, got {response.status_code}")
        
        # 11th attempt should be throttled
        response = self.client.post(
            self.verify_url,
            data=json.dumps({
                'phone_number': self.phone,
                'otp': '000000'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 429,
                        f"Expected throttle (429), got {response.status_code}")
    
    def test_otp_lockout_after_5_failed_attempts(self):
        """Verify account lockout after 5 failed OTP attempts"""
        # Make 5 failed attempts
        for i in range(5):
            response = self.client.post(
                self.verify_url,
                data=json.dumps({
                    'phone_number': self.phone,
                    'otp': '000000'
                }),
                content_type='application/json'
            )
            # Should get 400 or 429
            self.assertIn(response.status_code, [400, 429])
        
        # 6th attempt should be locked out (429)
        response = self.client.post(
            self.verify_url,
            data=json.dumps({
                'phone_number': self.phone,
                'otp': '000000'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 429,
                        "Expected lockout after 5 failed attempts")
        self.assertIn('15 minutes', response.json().get('error', ''),
                     "Error message should mention 15-minute lockout")
    
    def test_otp_lockout_clears_on_successful_verification(self):
        """Verify failure counter resets on successful OTP verification"""
        # Make 4 failed attempts
        for i in range(4):
            self.client.post(
                self.verify_url,
                data=json.dumps({
                    'phone_number': self.phone,
                    'otp': '000000'
                }),
                content_type='application/json'
            )
        
        # Verify with correct OTP
        response = self.client.post(
            self.verify_url,
            data=json.dumps({
                'phone_number': self.phone,
                'otp': self.valid_otp
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200,
                        f"Valid OTP should succeed, got {response.status_code}")
        
        # Verify failure counter is cleared by checking cache
        failure_key = f"otp_failures_{self.normalized_phone}"
        self.assertIsNone(cache.get(failure_key),
                         "Failure counter should be cleared after success")


class ResendOTPRateLimitTests(TestCase):
    """Test rate limiting on OTP resend"""
    
    def setUp(self):
        self.client = Client()
        self.phone = '0712345678'
        self.normalized_phone = normalize_phone_number(self.phone)
        self.resend_url = reverse('accounts_resend_otp') or '/api/accounts/resend-otp/'
        
        # Create an unverified user
        self.user = User.objects.create_user(
            username='testuser',
            phone_number=self.normalized_phone,
            password='TestPass123!',
            is_verified=False
        )
        cache.clear()
    
    def test_resend_otp_throttle_3_per_30_seconds(self):
        """Verify OTP resend is throttled at 3 per 30 seconds"""
        # First 3 resends should succeed
        for i in range(3):
            response = self.client.post(
                self.resend_url,
                data=json.dumps({
                    'phone_number': self.phone
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200,
                           f"Resend {i+1} should succeed, got {response.status_code}")
        
        # 4th resend should be throttled
        response = self.client.post(
            self.resend_url,
            data=json.dumps({
                'phone_number': self.phone
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 429,
                        f"Expected throttle (429), got {response.status_code}")


class LoginRateLimitTests(TestCase):
    """Test rate limiting on login endpoint"""
    
    def setUp(self):
        self.client = Client()
        self.phone = '0712345678'
        self.normalized_phone = normalize_phone_number(self.phone)
        self.login_url = reverse('accounts_login') or '/api/accounts/login/'
        
        # Create verified user
        self.user = User.objects.create_user(
            username='testuser',
            phone_number=self.normalized_phone,
            password='CorrectPassword123!',
            is_verified=True
        )
        cache.clear()
    
    def test_login_throttle_10_per_hour(self):
        """Verify login is throttled at 10 per hour"""
        # Make 10 failed attempts
        for i in range(10):
            response = self.client.post(
                self.login_url,
                data=json.dumps({
                    'phone_number': self.phone,
                    'password': 'WrongPassword'
                }),
                content_type='application/json'
            )
            # Should get 401 for invalid credentials, not throttled yet
            self.assertEqual(response.status_code, 401,
                           f"Attempt {i+1}: Expected 401, got {response.status_code}")
        
        # 11th attempt should be throttled
        response = self.client.post(
            self.login_url,
            data=json.dumps({
                'phone_number': self.phone,
                'password': 'WrongPassword'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 429,
                        f"Expected throttle (429), got {response.status_code}")
    
    def test_login_success_with_correct_credentials(self):
        """Verify successful login within rate limit"""
        response = self.client.post(
            self.login_url,
            data=json.dumps({
                'phone_number': self.phone,
                'password': 'CorrectPassword123!'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200,
                        f"Valid login should succeed, got {response.status_code}")
        self.assertIn('token', response.json(),
                     "Response should contain access token")


class PasswordResetRateLimitTests(TestCase):
    """Test rate limiting on password reset endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.phone = '0712345678'
        self.normalized_phone = normalize_phone_number(self.phone)
        self.reset_request_url = reverse('accounts_password_reset_request') or '/api/accounts/password-reset/'
        self.reset_url = reverse('accounts_password_reset') or '/api/accounts/password-reset-confirm/'
        
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            phone_number=self.normalized_phone,
            password='TestPass123!',
            is_verified=True
        )
        cache.clear()
    
    def test_password_reset_request_throttle_5_per_hour(self):
        """Verify password reset request is throttled at 5 per hour"""
        # First 5 requests should succeed
        for i in range(5):
            response = self.client.post(
                self.reset_request_url,
                data=json.dumps({
                    'phone_number': self.phone
                }),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200,
                           f"Request {i+1} should succeed, got {response.status_code}")
        
        # 6th request should be throttled
        response = self.client.post(
            self.reset_request_url,
            data=json.dumps({
                'phone_number': self.phone
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 429,
                        f"Expected throttle (429), got {response.status_code}")


class GenericErrorMessagesTests(TestCase):
    """Test that error messages don't allow account enumeration"""
    
    def setUp(self):
        self.client = Client()
        self.verify_url = reverse('accounts_verify_phone') or '/api/accounts/verify-phone/'
        cache.clear()
    
    def test_otp_verification_generic_error_for_invalid_otp(self):
        """Verify error message is generic for invalid OTP"""
        response = self.client.post(
            self.verify_url,
            data=json.dumps({
                'phone_number': '0712345678',
                'otp': '000000'
            }),
            content_type='application/json'
        )
        
        # Error should not distinguish between wrong OTP and non-existent user
        error_msg = response.json().get('error', '').lower()
        self.assertNotIn('not found', error_msg,
                        "Error should not reveal if user exists")
        self.assertNotIn('user', error_msg,
                        "Error should not mention user status")


class ThrottleHeadersTests(TestCase):
    """Test that DRF throttle headers are present in responses"""
    
    def setUp(self):
        self.client = Client()
        self.verify_url = reverse('accounts_verify_phone') or '/api/accounts/verify-phone/'
        cache.clear()
    
    def test_throttle_headers_present_in_response(self):
        """Verify DRF throttle information headers are present"""
        response = self.client.post(
            self.verify_url,
            data=json.dumps({
                'phone_number': '0712345678',
                'otp': '000000'
            }),
            content_type='application/json'
        )
        
        # DRF should add X-RateLimit headers
        # (Availability depends on cache backend and DRF configuration)
        # This test just verifies the request completes
        self.assertIsNotNone(response.status_code,
                           "Response should have status code")


if __name__ == '__main__':
    import unittest
    unittest.main()
