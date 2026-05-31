import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fagierrandsbackend'))

from fagierrandsbackend.wsgi import application
