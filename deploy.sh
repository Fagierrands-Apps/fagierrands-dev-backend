#!/bin/bash
# Run this after uploading to cPanel

cd /home3/distinc3/fagierrandsbackendapi
source venv/bin/activate
python manage.py collectstatic --noinput
touch tmp/restart.txt
echo "✅ Deployment complete!"
