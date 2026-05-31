from django.http import HttpResponse
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
import io

@csrf_exempt
def run_migrations_view(request):
    """Run migrations via web endpoint - DELETE THIS AFTER USE"""
    if request.method == 'POST' and request.POST.get('secret') == 'migrate_now_2026':
        output = io.StringIO()
        try:
            call_command('migrate', '--noinput', stdout=output)
            result = output.getvalue()
            return HttpResponse(f"<pre>Migrations completed:\n{result}</pre>")
        except Exception as e:
            return HttpResponse(f"<pre>Error: {str(e)}</pre>", status=500)
    return HttpResponse("Invalid request", status=403)
