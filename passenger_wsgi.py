import os
import sys

# Add the fagierrandsbackend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fagierrandsbackend'))

from fagierrandsbackup.wsgi import application