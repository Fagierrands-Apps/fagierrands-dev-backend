#!/usr/bin/env python
"""
Production-mode test for all onboarding endpoints
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')
os.environ['DEBUG'] = 'True'  # Keep debug for testing
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
import json

User = get_user_model()
client = Client()

print("=" * 60)
print("TESTING ONBOARDING ENDPOINTS (Production Mode)")
print("=" * 60)

# Clean up test user
User.objects.filter(phone_number='+254700000001').delete()

# Test 1: Register
print("\n1. Testing REGISTER...")
response = client.post('/api/accounts/register/', 
    data=json.dumps({
        'username': 'testuser001',
        'phone_number': '+254700000001',
        'email': 'test001@test.com',
        'password': 'Test123!',
        'password2': 'Test123!',
        'first_name': 'Test',
        'last_name': 'User',
        'user_type': 'user'
    }),
    content_type='application/json'
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json() if response.status_code < 500 else response.content[:200]}")

if response.status_code == 201:
    print("✅ REGISTER works")
else:
    print(f"❌ REGISTER failed: {response.status_code}")

# Test 2: Resend OTP
print("\n2. Testing RESEND OTP...")
response = client.post('/api/accounts/resend-otp/',
    data=json.dumps({'phone_number': '+254700000001'}),
    content_type='application/json'
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json() if response.status_code < 500 else response.content[:200]}")

if response.status_code == 200:
    print("✅ RESEND OTP works")
else:
    print(f"❌ RESEND OTP failed: {response.status_code}")

# Get OTP from database
user = User.objects.get(phone_number='+254700000001')
otp = user.phone_otp
print(f"OTP from DB: {otp}")

# Test 3: Verify Phone
print("\n3. Testing VERIFY PHONE...")
response = client.post('/api/accounts/verify-phone/',
    data=json.dumps({
        'phone_number': '+254700000001',
        'otp': otp
    }),
    content_type='application/json'
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json() if response.status_code < 500 else response.content[:200]}")

if response.status_code == 200:
    print("✅ VERIFY PHONE works")
    tokens = response.json()
    access_token = tokens.get('access')
else:
    print(f"❌ VERIFY PHONE failed: {response.status_code}")

# Test 4: Login
print("\n4. Testing LOGIN...")
response = client.post('/api/accounts/login/',
    data=json.dumps({
        'phone_number': '+254700000001',
        'password': 'Test123!'
    }),
    content_type='application/json'
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json() if response.status_code < 500 else response.content[:200]}")

if response.status_code == 200:
    print("✅ LOGIN works")
else:
    print(f"❌ LOGIN failed: {response.status_code}")

# Test 5: Password Reset Request
print("\n5. Testing PASSWORD RESET REQUEST...")
response = client.post('/api/accounts/password-reset/request/',
    data=json.dumps({'phone_number': '+254700000001'}),
    content_type='application/json'
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json() if response.status_code < 500 else response.content[:200]}")

if response.status_code == 200:
    print("✅ PASSWORD RESET REQUEST works")
else:
    print(f"❌ PASSWORD RESET REQUEST failed: {response.status_code}")

# Test 6: Admin Login Page
print("\n6. Testing ADMIN LOGIN PAGE...")
response = client.get('/admin/login/')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ ADMIN LOGIN PAGE works")
else:
    print(f"❌ ADMIN LOGIN PAGE failed: {response.status_code}")

# Test 7: Swagger Docs
print("\n7. Testing SWAGGER DOCS...")
response = client.get('/api/docs/')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ SWAGGER DOCS works")
else:
    print(f"❌ SWAGGER DOCS failed: {response.status_code}")

print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)

# Cleanup
User.objects.filter(phone_number='+254700000001').delete()
