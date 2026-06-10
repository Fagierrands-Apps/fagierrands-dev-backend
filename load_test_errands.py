#!/usr/bin/env python
"""
Load 10 test errands into dev database
1 cancelled, 6 completed, 2 in_transit, 2 pending
"""
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

# Get or create test users
customer, _ = User.objects.get_or_create(
    username='test_customer',
    defaults={
        'email': 'customer@test.com',
        'phone_number': '254700000001',
        'user_type': 'customer',
        'is_verified': True
    }
)

handler, _ = User.objects.get_or_create(
    username='test_handler',
    defaults={
        'email': 'handler@test.com',
        'phone_number': '254700000002',
        'user_type': 'handler',
        'is_verified': True
    }
)

# Get or create locations
pickup, _ = Location.objects.get_or_create(
    name='Westlands Mall',
    defaults={'address': 'Westlands, Nairobi', 'latitude': -1.2676, 'longitude': 36.8078}
)

dropoff, _ = Location.objects.get_or_create(
    name='Karen Shopping Center',
    defaults={'address': 'Karen, Nairobi', 'latitude': -1.3197, 'longitude': 36.7070}
)

errands = [
    {'status': 'cancelled', 'description': 'Deliver documents - Cancelled'},
    {'status': 'completed', 'description': 'Pick up groceries'},
    {'status': 'completed', 'description': 'Deliver parcel'},
    {'status': 'completed', 'description': 'Pick up prescription'},
    {'status': 'completed', 'description': 'Deliver documents'},
    {'status': 'completed', 'description': 'Shopping delivery'},
    {'status': 'completed', 'description': 'Package pickup'},
    {'status': 'in_transit', 'description': 'Urgent delivery in progress'},
    {'status': 'in_transit', 'description': 'Food delivery ongoing'},
    {'status': 'pending', 'description': 'Waiting for pickup'},
]

for i, errand in enumerate(errands, 1):
    Order.objects.create(
        customer=customer,
        handler=handler if errand['status'] != 'pending' else None,
        pickup_location=pickup,
        dropoff_location=dropoff,
        description=errand['description'],
        status=errand['status'],
        amount=Decimal('500.00') + Decimal(i * 50),
        created_at=datetime.now() - timedelta(days=10-i)
    )

print(f'✅ Loaded 10 test errands:')
print(f'  • 1 cancelled')
print(f'  • 6 completed')
print(f'  • 2 in_transit')
print(f'  • 2 pending (1 unassigned)')
print(f'  Customer: {customer.username}')
print(f'  Handler: {handler.username}')
