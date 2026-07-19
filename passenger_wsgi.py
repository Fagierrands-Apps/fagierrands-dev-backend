import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
