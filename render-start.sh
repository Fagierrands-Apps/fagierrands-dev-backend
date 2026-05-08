#!/usr/bin/env bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
exec gunicorn fagierrandsbackup.wsgi --bind 0.0.0.0:$PORT --log-level debug --access-logfile - --error-logfile -
