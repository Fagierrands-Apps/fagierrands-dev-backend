#!/bin/bash
set -e

python manage.py migrate --noinput
exec gunicorn fagierrands.wsgi --bind 0.0.0.0:$PORT --log-file -
