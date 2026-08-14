"""
API Rate Limiting / Throttles for FagiErrands

Rates are configured in settings.py under DEFAULT_THROTTLE_RATES
and can be overridden via environment variables.

NOTE: We use ScopedRateThrottle with a custom get_ident() that reads
the real client IP from X-Forwarded-For, since the server sits behind
Cloudflare and Render's load balancer. Without this, REMOTE_ADDR is
always the proxy IP and all users share one throttle bucket.
"""

from rest_framework.throttling import ScopedRateThrottle


class _RealIPThrottle(ScopedRateThrottle):
    """
    ScopedRateThrottle that extracts the real client IP from
    X-Forwarded-For when the server is behind a reverse proxy/CDN.
    Takes the leftmost (client-supplied) IP to avoid trusting the chain.
    """

    def get_ident(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            # XFF is a comma-separated list: client, proxy1, proxy2, ...
            # Take the leftmost entry (the original client IP)
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class RegisterThrottle(_RealIPThrottle):
    """Rate limit registration attempts — scope: 'register' (10/day)"""
    scope = 'register'


class OTPVerificationThrottle(_RealIPThrottle):
    """Rate limit OTP verification attempts — scope: 'otp_verification' (10/hour)"""
    scope = 'otp_verification'


class ResendOTPThrottle(_RealIPThrottle):
    """Rate limit OTP resend attempts — scope: 'resend_otp' (6/hour)"""
    scope = 'resend_otp'


class PasswordResetThrottle(_RealIPThrottle):
    """Rate limit password reset attempts — scope: 'password_reset' (3/hour)"""
    scope = 'password_reset'


class LoginThrottle(_RealIPThrottle):
    """Rate limit login attempts — scope: 'login' (20/hour)"""
    scope = 'login'


class TokenRefreshThrottle(_RealIPThrottle):
    """Rate limit token refresh attempts — scope: 'token_refresh' (20/hour)"""
    scope = 'token_refresh'
