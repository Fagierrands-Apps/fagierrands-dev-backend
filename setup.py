import os
import sys

SECRET = "run-setup-fagierrands-2026"

def application(environ, start_response):
    if environ.get('QUERY_STRING', '') != f"token={SECRET}":
        start_response('403 Forbidden', [('Content-Type', 'text/plain')])
        return [b'Forbidden']

    sys.path.insert(0, os.path.dirname(__file__))
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')

    import django
    django.setup()

    from django.core.management import call_command
    from io import StringIO
    output = []

    for cmd in ['migrate', 'collectstatic']:
        try:
            buf = StringIO()
            kwargs = {'--noinput': ''} if cmd == 'collectstatic' else {}
            call_command(cmd, '--noinput', stdout=buf, stderr=buf)
            output.append(f"=== {cmd.upper()} OK ===\n{buf.getvalue()}")
        except Exception as e:
            output.append(f"=== {cmd.upper()} ERROR ===\n{e}")

    output.append("\nDONE — delete setup.py from server now.")
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ["\n".join(output).encode()]
