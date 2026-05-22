# Payment System Status & Implementation Guide

## 🔍 CURRENT PAYMENT SYSTEM

### Active Payment Method: **NCBA Till API** ✅

**Implementation Status:** Fully implemented and configured

**Location:** 
- Service: `orders/ncba_service.py`
- Views: `orders/views_payment_ncba.py`
- Endpoints: `/api/orders/payments/*`

---

## 📋 CURRENT CONFIGURATION

### NCBA Till API Settings (in settings.py)
```python
NCBA_USERNAME = os.environ.get('NCBA_USERNAME', '')
NCBA_PASSWORD = os.environ.get('NCBA_PASSWORD', '')
NCBA_PAYBILL_NO = os.environ.get('NCBA_PAYBILL_NO', '880100')
NCBA_TILL_NO = os.environ.get('NCBA_TILL_NO', '')
NCBA_TRANSACTION_TYPE = 'CustomerPayBillOnline'
NCBA_USE_TILL_AS_ACCOUNT = False
NCBA_CALLBACK_URL = f"{BASE_URL}/api/orders/payments/ncba/callback/"
```

### Required Environment Variables on Render:
- ✅ `NCBA_USERNAME` - NCBA API username
- ✅ `NCBA_PASSWORD` - NCBA API password
- ✅ `NCBA_PAYBILL_NO` - Paybill number (default: 880100)
- ✅ `NCBA_TILL_NO` - Till number
- ✅ `BASE_URL` - Your app URL for callbacks

---

## 🚀 HOW IT WORKS

### Payment Flow:

1. **Client Initiates Payment**
   ```
   POST /api/orders/payments/initiate/
   {
     "order_id": 501,
     "payment_method": "mpesa",
     "phone_number": "+254712345678"
   }
   ```

2. **System Sends STK Push**
   - Gets NCBA access token
   - Initiates STK push to customer's phone
   - Customer enters M-Pesa PIN

3. **NCBA Processes Payment**
   - Customer confirms on phone
   - NCBA processes transaction
   - Sends callback to your server

4. **Callback Updates Status**
   ```
   POST /api/orders/payments/ncba/callback/
   ```
   - Updates payment status
   - Updates order status
   - Notifies client

---

## 🔧 PAYMENT ENDPOINTS

### 1. Initiate Payment
```
POST /api/orders/payments/initiate/
Body: {
  "order_id": 501,
  "payment_method": "mpesa",
  "phone_number": "+254712345678"
}
```

### 2. Check Payment Status
```
GET /api/orders/payments/{payment_id}/
```

### 3. Check Order Payment Status
```
GET /api/orders/{order_id}/payment-status/
```

### 4. Process Payment (NCBA)
```
POST /api/orders/payments/{payment_id}/process/
```

### 5. Generate QR Code
```
POST /api/orders/payments/ncba/qr-generate/
Body: {
  "amount": 450,
  "narration": "Order-501"
}
```

### 6. Cancel Payment
```
POST /api/orders/payments/{payment_id}/cancel/
```

### 7. NCBA Callback (Webhook)
```
POST /api/orders/payments/ncba/callback/
```

---

## ⚠️ POTENTIAL ISSUES

### Issue 1: Missing Credentials
**Symptom:** Payment fails with authentication error
**Cause:** NCBA credentials not set in Render
**Fix:** Add environment variables on Render

### Issue 2: Callback Not Received
**Symptom:** Payment stuck in "processing"
**Cause:** NCBA can't reach callback URL
**Fix:** Ensure `BASE_URL` is correct and accessible

### Issue 3: Phone Number Format
**Symptom:** STK push fails
**Cause:** Wrong phone format
**Fix:** Code already handles this (converts to 254XXXXXXXXX)

### Issue 4: Amount Decimals
**Symptom:** Payment rejected
**Cause:** NCBA doesn't accept decimals
**Fix:** Code already rounds amounts

---

## 🛠️ FIXING BROKEN PAYMENT

### Time Estimate: **30 minutes - 2 hours**

### Step 1: Verify Credentials (5 min)
Check Render environment variables:
```
NCBA_USERNAME = ?
NCBA_PASSWORD = ?
NCBA_TILL_NO = ?
```

### Step 2: Test NCBA Connection (10 min)
Create test script:
```python
from orders.ncba_service import NCBAService

service = NCBAService()
token = service.get_access_token()
print(f"Token: {token}")
```

