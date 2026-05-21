#!/usr/bin/env python
import os
import django
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')
os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'

django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from accounts.models import User
from orders.views_rider_details import get_assigned_rider_details
from orders.models import Order

def test_rider_details():
    factory = APIRequestFactory()
    
    # Get any user as client
    client = User.objects.filter(is_active=True).first()
    if not client:
        print("No active user found")
        return
    
    # Get an order
    order = Order.objects.select_related('assistant', 'assistant__profile').first()
    
    if not order:
        print("No orders found in database")
        return
    
    print(f"Testing with order ID: {order.id}")
    print(f"Client: {order.client.phone_number}")
    print(f"Rider assigned: {order.assistant is not None}")
    if order.assistant:
        print(f"Rider: {order.assistant.phone_number}")
    
    # Test 1: Get rider details (as order client)
    print("\n=== Test 1: Get Assigned Rider Details (Order Client) ===")
    request = factory.get(f"/api/orders/{order.id}/rider-details/")
    force_authenticate(request, user=order.client)
    response = get_assigned_rider_details(request, order.id)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.data}")
    
    # Test 2: Unauthorized access
    print("\n=== Test 2: Unauthorized Access ===")
    other_user = User.objects.exclude(id=order.client.id).first()
    if other_user:
        request = factory.get(f"/api/orders/{order.id}/rider-details/")
        force_authenticate(request, user=other_user)
        response = get_assigned_rider_details(request, order.id)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.data}")
    
    # Test 3: Non-existent order
    print("\n=== Test 3: Non-existent Order ===")
    request = factory.get("/api/orders/99999/rider-details/")
    force_authenticate(request, user=order.client)
    response = get_assigned_rider_details(request, 99999)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.data}")

if __name__ == "__main__":
    test_rider_details()
