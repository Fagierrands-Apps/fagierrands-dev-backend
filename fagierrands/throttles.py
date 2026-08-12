"""
API Rate Limiting / Throttles for FagiErrands
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class RegisterThrottle(AnonRateThrottle):
    """Rate limit registration attempts"""
    scope = 'register'
    rate = '10/day'


class OTPVerificationThrottle(AnonRateThrottle):
    """Rate limit OTP verification attempts"""
    scope = 'otp_verification'
    rate = '10/hour'


class ResendOTPThrottle(AnonRateThrottle):
    """Rate limit OTP resend attempts"""
    scope = 'resend_otp'
    rate = '3/30min'


class PasswordResetThrottle(AnonRateThrottle):
    """Rate limit password reset attempts"""
    scope = 'password_reset'
    rate = '3/hour'


class LoginThrottle(AnonRateThrottle):
    """Rate limit login attempts"""
    scope = 'login'
    rate = '20/hour'


class TokenRefreshThrottle(UserRateThrottle):
    """Rate limit token refresh attempts"""
    scope = 'token_refresh'
    rate = '20/hour'
