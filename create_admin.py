#!/usr/bin/env python
"""
Run this script once on Render to create admin user
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@fagierrands.com',
        password='FagiAdmin2026!',
        phone_number='+254700000000',
        user_type='admin',
        first_name='Admin',
        last_name='User'
    )
    admin.phone_verified = True
    admin.is_verified = True
    admin.save()
    print('✅ Admin user created successfully')
else:
    print('ℹ️  Admin user already exists')
