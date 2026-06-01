# Quick Guide: Test NCBA STK Push in Swagger (You're Logged In!)

## 🎯 You're Ready! Here's What to Do:

### Step 1: Find the Payment Endpoint
Look for: **`POST /api/orders/payments/initiate/`**
- It's under the **orders** section
- Click **"Try it out"**

### Step 2: Fill the Request Body
```json
{
  "order": 1,
  "amount": 10,
  "payment_method": "ncba",
  "phone_number": "0712345678"
}
```

**Replace:**
- `"order": 1` → Your actual order ID
- `"phone_number": "0712345678"` → Your actual phone number

### Step 3: Click "Execute"

### Step 4: Check Your Phone!
You should receive an STK push prompt within 5 seconds.

---

## ✅ What You'll See

### In Swagger Response (201 Created):
```json
{
  "payment_id": 123,
  "stk_pushed": true,
  "message": "NCBA payment initiated successfully. Please check your phone for the payment prompt.",
  "stk_data": {
    "transaction_id": "ws_CO_xxx",
    "paybill": "880100",
    "account": "852054"
  }
}
```

### On Your Phone:
```
NCBA Bank
Enter PIN to pay KES 10.00
to 880100
Account: 852054
```

---

## 🔍 Check Payment Status

After entering PIN, check status:

**Endpoint:** `GET /api/orders/payments/{payment_id}/`
- Use the `payment_id` from the response above
- Click "Try it out"
- Enter the payment_id
- Click "Execute"

**Response:**
```json
{
  "id": 123,
  "status": "completed",  // ✅ Success!
  "amount": "10.00"
}
```

---

## ⚠️ If STK Push Doesn't Work

### Check Environment Variables:
```bash
# In terminal where server is running:
echo $NCBA_USERNAME
echo $NCBA_TILL_NO
```

Should show:
```
Errand@123
852054
```

If empty, add them:
```bash
export NCBA_USERNAME="Errand@123"
export NCBA_PASSWORD="9Y7a24B5TNxxKimfnGz9MTbdn960JY57ASC/r6KOCQNnR220v52od6a2ajgEaipL"
export NCBA_TILL_NO="852054"

# Restart server
python manage.py runserver
```

---

## 📱 Phone Number Formats (All Work)

- `0712345678` ✅
- `254712345678` ✅
- `+254712345678` ✅
- `712345678` ✅

The system auto-formats to `254712345678`

---

## 🎯 Quick Test Checklist

- [ ] Logged into Swagger ✅ (You're here!)
- [ ] Environment variables set
- [ ] Have valid order ID
- [ ] Phone number ready
- [ ] Click "Try it out" on `/payments/initiate/`
- [ ] Enter request body
- [ ] Click "Execute"
- [ ] Check phone for STK push
- [ ] Enter PIN
- [ ] Verify payment status

---

**Ready? Go to Swagger and try it now!** 🚀
