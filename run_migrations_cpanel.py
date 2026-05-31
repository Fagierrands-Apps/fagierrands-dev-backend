#!/usr/bin/env python
import os
import sys
import django

# Add the fagierrandsbackup directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fagierrandsbackup'))

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')
os.environ.setdefault('DB_NAME', 'distinc3_FagierrandsNew')
os.environ.setdefault('DB_USER', 'distinc3_FagierrandsNew')
os.environ.setdefault('DB_PASSWORD', 'Pa7swrd1990@')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')
os.environ.setdefault('DB_ENGINE', 'django.db.backends.postgresql')
os.environ.setdefault('SECRET_KEY', '9r1%hz2tdkhu39#6f^^_z(&0u&1g8=^cy_$(907_fs#tni-1r7')

# Setup Django
django.setup()

# Run migrations
from django.core.management import call_command

print("Running migrations...")
call_command('migrate', '--noinput')
print("Migrations completed!")

print("\nCollecting static files...")
call_command('collectstatic', '--noinput')
print("Static files collected!")
