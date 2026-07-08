#!/usr/bin/env python
"""Check rider availability status"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()

print("=== RIDER AVAILABILITY STATUS ===\n")

assistants = User.objects.filter(
    user_type='assistant',
    assistant_verification__status='approved'
).select_related('assistant_verification')

if not assistants.exists():
    print("❌ No verified assistants found!")
    exit(1)

print(f"Total Verified Riders: {assistants.count()}\n")

for assistant in assistants:
    # Check active orders
    active_orders = Order.objects.filter(
        assistant=assistant,
        status__in=['Pending', 'Assigned', 'InTransit']
    )
    
    # Current delivery
    current = Order.objects.filter(
        assistant=assistant,
        status='InTransit'
    ).first()
    
    is_available = active_orders.count() == 0
    
    print(f"{'✅' if is_available else '🚚'} {assistant.first_name} {assistant.last_name} ({assistant.username})")
    print(f"   Phone: {assistant.phone_number}")
    print(f"   Vehicle: {assistant.assistant_verification.vehicle_type}")
    print(f"   Status: {'AVAILABLE' if is_available else 'ON DELIVERY'}")
    print(f"   Active Orders: {active_orders.count()}")
    
    if current:
        print(f"   Current Delivery: {current.order_number}")
        print(f"   From: {current.pickup_address[:30]}...")
        print(f"   To: {current.delivery_address[:30]}...")
    
    print()

# Summary
available = assistants.filter(
    assigned_orders__status__in=['Pending', 'Assigned', 'InTransit']
).distinct().count()

print(f"\n📊 SUMMARY:")
print(f"   Available: {assistants.count() - available}")
print(f"   Busy: {available}")
