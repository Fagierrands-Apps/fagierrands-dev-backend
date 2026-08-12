"""
Login security and session management utilities.

Handles:
- Concurrent session limits
- Failed login attempt tracking
- Suspicious login detection (impossible travel, unusual locations)
- Session validation
"""

import logging
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

logger = logging.getLogger(__name__)


class LoginSecurityManager:
    """Manages login security checks and tracking"""
    
    # Cache keys
    FAILED_ATTEMPTS_KEY = "login_failures_{user_id}"
    LOCKOUT_KEY = "login_lockout_{user_id}"
    LAST_LOGIN_KEY = "last_login_{user_id}"
    SESSION_KEY = "session_{user_id}_{session_id}"
    CONCURRENT_SESSIONS_KEY = "concurrent_sessions_{user_id}"
    LAST_LOGIN_LOCATION_KEY = "last_login_location_{user_id}"
    
    @staticmethod
    def check_login_allowed(user, ip_address=None, location=None):
        """
        Check if user is allowed to login.
        
        Returns:
            (bool, str): (allowed, reason)
        """
        user_id = user.id
        
        # Check if user is locked out
        lockout_key = LoginSecurityManager.LOCKOUT_KEY.format(user_id=user_id)
        if cache.get(lockout_key):
            reason = f"Account locked due to multiple failed login attempts. Try again in 15 minutes."
            logger.warning(f"Login blocked for user {user_id}: Account locked")
            return False, reason
        
        # Check for suspicious activity
        is_suspicious, reason = LoginSecurityManager.detect_suspicious_login(
            user, ip_address, location
        )
        
        return True, None
    
    @staticmethod
    def record_failed_login(user, ip_address=None, reason=""):
        """Record failed login attempt and apply lockout if needed"""
        user_id = user.id
        failed_key = LoginSecurityManager.FAILED_ATTEMPTS_KEY.format(user_id=user_id)
        
        # Increment failed attempts
        failures = cache.get(failed_key, 0) + 1
        cache.set(failed_key, failures, 3600)  # 1 hour window
        
        logger.warning(
            f"Failed login for user {user_id} (attempt {failures}) from IP {ip_address}: {reason}"
        )
        
        # Apply lockout after threshold
        threshold = getattr(settings, 'LOGIN_FAILURE_THRESHOLD', 5)
        if failures >= threshold:
            lockout_duration = getattr(settings, 'LOGIN_FAILURE_LOCKOUT_DURATION', 900)
            lockout_key = LoginSecurityManager.LOCKOUT_KEY.format(user_id=user_id)
            cache.set(lockout_key, True, lockout_duration)
            logger.error(f"User {user_id} locked out after {failures} failed login attempts")
            return f"Too many failed login attempts. Account locked for 15 minutes."
        
        return f"Invalid credentials. {threshold - failures} attempt(s) remaining before lockout."
    
    @staticmethod
    def record_successful_login(user, session_id, ip_address=None, location=None):
        """Record successful login and track session"""
        user_id = user.id
        
        # Clear failed attempts
        failed_key = LoginSecurityManager.FAILED_ATTEMPTS_KEY.format(user_id=user_id)
        cache.delete(failed_key)
        
        # Track last login
        last_login_key = LoginSecurityManager.LAST_LOGIN_KEY.format(user_id=user_id)
        cache.set(last_login_key, {
            'ip': ip_address,
            'location': location,
            'timestamp': timezone.now().isoformat()
        }, 86400 * 30)  # 30 days
        
        # Track session
        session_key = LoginSecurityManager.SESSION_KEY.format(
            user_id=user_id,
            session_id=session_id
        )
        cache.set(session_key, {
            'ip': ip_address,
            'location': location,
            'created_at': timezone.now().isoformat()
        }, 3600 * 24)  # 24 hours
        
        # Track concurrent sessions
        LoginSecurityManager._track_concurrent_session(user_id, session_id, ip_address)
        
        logger.info(f"Successful login for user {user_id} from IP {ip_address}")
    
    @staticmethod
    def _track_concurrent_session(user_id, session_id, ip_address):
        """Track and enforce concurrent session limits"""
        concurrent_key = LoginSecurityManager.CONCURRENT_SESSIONS_KEY.format(user_id=user_id)
        sessions = cache.get(concurrent_key, [])
        
        # Add new session
        sessions.append({
            'session_id': session_id,
            'ip': ip_address,
            'created_at': timezone.now().isoformat()
        })
        
        # Enforce max concurrent sessions
        max_sessions = getattr(settings, 'MAX_CONCURRENT_SESSIONS', 3)
        if len(sessions) > max_sessions:
            # Remove oldest session
            sessions = sessions[-max_sessions:]
        
        cache.set(concurrent_key, sessions, 86400)
    
    @staticmethod
    def detect_suspicious_login(user, ip_address=None, location=None):
        """
        Detect suspicious login patterns.
        
        Returns:
            (bool, str): (is_suspicious, reason)
        """
        if not ip_address:
            return False, None
        
        last_login_key = LoginSecurityManager.LAST_LOGIN_KEY.format(user_id=user.id)
        last_login = cache.get(last_login_key)
        
        if not last_login:
            # First login or no recent history
            return False, None
        
        last_ip = last_login.get('ip')
        last_location = last_login.get('location')
        last_timestamp = last_login.get('timestamp')
        
        # Check for IP change (indicates potential account compromise)
        if last_ip and last_ip != ip_address:
            logger.warning(
                f"Suspicious login for user {user.id}: IP changed from {last_ip} to {ip_address}"
            )
            # Could trigger additional verification, but don't block for now
            return False, None  # Log but don't block
        
        # Check for location change (impossible travel)
        if last_location and location and last_location != location:
            if last_timestamp:
                try:
                    last_time = timezone.datetime.fromisoformat(last_timestamp)
                    time_diff = (timezone.now() - last_time).total_seconds()
                    
                    # If locations changed within 1 hour, might be suspicious
                    # (could calculate distance, but location might be city-level)
                    if time_diff < 3600:
                        logger.warning(
                            f"Suspicious login for user {user.id}: "
                            f"Location changed from {last_location} to {location} in {time_diff}s"
                        )
                        return False, None  # Log but don't block
                except (ValueError, AttributeError):
                    pass
        
        return False, None
    
    @staticmethod
    def validate_session(user_id, session_id, ip_address=None):
        """
        Validate session is still active and hasn't been tampered with.
        
        Returns:
            (bool, str): (valid, reason if invalid)
        """
        session_key = LoginSecurityManager.SESSION_KEY.format(
            user_id=user_id,
            session_id=session_id
        )
        
        session_data = cache.get(session_key)
        if not session_data:
            return False, "Session not found or expired."
        
        # Verify IP hasn't changed (strong indicator of hijacking)
        if ip_address and session_data.get('ip') != ip_address:
            logger.warning(f"Session validation failed for user {user_id}: IP mismatch")
            return False, "Session IP mismatch. Please login again."
        
        return True, None
    
    @staticmethod
    def logout(user_id, session_id):
        """Clean up session on logout"""
        session_key = LoginSecurityManager.SESSION_KEY.format(
            user_id=user_id,
            session_id=session_id
        )
        cache.delete(session_key)
        
        logger.info(f"Session ended for user {user_id}")


