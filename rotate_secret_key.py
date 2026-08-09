#!/usr/bin/env python3
"""
Rotate Django SECRET_KEY in .env file.
Usage: python rotate_secret_key.py
"""
import os
import re
from django.core.management.utils import get_random_secret_key

env_path = os.path.join(os.path.dirname(__file__), '.env')

if not os.path.exists(env_path):
    print(f"ERROR: .env not found at {env_path}")
    exit(1)

new_key = get_random_secret_key()

with open(env_path, 'r') as f:
    content = f.read()

if re.search(r'^SECRET_KEY=', content, re.MULTILINE):
    content = re.sub(r'^SECRET_KEY=.*$', f'SECRET_KEY={new_key}', content, flags=re.MULTILINE)
else:
    content += f'\nSECRET_KEY={new_key}\n'

with open(env_path, 'w') as f:
    f.write(content)

print(f"✅ SECRET_KEY rotated successfully.")
print("⚠️  All existing JWT tokens are now invalid — users will need to log in again.")
print("⚠️  Restart the server to apply the new key.")
