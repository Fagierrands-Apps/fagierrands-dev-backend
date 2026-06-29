#!/usr/bin/env python
"""
Create Django superuser for dev server
Run via cPanel Python App: python create_superuser.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if superuser already exists
if User.objects.filter(username='admin').exists():
    print('✅ Superuser "admin" already exists')
else:
    # Create superuser
    User.objects.create_superuser(
        username='admin',
        email='admin@fagierrands.com',
        password='Admin@2026',
        phone_number='254739344825',
        first_name='Admin',
        last_name='User',
        user_type='admin',
        is_verified=True
    )
    print('✅ Superuser created successfully!')
    print('Username: admin')
    print('Password: Admin@2026')
    print('Login at: /admin/')
