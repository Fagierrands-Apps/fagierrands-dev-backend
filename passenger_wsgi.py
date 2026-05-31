import os
import sys

# Add the fagierrandsbackup directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fagierrandsbackup'))

from fagierrandsbackup.wsgi import application
