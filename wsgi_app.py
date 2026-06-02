"""
Django WSGI Application for cPanel
This file is protected from cPanel overwrites
"""
import os
import sys
from datetime import datetime

# Add project directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Custom logging function
LOG_FILE = os.path.join(current_dir, 'wsgi_startup.log')

def log_startup(message):
    """Log startup messages"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    except:
        pass

log_startup("=" * 60)
log_startup("WSGI Startup Initiated")

try:
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')
    log_startup("Django settings module set")
    
    # Initialize Django application
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    log_startup("✓ Django application initialized successfully")
    log_startup("=" * 60)
    
except Exception as e:
    log_startup(f"✗ FATAL ERROR: {e}")
    import traceback
    log_startup(traceback.format_exc())
    log_startup("=" * 60)
    raise

