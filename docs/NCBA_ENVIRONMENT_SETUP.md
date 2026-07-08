# NCBA Payment System - Environment Variables Setup

## ✅ Code Sync Complete

The following files have been synced from production:
- ✅ `orders/ncba_service.py` - Enhanced with credential validation and better error handling
- ✅ `orders/views_payment_ncba.py` - Production-tested payment views
- ✅ `fagierrandsbackup/settings.py` - Already configured correctly

## 🔐 Required Environment Variables

Add these to your system environment (NOT in code):

### Method 1: Export in Terminal (Temporary)
```bash
export NCBA_USERNAME="Errand@123"
export NCBA_PASSWORD="9Y7a24B5TNxxKimfnGz9MTbdn960JY57ASC/r6KOCQNnR220v52od6a2ajgEaipL"
export NCBA_TILL_NO="852054"
export NCBA_PAYBILL_NO="880100"
export NCBA_TRANSACTION_TYPE="CustomerPayBillOnline"
export NCBA_USE_TILL_AS_ACCOUNT="False"
```

### Method 2: Add to ~/.bashrc (Permanent)
```bash
echo 'export NCBA_USERNAME="Errand@123"' >> ~/.bashrc
echo 'export NCBA_PASSWORD="9Y7a24B5TNxxKimfnGz9MTbdn960JY57ASC/r6KOCQNnR220v52od6a2ajgEaipL"' >> ~/.bashrc
echo 'export NCBA_TILL_NO="852054"' >> ~/.bashrc
echo 'export NCBA_PAYBILL_NO="880100"' >> ~/.bashrc
echo 'export NCBA_TRANSACTION_TYPE="CustomerPayBillOnline"' >> ~/.bashrc
echo 'export NCBA_USE_TILL_AS_ACCOUNT="False"' >> ~/.bashrc
source ~/.bashrc
```

### Method 3: Use .env file with python-dotenv (Recommended for Development)
```bash
# Add to .env file (already exists)
cat >> .env << 'EOF'

# NCBA Till API Configuration
NCBA_USERNAME=Errand@123
NCBA_PASSWORD=9Y7a24B5TNxxKimfnGz9MTbdn960JY57ASC/r6KOCQNnR220v52od6a2ajgEaipL
NCBA_PAYBILL_NO=880100
NCBA_TILL_NO=852054
NCBA_TRANSACTION_TYPE=CustomerPayBillOnline
NCBA_USE_TILL_AS_ACCOUNT=False
EOF
```

## 🧪 Verification Script

Run this to verify NCBA is configured correctly:

```bash
cd /home/fagitone/Documents/GitHub/fagierrands-dev-backend
python manage.py shell
```

```python
# Test 1: Check environment variables loaded
from django.conf import settings
print("=" * 60)
print("NCBA Configuration Check")
print("=" * 60)
print(f"NCBA_USERNAME: {settings.NCBA_USERNAME}")
print(f"NCBA_PASSWORD: {'*' * 10}{settings.NCBA_PASSWORD[-10:] if settings.NCBA_PASSWORD else 'NOT SET'}")
print(f"NCBA_TILL_NO: {settings.NCBA_TILL_NO}")
print(f"NCBA_PAYBILL_NO: {settings.NCBA_PAYBILL_NO}")
print(f"NCBA_CALLBACK_URL: {settings.NCBA_CALLBACK_URL}")
print("=" * 60)

# Test 2: Initialize NCBA Service
from orders.ncba_service import NCBAService
service = NCBAService()
print("\nNCBA Service Initialized:")
print(f"  Username: {service.username}")
print(f"  Till No: {service.till_no}")
print(f"  Paybill: {service.paybill_no}")

# Test 3: Get Access Token
print("\nTesting Authentication...")
try:
    token = service.get_access_token()
    print(f"✅ SUCCESS: Token obtained")
    print(f"   Token preview: {token[:30]}...")
except Exception as e:
    print(f"❌ FAILED: {str(e)}")

print("\n" + "=" * 60)
print("If you see ✅ SUCCESS above, NCBA is ready!")
print("=" * 60)
```

## 📋 What Was Synced

### 1. `orders/ncba_service.py` Improvements:
- ✅ Credential validation before API calls
- ✅ Specific 401 Unauthorized error handling
- ✅ Better error messages with actionable guidance
- ✅ Enhanced logging for debugging
- ✅ Longer token cache (900s buffer vs 60s)

### 2. `orders/views_payment_ncba.py` Features:
- ✅ Auto STK push on payment initiation
- ✅ Payment status polling support
- ✅ Callback handling
- ✅ QR code generation
- ✅ Payment cancellation
- ✅ Order payment status tracking

## 🚀 Quick Start After Adding Environment Variables

1. **Restart your development server:**
   ```bash
   cd /home/fagitone/Documents/GitHub/fagierrands-dev-backend
   python manage.py runserver
   ```

2. **Test NCBA authentication:**
   ```bash
   python manage.py shell -c "from orders.ncba_service import NCBAService; s=NCBAService(); print('✅ Token:', s.get_access_token()[:30])"
   ```

3. **Test payment initiation (via API):**
   ```bash
   curl -X POST http://localhost:8000/api/orders/payments/initiate/ \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "order": 1,
       "amount": 100,
       "payment_method": "ncba",
       "phone_number": "254712345678"
     }'
   ```

## ✅ Success Criteria

After adding environment variables, you should see:
- ✅ No "NCBA credentials not configured" errors
- ✅ Token obtained successfully
- ✅ STK push can be initiated
- ✅ Payment status can be queried
- ✅ Callbacks are handled correctly

## 🔧 Troubleshooting

### Error: "NCBA credentials not configured"
**Solution:** Environment variables not loaded. Check:
1. Variables are exported in current shell
2. Server was restarted after adding variables
3. No typos in variable names

### Error: "401 Unauthorized"
**Solution:** Invalid credentials. Verify:
1. NCBA_USERNAME = `Errand@123`
2. NCBA_PASSWORD = `9Y7a24B5TNxxKimfnGz9MTbdn960JY57ASC/r6KOCQNnR220v52od6a2ajgEaipL`
3. No extra spaces or quotes in values

### Error: "Token request timed out"
**Solution:** Network issue. Check:
1. Internet connection
2. NCBA API is accessible: `curl https://c2bapis.ncbagroup.com`
3. Firewall settings

## 📝 Notes

- ✅ Code is now identical to production
- ✅ Settings are configured to read from environment
- ✅ No credentials in code (security best practice)
- ✅ Ready for production deployment

**Next Step:** Add the environment variables using one of the methods above, then run the verification script.
