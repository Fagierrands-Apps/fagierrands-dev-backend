#!/usr/bin/env python
"""
Debug script to check phone number flow in NCBA payment
"""
import os
import sys
import django

sys.path.insert(0, '/home/fagitone/Documents/GitHub/fagierrands-dev-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')

# Mock required env vars
os.environ['SECRET_KEY'] = 'test'
os.environ['PG_DB_NAME'] = 'test'
os.environ['PG_USER'] = 'test'
os.environ['PG_PASSWORD'] = 'test'
os.environ['PG_HOST'] = 'test'
os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_SERVICE_ROLE_KEY'] = 'test'
os.environ['EMAIL_HOST_PASSWORD'] = 'test'

django.setup()

from orders.models import Payment

print("=" * 70)
print("CHECKING RECENT PAYMENTS - PHONE NUMBER VERIFICATION")
print("=" * 70)

# Get last 5 payments
payments = Payment.objects.all().order_by('-payment_date')[:5]

if not payments:
    print("\n❌ No payments found in database")
else:
    print(f"\nFound {payments.count()} recent payments:\n")
    
    for p in payments:
        print(f"Payment ID: {p.id}")
        print(f"  Order ID: {p.order.id}")
        print(f"  Client: {p.client.username if p.client else 'N/A'}")
        print(f"  Client Phone: {p.client.phone_number if p.client and hasattr(p.client, 'phone_number') else 'N/A'}")
        print(f"  Payment Phone: {p.phone_number}")
        print(f"  Amount: {p.amount}")
        print(f"  Status: {p.status}")
        print(f"  Method: {p.payment_method}")
        print(f"  Date: {p.payment_date}")
        
        # Check if phone numbers match
        if p.client and hasattr(p.client, 'phone_number'):
            if p.phone_number == p.client.phone_number:
                print(f"  ⚠️  ISSUE: Payment phone matches client phone (not from request)")
            else:
                print(f"  ✅ Payment phone is different from client phone (from request)")
        print("-" * 70)

print("\n" + "=" * 70)
print("DIAGNOSIS")
print("=" * 70)
print("\nThe phone_number field in Payment model should come from:")
print("  validated_data.get('phone_number') in serializer.create()")
print("\nIf STK push goes to wrong number, check:")
print("  1. Request body has correct phone_number")
print("  2. Serializer is saving the correct phone_number")
print("  3. No default value overriding the phone_number")
print("=" * 70)
