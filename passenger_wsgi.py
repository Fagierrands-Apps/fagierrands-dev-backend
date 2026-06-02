import os
import sys

# cPanel Python App Configuration
# Virtual environment path - cPanel auto-configures this
INTERP = os.path.join(os.environ['HOME'], 'virtualenv', 'api.errandserver.fagierrands.com', '3.11', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')

# Load Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()