#!/usr/bin/env python
"""Quick script to check payment system status"""
import django
import os
import sys

# Setup Django
sys.path.insert(0, '/home/fagitone/Documents/GitHub/fagierrands-dev-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')
django.setup()

from orders.models import Payment, Order
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

print("=" * 60)
print("PAYMENT SYSTEM STATUS CHECK")
print("=" * 60)

# Check environment variables
print("\n1. NCBA Configuration:")
print(f"   - Username: {'✓ Set' if settings.NCBA_USERNAME else '✗ Missing'}")
print(f"   - Password: {'✓ Set' if settings.NCBA_PASSWORD else '✗ Missing'}")
print(f"   - Till Number: {settings.NCBA_TILL_NO if settings.NCBA_TILL_NO else '✗ Missing'}")
print(f"   - Paybill Number: {settings.NCBA_PAYBILL_NO if settings.NCBA_PAYBILL_NO else '✗ Missing'}")

# Check recent payments
print("\n2. Recent Payments (Last 5):")
payments = Payment.objects.all().order_by('-id')[:5]
if payments:
    for p in payments:
        date_str = p.payment_date.strftime('%Y-%m-%d %H:%M') if p.payment_date else 'N/A'
        print(f"   - ID: {p.id} | Status: {p.status} | Amount: {p.amount} | Date: {date_str}")
else:
    print("   No payments found")

# Check payment statistics
print("\n3. Payment Statistics:")
total_payments = Payment.objects.count()
pending_payments = Payment.objects.filter(status='pending').count()
completed_payments = Payment.objects.filter(status='completed').count()
failed_payments = Payment.objects.filter(status='failed').count()

print(f"   - Total: {total_payments}")
print(f"   - Pending: {pending_payments}")
print(f"   - Completed: {completed_payments}")
print(f"   - Failed: {failed_payments}")

# Check recent orders
print("\n4. Recent Orders (Last 5):")
orders = Order.objects.all().order_by('-id')[:5]
if orders:
    for o in orders:
        date_str = o.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(o, 'created_at') and o.created_at else 'N/A'
        print(f"   - ID: {o.id} | Status: {o.status} | Amount: {o.amount} | Date: {date_str}")
else:
    print("   No orders found")

# Test NCBA service
print("\n5. NCBA Service Test:")
try:
    from orders.ncba_service import NCBAService
    ncba = NCBAService()
    print(f"   - Service initialized: ✓")
    print(f"   - Base URL: {ncba.base_url}")
    print(f"   - Attempting token fetch...")
    token = ncba.get_access_token()
    if token:
        print(f"   - Token obtained: ✓ (length: {len(token)})")
    else:
        print(f"   - Token obtained: ✗")
except Exception as e:
    print(f"   - Error: {str(e)}")

print("\n" + "=" * 60)
print("CHECK COMPLETE")
print("=" * 60)
