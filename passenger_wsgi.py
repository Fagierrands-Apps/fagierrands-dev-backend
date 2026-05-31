import os
import sys

# Add the application directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Django WSGI application
from fagierrandsbackend.wsgi import application