### Step 3: Test STK Push (10 min)
```python
response = service.initiate_stk_push(
    phone_number="254712345678",
    amount=10,
    account_no="TEST-001"
)
print(response)
```

### Step 4: Check Callback URL (5 min)
Verify callback is accessible:
```bash
curl https://your-app.onrender.com/api/orders/payments/ncba/callback/
```

### Step 5: Test Full Flow (30 min)
1. Create test order
2. Initiate payment
3. Check phone for STK push
4. Confirm payment
5. Verify callback received
6. Check payment status updated

---

## 🔄 ALTERNATIVE: Switch to Direct M-Pesa

If NCBA is problematic, you can switch to direct M-Pesa Daraja API.

### Time Estimate: **2-4 hours**

### Files Already Present:
- ✅ `orders/views_payment_mpesa.py` - M-Pesa views
- ✅ `orders/mpesa_service.py` - M-Pesa service

### What's Needed:
1. M-Pesa credentials from Safaricom
2. Update environment variables
3. Switch payment endpoint
4. Test integration

### M-Pesa Credentials Required:
```
MPESA_CONSUMER_KEY
MPESA_CONSUMER_SECRET
MPESA_SHORTCODE
MPESA_PASSKEY
MPESA_ENVIRONMENT (sandbox/production)
```

---

## 📊 PAYMENT STATUS FLOW

```
pending → processing → completed
   ↓           ↓
failed      cancelled
```

### Status Meanings:
- **pending** - Payment record created, not yet initiated
- **processing** - STK push sent, waiting for customer
- **completed** - Payment successful ✅
- **failed** - Payment failed ❌
- **cancelled** - Payment cancelled by user

---

## 🧪 TESTING PAYMENT

### Test in Swagger:
1. Go to: `https://your-app.onrender.com/swagger/`
2. Find: `POST /api/orders/payments/initiate/`
3. Click "Try it out"
4. Enter test data
5. Execute

### Test with Postman:
```json
POST https://your-app.onrender.com/api/orders/payments/initiate/
Headers: {
  "Authorization": "Bearer YOUR_TOKEN",
  "Content-Type": "application/json"
}
Body: {
  "order_id": 1,
  "payment_method": "mpesa",
  "phone_number": "+254712345678"
}
```

---

## 🎯 QUICK FIX CHECKLIST

If payment is broken, check in this order:

- [ ] NCBA credentials set on Render?
- [ ] BASE_URL correct?
- [ ] NCBA_TILL_NO set?
- [ ] Callback URL accessible?
- [ ] Test phone number valid?
- [ ] Order exists and is pending?
- [ ] Check Render logs for errors
- [ ] Test NCBA API directly

---

## 💡 RECOMMENDATIONS

### Immediate Actions:
1. **Verify NCBA credentials** on Render (5 min)
2. **Test with small amount** (KES 10) (10 min)
3. **Check callback logs** in Render (5 min)

### Long-term Improvements:
1. Add payment retry mechanism
2. Implement payment timeout handling
3. Add payment status polling
4. Set up payment monitoring/alerts
5. Add fallback to alternative payment method

---

## 📞 SUPPORT

### NCBA Support:
- Email: support@ncbagroup.com
- Phone: +254 711 056 000

### Safaricom M-Pesa Support:
- Email: apisupport@safaricom.co.ke
- Portal: https://developer.safaricom.co.ke

---

## 🚨 EMERGENCY FALLBACK

If NCBA is completely down:

### Option 1: Manual Payment
1. Client pays to Till number manually
2. Handler confirms payment
3. Manually update order status

### Option 2: Switch to M-Pesa
1. Get M-Pesa credentials
2. Update environment variables
3. Switch payment service
4. Redeploy

### Option 3: Use PayPal (International)
- File exists: `orders/paypal_payment_admin.py`
- Needs PayPal credentials
- Good for international clients

---

## ✅ SUMMARY

**Current System:** NCBA Till API (STK Push)
**Status:** Fully implemented ✅
**Fix Time:** 30 min - 2 hours
**Alternative:** M-Pesa Daraja (2-4 hours)

**Most Likely Issue:** Missing NCBA credentials on Render

**Quick Fix:** Add credentials to Render environment variables and redeploy.
