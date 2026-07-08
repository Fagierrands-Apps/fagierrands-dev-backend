# NCBA Payment System - Development Sync Plan

## 📊 Current Status Analysis

### ✅ Production (fagierrandsbackup) - WORKING
- NCBA credentials configured in environment
- STK Push working correctly
- Payment flow tested and operational
- Enhanced error handling and logging
- Credential validation in place

### ⚠️ Development (fagierrands-dev-backend) - NEEDS SYNC
- NCBA code exists but credentials missing
- Settings configured but no environment variables
- Less robust error handling
- Missing credential validation

---

## 🎯 Sync Plan

### Phase 1: Environment Configuration (5 min)
**Priority: CRITICAL**

#### 1.1 Add NCBA Credentials to `.env`
```bash
# Add to /home/fagitone/Documents/GitHub/fagierrands-dev-backend/.env

# NCBA Till API Configuration
NCBA_USERNAME=Errand@123
NCBA_PASSWORD=9Y7a24B5TNxxKimfnGz9MTbdn960JY57ASC/r6KOCQNnR220v52od6a2ajgEaipL
NCBA_PAYBILL_NO=880100
NCBA_TILL_NO=852054
NCBA_TRANSACTION_TYPE=CustomerPayBillOnline
NCBA_USE_TILL_AS_ACCOUNT=False
```

**Files to modify:**
- `/home/fagitone/Documents/GitHub/fagierrands-dev-backend/.env`

---

### Phase 2: Sync NCBA Service (10 min)
**Priority: HIGH**

#### 2.1 Update `ncba_service.py` with Production Version
**Changes needed:**
- Add credential validation in `get_access_token()`
- Improve error messages with actionable guidance
- Add 401 Unauthorized handling
- Adjust token cache timeout (900s buffer vs 60s)
- Better logging for debugging

**Key improvements from production:**
```python
# Validate credentials before API call
if not self.username or not self.password:
    logger.error("NCBA credentials not configured")
    raise Exception("NCBA credentials missing. Set NCBA_USERNAME and NCBA_PASSWORD.")

# Handle 401 specifically
if response.status_code == 401:
    logger.error(f"NCBA 401 Unauthorized - Invalid credentials")
    raise Exception("Invalid NCBA credentials. Verify NCBA_USERNAME and NCBA_PASSWORD.")

# Longer cache buffer for stability
cache.set(cache_key, token, expires_in - 900)  # 15 min buffer
```

**Files to modify:**
- `/home/fagitone/Documents/GitHub/fagierrands-dev-backend/orders/ncba_service.py`

---

### Phase 3: Verify URL Configuration (2 min)
**Priority: MEDIUM**

#### 3.1 Confirm NCBA Endpoints
✅ Already configured correctly in `orders/urls.py`:
- `/api/orders/payments/initiate/` - InitiatePaymentView
- `/api/orders/payments/<id>/` - PaymentStatusView
- `/api/orders/payments/<id>/process/` - NCBAPaymentView
- `/api/orders/payments/ncba/callback/` - NCBACallbackView
- `/api/orders/payments/ncba/qr-generate/` - NCBAQRGenerationView
- `/api/orders/payments/<id>/cancel/` - PaymentCancellationView
- `/api/orders/<id>/payment-status/` - OrderPaymentStatusView

**No changes needed** ✅

---

### Phase 4: Testing & Validation (15 min)
**Priority: HIGH**

#### 4.1 Test NCBA Authentication
```bash
cd /home/fagitone/Documents/GitHub/fagierrands-dev-backend
python manage.py shell
```

```python
from orders.ncba_service import NCBAService

# Initialize service
service = NCBAService()

# Verify credentials loaded
print(f"Username: {service.username}")
print(f"Password: {'*' * 10}{service.password[-10:]}")
print(f"Till No: {service.till_no}")
print(f"Paybill: {service.paybill_no}")

# Test authentication
try:
    token = service.get_access_token()
    print(f"✅ SUCCESS: Token obtained: {token[:30]}...")
except Exception as e:
    print(f"❌ FAILED: {str(e)}")
```

