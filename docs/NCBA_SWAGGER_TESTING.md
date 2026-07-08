# Testing NCBA STK Push via Swagger

## ✅ Yes, You Can Test NCBA Payments Through Swagger!

Your development environment has Swagger UI configured and the NCBA payment endpoints are exposed.

---

## 🌐 Access Swagger UI

**URLs available:**
- `http://localhost:8000/swagger/`
- `http://localhost:8000/api/docs/`
- `http://localhost:8000/redoc/` (alternative documentation)

---

## 🔐 Prerequisites

1. **Add environment variables first:**
   ```bash
   export NCBA_USERNAME="Errand@123"
   export NCBA_PASSWORD="9Y7a24B5TNxxKimfnGz9MTbdn960JY57ASC/r6KOCQNnR220v52od6a2ajgEaipL"
   export NCBA_TILL_NO="852054"
   ```

2. **Start development server:**
   ```bash
   cd /home/fagitone/Documents/GitHub/fagierrands-dev-backend
   python manage.py runserver
   ```

3. **Get authentication token:**
   - Login via `/api/accounts/login/` endpoint
   - Copy the JWT token from response

---

## 📱 Test NCBA STK Push via Swagger

### Step 1: Authenticate in Swagger
1. Open `http://localhost:8000/swagger/`
2. Click **"Authorize"** button (top right)
3. Enter: `Bearer YOUR_JWT_TOKEN`
4. Click **"Authorize"** then **"Close"**

### Step 2: Create Test Order (if needed)
Navigate to **orders** section and create an order first, or use existing order ID.

### Step 3: Initiate NCBA Payment
1. Find **`POST /api/orders/payments/initiate/`** endpoint
2. Click **"Try it out"**
3. Enter request body:
   ```json
   {
     "order": 1,
     "amount": 10,
     "payment_method": "ncba",
     "phone_number": "0712345678"
   }
   ```
4. Click **"Execute"**

### Step 4: Check Response
**Success response (201):**
```json
{
  "payment_id": 123,
  "transaction_reference": "PAY-xxx",
  "amount": 10.0,
  "payment_method": "ncba",
  "stk_pushed": true,
  "message": "NCBA payment initiated successfully. Please check your phone for the payment prompt.",
  "stk_data": {
    "transaction_id": "ws_CO_xxx",
    "reference_id": "xxx",
    "customer_message": "Please check your phone",
    "paybill": "880100",
    "account": "852054"
  }
}
```

**Your phone will receive STK push prompt!**

---

## 🧪 Available NCBA Endpoints in Swagger

### 1. **Initiate Payment** (Triggers STK Push)
```
POST /api/orders/payments/initiate/
```
**Body:**
```json
{
  "order": 1,
  "amount": 100,
  "payment_method": "ncba",
  "phone_number": "254712345678"
}
```

### 2. **Check Payment Status**
```
GET /api/orders/payments/{payment_id}/
```
**Response:**
```json
{
  "id": 123,
  "status": "completed",
  "amount": "100.00",
  "payment_method": "ncba"
}
```

### 3. **Process Payment** (Manual STK Push)
```
POST /api/orders/payments/{payment_id}/process/
```
Use this if auto STK push failed.

### 4. **Check Order Payment Status**
```
GET /api/orders/{order_id}/payment-status/
```
**Response:**
```json
{
  "order_id": 1,
  "order_status": "completed",
  "has_payment": true,
  "payment": {
    "id": 123,
    "status": "completed",
    "amount": "100.00"
  }
}
```

### 5. **Generate QR Code**
```
POST /api/orders/payments/ncba/qr-generate/
```
**Body:**
```json
{
  "amount": 100,
  "order_id": 1
}
```

### 6. **Cancel Payment**
```
POST /api/orders/payments/{payment_id}/cancel/
```

---

## 📝 Testing Workflow

### Complete Test Flow:
1. **Login** → Get JWT token
2. **Authorize** in Swagger with token
3. **Create Order** (if needed)
4. **Initiate Payment** → STK push sent to phone
5. **Enter PIN** on your phone
6. **Check Status** → Should show "completed"

---

## 🔍 Troubleshooting

### Issue: "NCBA credentials not configured"
**Solution:** Add environment variables before starting server

### Issue: "401 Unauthorized" in Swagger
**Solution:** 
1. Get fresh JWT token from login endpoint
2. Click "Authorize" button
3. Enter: `Bearer YOUR_TOKEN` (with space after Bearer)

### Issue: STK push not received
**Solution:**
1. Verify phone number format: `254712345678`
2. Check NCBA_TILL_NO is set: `852054`
3. Ensure phone has network coverage

### Issue: "Payment not found"
**Solution:** Use correct payment_id from initiate response

---

## 💡 Pro Tips

1. **Use small amounts for testing:** Start with 10 KES
2. **Test phone format:** Both `0712345678` and `254712345678` work
3. **Check logs:** Terminal shows detailed NCBA API responses
4. **Polling:** Frontend should poll `/payment-status/` every 3 seconds
5. **Timeout:** STK push expires after 60 seconds

---

## 🎯 Quick Test Script

If you prefer command line over Swagger:

```bash
# 1. Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your_user","password":"your_pass"}' \
  | jq -r '.access')

# 2. Initiate payment
curl -X POST http://localhost:8000/api/orders/payments/initiate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order": 1,
    "amount": 10,
    "payment_method": "ncba",
    "phone_number": "0712345678"
  }'
```

---

## ✅ Expected Behavior

1. **Immediate response** with payment_id and transaction_id
2. **STK push** appears on phone within 5 seconds
3. **Enter PIN** on phone
4. **Payment completes** within 10-30 seconds
5. **Status updates** to "completed"
6. **Order status** changes to "completed"

---

## 📚 Related Documentation

- **Full Setup:** `NCBA_ENVIRONMENT_SETUP.md`
- **Verification:** Run `python verify_ncba.py`
- **API Details:** `orders/README_NCBA_API.md`

---

**Ready to test?** 
1. Add environment variables
2. Start server: `python manage.py runserver`
3. Open: `http://localhost:8000/swagger/`
4. Test away! 🚀
