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

# Change this to True to actually delete
CONFIRM_DELETE = True

print("⚠️  Dev Database Clear Script")
print(f"\nCurrent counts:")
print(f"  Users: {User.objects.count()}")
print(f"  Profiles: {Profile.objects.count()}")
print(f"  Orders: {Order.objects.count()}")

if not CONFIRM_DELETE:
    print("\n❌ CONFIRM_DELETE is False")
    print("Change line 22 to: CONFIRM_DELETE = True")
    print("Then run again to delete all data")
    sys.exit(0)

print("\n🗑️  Deleting all data...")

Order.objects.all().delete()
print("✓ Deleted all orders")

Profile.objects.all().delete()
print("✓ Deleted all profiles")

User.objects.all().delete()
print("✓ Deleted all users")

print("\n✅ Dev database cleared!")
