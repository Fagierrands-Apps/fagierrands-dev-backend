import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# Use same settings as Render - will auto-detect cPanel vs Render
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()