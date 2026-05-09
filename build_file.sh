#!/bin/bash

# Exit the script if any command fails
set -e

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating admin user..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@fagierrands.com',
        password='FagiAdmin2026!',
        phone_number='+254700000000',
        user_type='ADMIN',
        first_name='Admin',
        last_name='User'
    )
    admin.phone_verified = True
    admin.is_verified = True
    admin.save()
    print('Admin user created successfully')
else:
    print('Admin user already exists')
EOF

# Run any custom build steps if needed
echo "Custom build steps (if any)..."
# Add any other necessary build commands here

echo "Build complete."