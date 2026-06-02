"""
Django WSGI Application for cPanel
This file is protected from cPanel overwrites
"""
import os
import sys

# Add project directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')

# Initialize Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