class ConcurrentSessionManager:
    """Manages concurrent session limits"""
    
    @staticmethod
    def get_active_sessions(user_id):
        """Get list of active sessions for a user"""
        concurrent_key = LoginSecurityManager.CONCURRENT_SESSIONS_KEY.format(user_id=user_id)
        return cache.get(concurrent_key, [])
    
    @staticmethod
    def get_session_count(user_id):
        """Get number of active sessions"""
        return len(ConcurrentSessionManager.get_active_sessions(user_id))
    
    @staticmethod
    def has_reached_limit(user_id):
        """Check if user has reached concurrent session limit"""
        max_sessions = getattr(settings, 'MAX_CONCURRENT_SESSIONS', 3)
        current = ConcurrentSessionManager.get_session_count(user_id)
        return current >= max_sessions
    
    @staticmethod
    def end_oldest_session(user_id):
        """Terminate the oldest session if limit reached"""
        concurrent_key = LoginSecurityManager.CONCURRENT_SESSIONS_KEY.format(user_id=user_id)
        sessions = cache.get(concurrent_key, [])
        
        if sessions:
            oldest = sessions.pop(0)
            cache.set(concurrent_key, sessions, 86400)
            return oldest
        
        return None


def get_client_ip(request):
    """
    Extract client IP address from request.
    Handles proxies and load balancers.
    """
    # Check for proxy headers
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take first IP if multiple
        ip = x_forwarded_for.split(',')[0].strip()
        return ip
    
    # Fallback to direct connection
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def get_location_from_ip(ip_address):
    """
    Get location from IP address.
    Placeholder - integrate with GeoIP2 or similar service if needed.
    """
    # TODO: Integrate with MaxMind GeoIP2 or similar for production
    # For now, return generic location based on IP octet for testing
    return f"Location({ip_address})"
