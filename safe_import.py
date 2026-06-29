#!/usr/bin/env python
"""
Clear all data from dev database
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')

from dotenv import load_dotenv
load_dotenv('.env.dev')

django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Profile
from orders.models import Order

User = get_user_model()

print("⚠️  WARNING: This will delete ALL data from dev database!")
print(f"Current counts:")
print(f"  Users: {User.objects.count()}")
print(f"  Profiles: {Profile.objects.count()}")
print(f"  Orders: {Order.objects.count()}")

confirm = input("\nType 'DELETE ALL' to confirm: ")

if confirm == "DELETE ALL":
    Order.objects.all().delete()
    print("✓ Deleted all orders")
    
    Profile.objects.all().delete()
    print("✓ Deleted all profiles")
    
    User.objects.all().delete()
    print("✓ Deleted all users")
    
    print("\n✅ Dev database cleared!")
else:
    print("❌ Cancelled")
