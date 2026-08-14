from django.http import HttpResponseNotFound

_BLOCKED = {
    '/.env', '/.env.local', '/.env.production', '/.env.development',
    '/.env.test', '/.env.backup', '/.env.staging',
    '/.git/config', '/.aws/credentials', '/.ssh/id_rsa',
    '/etc/passwd', '/etc/shadow',
    '/phpinfo.php', '/info.php', '/debug.php', '/test.php',
    '/wp-login.php', '/wp-admin/', '/admin.php',
    '/phpmyadmin/', '/pma/', '/shell.php', '/cmd.php',
}


class BlockProbesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path_info.lower() in _BLOCKED:
            return HttpResponseNotFound()
        return self.get_response(request)


class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking (already set by Django's XFrameOptionsMiddleware, but explicit)
        response['X-Frame-Options'] = 'DENY'
        
        # Enable XSS protection in older browsers
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy — don't send referrer to external sites
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature Policy) — restrict dangerous features
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=(), '
            'usb=(), '
            'accelerometer=(), '
            'gyroscope=()'
        )
        
        return response
