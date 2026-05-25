#!/usr/bin/env bash

echo "Testing database connection..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.db import connection
try:
    connection.ensure_connection()
    print('✓ Database connection successful')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    exit(1)
"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
exec gunicorn config.wsgi --bind 0.0.0.0:$PORT --log-level debug --access-logfile - --error-logfile -
