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
