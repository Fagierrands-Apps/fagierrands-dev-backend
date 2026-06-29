#!/usr/bin/env python
"""Check backend logs for errors"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()

print("=== DATABASE STATUS ===\n")

# Check orders
orders = Order.objects.all()
print(f"Total Orders: {orders.count()}")
print(f"  - Pending: {Order.objects.filter(status='Pending').count()}")
print(f"  - InTransit: {Order.objects.filter(status='InTransit').count()}")
print(f"  - Completed: {Order.objects.filter(status='Completed').count()}")
print(f"  - Cancelled: {Order.objects.filter(status='Cancelled').count()}")

# Check users
users = User.objects.filter(user_type='user')
assistants = User.objects.filter(user_type='assistant')
handlers = User.objects.filter(user_type='handler')

print(f"\nTotal Users: {users.count()}")
print(f"Total Assistants/Riders: {assistants.count()}")
print(f"Total Handlers: {handlers.count()}")

# Check verified assistants
verified = User.objects.filter(user_type='assistant', assistant_verification__status='approved').count()
print(f"Verified Assistants: {verified}")

# Show sample orders
print("\n=== SAMPLE ORDERS ===\n")
for order in orders[:5]:
    print(f"ID: {order.id} | {order.order_number}")
    print(f"  User: {order.user.username}")
    print(f"  Assistant: {order.assistant.username if order.assistant else 'None'}")
    print(f"  Status: {order.status}")
    print(f"  Title: {order.title}")
    print()

print("\n=== CHECK API ENDPOINTS ===")
print("Test these URLs:")
print(f"- Orders API: https://dev.fagierrands.com/api/orders/")
print(f"- Stats API: https://dev.fagierrands.com/api/dashboard/stats/")
print(f"- Assistants API: https://dev.fagierrands.com/api/assistants/")
