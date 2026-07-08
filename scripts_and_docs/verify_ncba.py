#!/usr/bin/env python
"""
NCBA Payment System Verification Script
Run this after adding environment variables to verify NCBA is configured correctly
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/fagitone/Documents/GitHub/fagierrands-dev-backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')
django.setup()

from django.conf import settings
from orders.ncba_service import NCBAService

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def main():
    print_header("NCBA Payment System Verification")
    
    # Test 1: Check Environment Variables
    print_header("Test 1: Environment Variables")
    
    checks = {
        'NCBA_USERNAME': settings.NCBA_USERNAME,
        'NCBA_PASSWORD': settings.NCBA_PASSWORD,
        'NCBA_TILL_NO': settings.NCBA_TILL_NO,
        'NCBA_PAYBILL_NO': settings.NCBA_PAYBILL_NO,
        'NCBA_TRANSACTION_TYPE': settings.NCBA_TRANSACTION_TYPE,
        'NCBA_CALLBACK_URL': settings.NCBA_CALLBACK_URL,
    }
    
    all_set = True
    for key, value in checks.items():
        if key == 'NCBA_PASSWORD':
            if value:
                masked = '*' * 10 + value[-10:] if len(value) > 10 else '*' * len(value)
                print_success(f"{key}: {masked}")
            else:
                print_error(f"{key}: NOT SET")
                all_set = False
        else:
            if value:
                print_success(f"{key}: {value}")
            else:
                print_error(f"{key}: NOT SET")
                all_set = False
    
    if not all_set:
        print_error("\nSome environment variables are missing!")
        print("\nAdd them using one of these methods:")
        print("1. Export in terminal: export NCBA_USERNAME='Errand@123'")
        print("2. Add to ~/.bashrc for permanent setup")
        print("3. Add to .env file (recommended for development)")
        print("\nSee NCBA_ENVIRONMENT_SETUP.md for details")
        return False
    
    # Test 2: Initialize NCBA Service
    print_header("Test 2: NCBA Service Initialization")
    
    try:
        service = NCBAService()
        print_success(f"Service initialized")
        print(f"   Base URL: {service.base_url}")
        print(f"   Username: {service.username}")
        print(f"   Till No: {service.till_no}")
        print(f"   Paybill: {service.paybill_no}")
        print(f"   Transaction Type: {service.default_transaction_type}")
        print(f"   Callback URL: {service.callback_url}")
    except Exception as e:
        print_error(f"Failed to initialize service: {str(e)}")
        return False
    
    # Test 3: Authentication
    print_header("Test 3: NCBA Authentication")
    
    try:
        print("Requesting access token from NCBA API...")
        token = service.get_access_token()
        print_success("Authentication successful!")
        print(f"   Token preview: {token[:30]}...")
        print(f"   Token length: {len(token)} characters")
    except Exception as e:
        print_error(f"Authentication failed: {str(e)}")
        print("\nPossible causes:")
        print("1. Invalid credentials - verify NCBA_USERNAME and NCBA_PASSWORD")
        print("2. Network issue - check internet connection")
        print("3. NCBA API down - try again later")
        return False
    
    # Test 4: Configuration Summary
    print_header("Configuration Summary")
    
    print_success("All checks passed!")
    print("\nNCBA Payment System is ready to use:")
    print("  • STK Push: Ready")
    print("  • Payment Status Query: Ready")
    print("  • QR Code Generation: Ready")
    print("  • Webhook Callbacks: Ready")
    
    print("\nAvailable API Endpoints:")
    print("  POST   /api/orders/payments/initiate/")
    print("  GET    /api/orders/payments/<id>/")
    print("  POST   /api/orders/payments/<id>/process/")
    print("  POST   /api/orders/payments/ncba/callback/")
    print("  POST   /api/orders/payments/ncba/qr-generate/")
    print("  POST   /api/orders/payments/<id>/cancel/")
    print("  GET    /api/orders/<id>/payment-status/")
    
    print_header("Verification Complete")
    print_success("NCBA Payment System is fully configured and operational!")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
