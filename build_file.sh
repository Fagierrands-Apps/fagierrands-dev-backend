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
python manage.py migrate --noinput

# Verify token_blacklist tables exist
echo "Verifying token_blacklist tables..."
python manage.py shell << 'VERIFY_EOF'
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE '%token_blacklist%'")
tables = cursor.fetchall()
print(f"Token blacklist tables found: {tables}")
if not tables:
    print("WARNING: token_blacklist tables not found! Running migrations again...")
VERIFY_EOF

# Run token_blacklist migrations specifically
echo "Ensuring token_blacklist migrations..."
python manage.py migrate token_blacklist --noinput

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