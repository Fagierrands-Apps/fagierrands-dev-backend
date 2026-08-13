"""
API Rate Limiting / Throttles for FagiErrands

Rates are configured in settings.py under DEFAULT_THROTTLE_RATES
and can be overridden via environment variables.
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class RegisterThrottle(AnonRateThrottle):
    """Rate limit registration attempts"""
    scope = 'register'


class OTPVerificationThrottle(AnonRateThrottle):
    """Rate limit OTP verification attempts"""
    scope = 'otp_verification'


class ResendOTPThrottle(AnonRateThrottle):
    """Rate limit OTP resend attempts"""
    scope = 'resend_otp'


class PasswordResetThrottle(AnonRateThrottle):
    """Rate limit password reset attempts"""
    scope = 'password_reset'


class LoginThrottle(AnonRateThrottle):
    """Rate limit login attempts"""
    scope = 'login'


class TokenRefreshThrottle(UserRateThrottle):
    """Rate limit token refresh attempts"""
    scope = 'token_refresh'
