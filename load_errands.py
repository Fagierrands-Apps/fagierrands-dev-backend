#!/usr/bin/env python
"""Load 10 test errands (run after load_users.py)"""
import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order
from locations.models import Location

User = get_user_model()

# Get users
customers = list(User.objects.filter(user_type='customer')[:10])
handler = User.objects.filter(user_type='handler').first()

if not customers or not handler:
    print("❌ Need customers and at least 1 handler!")
    exit(1)

# Create locations for first customer
customer = customers[0]
pickup = Location.objects.create(
    user=customer,
    name='Westlands Mall',
    address='Westlands, Nairobi',
    latitude=-1.2676,
    longitude=36.8078
)
dropoff = Location.objects.create(
    user=customer,
    name='Karen Center',
    address='Karen, Nairobi',
    latitude=-1.3197,
    longitude=36.7070
)

errands = [
    {'status': 'cancelled', 'desc': 'Cancelled delivery', 'handler': handler},
    {'status': 'completed', 'desc': 'Groceries delivered', 'handler': handler},
    {'status': 'completed', 'desc': 'Parcel delivered', 'handler': handler},
    {'status': 'completed', 'desc': 'Documents delivered', 'handler': handler},
    {'status': 'completed', 'desc': 'Prescription delivered', 'handler': handler},
    {'status': 'completed', 'desc': 'Shopping delivered', 'handler': handler},
    {'status': 'completed', 'desc': 'Package delivered', 'handler': handler},
    {'status': 'in_transit', 'desc': 'Urgent delivery', 'handler': handler},
    {'status': 'in_transit', 'desc': 'Food delivery', 'handler': handler},
    {'status': 'pending', 'desc': 'Awaiting pickup', 'handler': None},
]

for i, e in enumerate(errands, 1):
    Order.objects.create(
        customer=customers[i % len(customers)],
        handler=e['handler'],
        pickup_location=pickup,
        dropoff_location=dropoff,
        description=e['desc'],
        status=e['status'],
        amount=Decimal(500 + i * 50),
        created_at=datetime.now() - timedelta(days=10-i)
    )

print("✅ Loaded 10 errands:")
print("  • 1 cancelled")
print("  • 6 completed")
print("  • 2 in_transit")
print("  • 2 pending")
