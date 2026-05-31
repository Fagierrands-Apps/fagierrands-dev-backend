import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Try to import from the correct location
try:
    from fagierrandsbackup.wsgi import application
except ImportError:
    try:
        from fagierrandsbackend.wsgi import application
    except ImportError:
        # If nested structure exists
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fagierrandsbackup'))
        try:
            from fagierrandsbackup.wsgi import application
        except ImportError:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fagierrandsbackend'))
            from fagierrandsbackend.wsgi import application
