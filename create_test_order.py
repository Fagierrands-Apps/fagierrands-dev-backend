#!/usr/bin/env python
"""
Quick script to create a test order for testing handler notifications
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')
django.setup()

from orders.models import Order
from accounts.models import User

# Get a test user (or create one)
try:
    user = User.objects.filter(user_type='client').first()
    if not user:
        print("❌ No client users found! Creating test client...")
        user = User.objects.create_user(
            phone_number='254700000001',
            first_name='Test',
            last_name='Client',
            user_type='client',
            is_phone_verified=True
        )
        print(f"✅ Created test client: {user.phone_number}")
except Exception as e:
    print(f"Error getting user: {e}")
    exit(1)

# Create test order
order = Order.objects.create(
    user=user,
    title='Test Errand - Handler Notification',
    pickup_address='Westlands, Nairobi',
    pickup_lat=-1.2674,
    pickup_lng=36.8084,
    delivery_address='Kilimani, Nairobi',
    delivery_lat=-1.2921,
    delivery_lng=36.7856,
    receiver_name='Test Receiver',
    receiver_phone='254700000002',
    distance_km=5.2,
    total_price=500,
    status='Pending',
    payment_method='mpesa',
    payment_status='pending'
)

print(f"\n🎉 TEST ORDER CREATED!")
print(f"📦 Order ID: {order.id}")
print(f"📝 Order Number: {order.order_number}")
print(f"📍 From: {order.pickup_address}")
print(f"📍 To: {order.delivery_address}")
print(f"💰 Price: KES {order.total_price}")
print(f"📊 Status: {order.status}")
print(f"\n⏰ Wait 10 seconds for handler dashboard to detect it...")
