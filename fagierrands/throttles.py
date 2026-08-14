"""
API Rate Limiting / Throttles for FagiErrands

Rates are configured in settings.py under DEFAULT_THROTTLE_RATES
and can be overridden via environment variables.

NOTE: We use ScopedRateThrottle (not AnonRateThrottle) so each endpoint
gets its own independent counter keyed on scope + IP. AnonRateThrottle
ignores the scope name and always reads from DEFAULT_THROTTLE_RATES['anon'].
"""

from rest_framework.throttling import ScopedRateThrottle


class RegisterThrottle(ScopedRateThrottle):
    """Rate limit registration attempts — scope: 'register'"""
    scope = 'register'


class OTPVerificationThrottle(ScopedRateThrottle):
    """Rate limit OTP verification attempts — scope: 'otp_verification'"""
    scope = 'otp_verification'


class ResendOTPThrottle(ScopedRateThrottle):
    """Rate limit OTP resend attempts — scope: 'resend_otp'"""
    scope = 'resend_otp'


class PasswordResetThrottle(ScopedRateThrottle):
    """Rate limit password reset attempts — scope: 'password_reset'"""
    scope = 'password_reset'


class LoginThrottle(ScopedRateThrottle):
    """Rate limit login attempts — scope: 'login'"""
    scope = 'login'


class TokenRefreshThrottle(ScopedRateThrottle):
    """Rate limit token refresh attempts — scope: 'token_refresh'"""
    scope = 'token_refresh'
