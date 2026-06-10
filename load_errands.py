#!/usr/bin/env python
"""Load 20 test errands (run after load_users.py)"""
import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()

# Get users
users = list(User.objects.filter(user_type='user')[:10])
handler = User.objects.filter(user_type='handler').first()

if not users or not handler:
    print("❌ Need users and at least 1 handler!")
    exit(1)

errands = [
    {'status': 'Cancelled', 'desc': 'Cancelled grocery delivery'},
    {'status': 'Cancelled', 'desc': 'Cancelled document pickup'},
    {'status': 'Completed', 'desc': 'Groceries delivered'},
    {'status': 'Completed', 'desc': 'Parcel delivered'},
    {'status': 'Completed', 'desc': 'Documents delivered'},
    {'status': 'Completed', 'desc': 'Prescription delivered'},
    {'status': 'Completed', 'desc': 'Shopping delivered'},
    {'status': 'Completed', 'desc': 'Package delivered'},
    {'status': 'Completed', 'desc': 'Food delivery'},
    {'status': 'Completed', 'desc': 'Gift delivery'},
    {'status': 'Completed', 'desc': 'Books delivered'},
    {'status': 'Completed', 'desc': 'Electronics delivered'},
    {'status': 'InTransit', 'desc': 'Urgent delivery'},
    {'status': 'InTransit', 'desc': 'Food delivery ongoing'},
    {'status': 'InTransit', 'desc': 'Package on the way'},
    {'status': 'InTransit', 'desc': 'Documents being delivered'},
    {'status': 'Pending', 'desc': 'Awaiting pickup - Groceries'},
    {'status': 'Pending', 'desc': 'Awaiting pickup - Documents'},
    {'status': 'Pending', 'desc': 'Awaiting pickup - Package'},
    {'status': 'Pending', 'desc': 'Awaiting pickup - Parcel'},
]

for i, e in enumerate(errands, 1):
    assigned = handler if e['status'] != 'Pending' else None
    
    Order.objects.create(
        user=users[i % len(users)],
        assistant=assigned,
        title=e['desc'],
        item_description=e['desc'],
        pickup_address='Westlands Mall, Nairobi',
        pickup_lat=-1.2676,
        pickup_lng=36.8078,
        delivery_address='Karen Shopping Center, Nairobi',
        delivery_lat=-1.3197,
        delivery_lng=36.7070,
        receiver_name='Test Receiver',
        receiver_phone='254700000000',
        distance_km=Decimal('10.5'),
        base_price=Decimal('500'),
        total_price=Decimal(500 + i * 50),
        status=e['status'],
        payment_method='mpesa',
        payment_status='paid' if e['status'] in ['Completed', 'InTransit'] else 'pending',
        created_at=datetime.now() - timedelta(days=20-i)
    )

print("✅ Loaded 20 errands:")
print("  • 2 cancelled")
print("  • 10 completed")
print("  • 4 in_transit")
print("  • 4 pending")
