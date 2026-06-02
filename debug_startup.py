"""
Custom Django startup logger for cPanel debugging
Creates a log file we can check when things go wrong
"""
import os
import sys
import traceback
from datetime import datetime

# Log file path
LOG_FILE = '/home3/distinc3/api.errandserver.fagierrands.com/startup_debug.log'

def log(message):
    """Write to log file with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

# Clear old log
try:
    open(LOG_FILE, 'w').close()
except:
    pass

log("=" * 50)
log("Django Startup Debug Log")
log("=" * 50)

log(f"Python Version: {sys.version}")
log(f"Python Executable: {sys.executable}")
log(f"Current Directory: {os.getcwd()}")

# Test Django import
try:
    import django
    log(f"✓ Django imported successfully - Version: {django.get_version()}")
except Exception as e:
    log(f"✗ Django import FAILED: {e}")
    log(traceback.format_exc())
    sys.exit(1)

# Test settings import
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')
    log(f"✓ DJANGO_SETTINGS_MODULE set to: {os.environ['DJANGO_SETTINGS_MODULE']}")
except Exception as e:
    log(f"✗ Settings module FAILED: {e}")
    log(traceback.format_exc())
    sys.exit(1)

# Test Django setup
try:
    django.setup()
    log("✓ Django setup() completed successfully")
except Exception as e:
    log(f"✗ Django setup FAILED: {e}")
    log(traceback.format_exc())
    sys.exit(1)

# Test database connection
try:
    from django.db import connection
    connection.ensure_connection()
    log("✓ Database connection successful")
except Exception as e:
    log(f"✗ Database connection FAILED: {e}")
    log(traceback.format_exc())

# Test WSGI application
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    log("✓ WSGI application created successfully")
    log("=" * 50)
    log("STARTUP SUCCESSFUL - App should be running")
    log("=" * 50)
except Exception as e:
    log(f"✗ WSGI application FAILED: {e}")
    log(traceback.format_exc())
    sys.exit(1)
