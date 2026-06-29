"""
⚠️⚠️⚠️ CRITICAL PAYMENT SYSTEM - DO NOT MODIFY ⚠️⚠️⚠️

THIS MODULE IS PRODUCTION-TESTED AND HANDLES REAL MONEY TRANSACTIONS
ANY CHANGES CAN RESULT IN FAILED PAYMENTS OR FINANCIAL LOSS

WORKING CONFIGURATION (VERIFIED JUNE 5, 2026):
=================================================
PayBillNo: 880100 (NCBA main paybill)
AccountNo: 852054 (Till number)
TransactionType: CustomerPayBillOnline

NCBA CREDENTIALS REQUIRED IN .env:
===================================
NCBA_USERNAME=Errand@123
NCBA_PASSWORD=<secret>
NCBA_TILL_NO=852054
NCBA_PAYBILL_NO=880100
NCBA_TRANSACTION_TYPE=CustomerPayBillOnline
NCBA_CALLBACK_URL=<production-url>/api/orders/payments/ncba/callback/

CRITICAL FILES (DO NOT MODIFY):
================================
1. /orders/views_payment_ncba.py - Payment initiation & callbacks
2. /orders/ncba_service.py - NCBA API integration
3. /orders/serializers.py - Payment validation (line 67: PaymentPending check)
4. /orders/models.py - Order & Payment models

KEY FIXES APPLIED:
==================
 Payment status validation: 'PaymentPending' (PascalCase)
 Field mapping: order.user (not order.client)
 Account number: Uses till_no directly (852054)
 Optional fields for backward compatibility

TESTING CHECKLIST:
==================
 STK Push prompt received
 Payment successful with valid account
 Callback handling (if configured)
 Order status updates

IF YOU MUST MODIFY:
===================
1. Test in development environment first
2. Keep backup of working version
3. Never change account number format
4. Never change status validation logic
5. Document all changes with reason

SECURITY NOTES:
===============
- Credentials stored in .env (never commit)
- Use HTTPS in production
- Validate callback signatures
- Rate limit payment endpoints
- Log all transactions

SUPPORT CONTACT:
================
If payment issues occur, check:
1. Server logs: /logs/django.log
2. NCBA credentials are valid
3. Till 852054 is active
4. Callback URL is accessible

Last verified: June 5, 2026
Status:  PRODUCTION READY - DO NOT TOUCH
"""

# This file serves as documentation only
# See actual implementation in the files listed above