#### 4.2 Test STK Push (Optional - requires real phone)
```python
# Test STK push with a test amount
result = service.initiate_stk_push(
    phone_number="254712345678",  # Replace with test number
    amount=10,
    account_no="TEST-001"
)
print(f"STK Push Result: {result}")
```

#### 4.3 Test Payment Flow via API
```bash
# Create test order and payment
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

---

## 📋 Implementation Checklist

### Pre-Implementation
- [ ] Backup current `.env` file
- [ ] Backup current `ncba_service.py`
- [ ] Ensure development server is stopped

### Phase 1: Environment
- [ ] Add NCBA credentials to `.env`
- [ ] Verify no syntax errors in `.env`
- [ ] Restart development server
- [ ] Check logs for NCBA settings loaded

### Phase 2: Code Sync
- [ ] Update `ncba_service.py` with production version
- [ ] Review changes (credential validation, error handling)
- [ ] Test import: `from orders.ncba_service import NCBAService`

### Phase 3: Verification
- [ ] URLs already configured ✅
- [ ] No changes needed

### Phase 4: Testing
- [ ] Test authentication (get_access_token)
- [ ] Test STK push (optional)
- [ ] Test full payment flow
- [ ] Check logs for errors
- [ ] Verify callback URL accessible

---

## 🔧 Quick Commands

### Start Development Server
```bash
cd /home/fagitone/Documents/GitHub/fagierrands-dev-backend
python manage.py runserver
```

### Check NCBA Configuration
```bash
python manage.py shell -c "from django.conf import settings; print(f'NCBA User: {settings.NCBA_USERNAME}'); print(f'NCBA Till: {settings.NCBA_TILL_NO}')"
```

### View Logs
```bash
tail -f logs/django.log  # If logging to file
# OR check console output
```

---

## 🚨 Troubleshooting

### Issue: "NCBA credentials not configured"
**Solution:** Verify `.env` has NCBA_USERNAME and NCBA_PASSWORD

### Issue: "401 Unauthorized"
**Solution:** 
1. Check credentials are correct
2. Verify no extra spaces in `.env`
3. Restart server after adding credentials

### Issue: "Token request timed out"
**Solution:**
1. Check internet connection
2. Verify NCBA API is accessible: `curl https://c2bapis.ncbagroup.com`
3. Check firewall settings

### Issue: STK Push not received
**Solution:**
1. Verify phone number format (254XXXXXXXXX)
2. Check NCBA_TILL_NO is correct
3. Verify callback URL is accessible
4. Check NCBA dashboard for transaction status

---

## 📝 Key Differences: Production vs Development

| Feature | Production | Development (Before) | Action |
|---------|-----------|---------------------|--------|
| Credentials | ✅ Set | ❌ Missing | Add to .env |
| Validation | ✅ Yes | ❌ No | Sync code |
| Error Handling | ✅ Enhanced | ⚠️ Basic | Sync code |
| 401 Handling | ✅ Specific | ❌ Generic | Sync code |
| Cache Timeout | 900s buffer | 60s buffer | Sync code |
| Logging | ✅ Detailed | ⚠️ Basic | Sync code |

---

## ⏱️ Estimated Time

- **Phase 1 (Environment):** 5 minutes
- **Phase 2 (Code Sync):** 10 minutes
- **Phase 3 (Verification):** 2 minutes
- **Phase 4 (Testing):** 15 minutes

**Total:** ~30 minutes

---

## 🎯 Success Criteria

✅ NCBA credentials loaded from environment
✅ Authentication successful (token obtained)
✅ STK Push can be initiated
✅ Payment status can be queried
✅ Callback endpoint accessible
✅ No errors in logs
✅ Full payment flow works end-to-end

---

## 📚 Related Documentation

- Production NCBA docs: `/home/fagitone/Documents/GitHub/fagierrandsbackup/NCBA_*.md`
- NCBA API Guide: `orders/README_NCBA_API.md`
- Credentials: `/home/fagitone/Documents/GitHub/fagierrandsbackup/NCBA_CREDENTIALS_FOUND.md`

---

**Created:** 2026-05-29
**Status:** Ready for Implementation
**Priority:** HIGH - Required for payment functionality
