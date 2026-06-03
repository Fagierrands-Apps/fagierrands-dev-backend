import os
import sys

# Fix OpenBLAS thread limit to prevent resource exhaustion
os.environ['OPENBLAS_NUM_THREADS'] = '4'

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()