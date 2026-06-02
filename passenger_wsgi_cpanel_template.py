# passenger_wsgi.py template for cPanel
# REPLACE 'username' with your actual cPanel username

import sys
import os

# Virtual environment Python interpreter path
INTERP = "/home/username/virtualenv/api.errandserver.fagitone.com/3.11/bin/python3"

# Ensure we're using the virtual environment
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add project directory to Python path
sys.path.insert(0, '/home/username/api.errandserver.fagitone.com')

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'fagierrandsbackup.settings'

# Load environment variables from .env
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Initialize Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
