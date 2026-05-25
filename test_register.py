#!/usr/bin/env python
"""Test registration endpoint without starting full server"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DATABASE_URL'] = 'sqlite:///test_db.sqlite3'
django.setup()

from django.core.management import call_command
from django.test import Client
import json

# Create tables
print("Creating database tables...")
call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)

# Create test client
client = Client()

# Test data
data = {
    "username": "testclient123",
    "email": "testclient@example.com",
    "password": "TestPass123!",
    "password2": "TestPass123!",
    "first_name": "Test",
    "last_name": "Client",
    "user_type": "user",
    "phone_number": "0725115550"
}

print("\nTesting POST /api/accounts/register/")
print(f"Data: {json.dumps(data, indent=2)}\n")

response = client.post(
    '/api/accounts/register/',
    data=json.dumps(data),
    content_type='application/json'
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
