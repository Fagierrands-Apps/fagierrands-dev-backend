import os
import sys

# Virtual environment - cPanel handles this automatically
# Just make sure we're in the right directory
sys.path.insert(0, os.path.dirname(__file__))

# Import the real WSGI application from wsgi_app.py
# This way cPanel can overwrite THIS file but not wsgi_app.py
from wsgi_app import application