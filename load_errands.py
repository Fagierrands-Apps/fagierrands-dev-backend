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
customers = list(User.objects.filter(user_type='user')[:10])
handler = User.objects.filter(user_type='handler').first()

if not customers or not handler:
    print("❌ Need users and at least 1 handler!")
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
    {'status': 'cancelled', 'desc': 'Cancelled grocery delivery'},
    {'status': 'cancelled', 'desc': 'Cancelled document pickup'},
    {'status': 'completed', 'desc': 'Groceries delivered'},
    {'status': 'completed', 'desc': 'Parcel delivered'},
    {'status': 'completed', 'desc': 'Documents delivered'},
    {'status': 'completed', 'desc': 'Prescription delivered'},
    {'status': 'completed', 'desc': 'Shopping delivered'},
    {'status': 'completed', 'desc': 'Package delivered'},
    {'status': 'completed', 'desc': 'Food delivery completed'},
    {'status': 'completed', 'desc': 'Gift delivery completed'},
    {'status': 'completed', 'desc': 'Books delivered'},
    {'status': 'completed', 'desc': 'Electronics delivered'},
    {'status': 'in_transit', 'desc': 'Urgent delivery in progress'},
    {'status': 'in_transit', 'desc': 'Food delivery ongoing'},
    {'status': 'in_transit', 'desc': 'Package on the way'},
    {'status': 'in_transit', 'desc': 'Documents being delivered'},
    {'status': 'pending', 'desc': 'Awaiting pickup - Groceries'},
    {'status': 'pending', 'desc': 'Awaiting pickup - Documents'},
    {'status': 'pending', 'desc': 'Awaiting pickup - Package'},
    {'status': 'pending', 'desc': 'Awaiting pickup - Parcel'},
]

for i, e in enumerate(errands, 1):
    # Assign handler for non-pending errands
    assigned_handler = handler if e['status'] != 'pending' else None
    
    Order.objects.create(
        customer=customers[i % len(customers)],
        handler=assigned_handler,
        pickup_location=pickup,
        dropoff_location=dropoff,
        description=e['desc'],
        status=e['status'],
        amount=Decimal(500 + i * 50),
        created_at=datetime.now() - timedelta(days=20-i)
    )

print("✅ Loaded 20 errands:")
print("  • 2 cancelled")
print("  • 10 completed")
print("  • 4 in_transit")
print("  • 4 pending")
