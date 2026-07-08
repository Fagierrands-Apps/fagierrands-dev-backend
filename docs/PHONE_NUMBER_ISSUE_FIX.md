# 🔍 PHONE NUMBER ISSUE - DIAGNOSIS & FIX

## ❌ Problem Identified

You logged in with phone **X**, filled payment form with phone **Y**, but STK push went to phone **X**.

## 🔎 Root Cause

The code is **CORRECT** - it uses `validated_data.get('phone_number')` from your request.

**Possible causes:**

### 1. Frontend Auto-Fill Issue
The frontend might be auto-filling the logged-in user's phone number instead of using the one you typed.

### 2. Request Body Not Sent Correctly
Check what was actually sent in the request body.

---

## ✅ VERIFICATION STEPS

### Step 1: Check What Was Sent
In Swagger, after clicking "Execute", scroll down to see **"Request body"** section.

**It should show:**
```json
{
  "order": 1,
  "amount": 10,
  "payment_method": "ncba",
  "phone_number": "0712345678"  ← YOUR TYPED NUMBER
}
```

### Step 2: Check Server Logs
Look at your terminal where `python manage.py runserver` is running.

**You should see:**
```
Created new NCBA payment: ID=123, Status=pending, Method=ncba, Phone=0712345678
```

**If it shows a different phone number**, then the request body had the wrong number.

---

## 🔧 QUICK FIX TEST

### Test in Swagger with Explicit Phone Number:

1. **Go to:** `POST /api/orders/payments/initiate/`
2. **Click:** "Try it out"
3. **Enter this EXACT JSON:**
   ```json
   {
     "order": 1,
     "amount": 10,
     "payment_method": "ncba",
     "phone_number": "0798765432"
   }
   ```
   *(Use a completely different number)*

4. **Click:** "Execute"
5. **Check:** Which phone gets the STK push?

---

## 📋 Expected Behavior

**Code Flow:**
```
Request → Serializer validates → phone_number saved to Payment model → 
STK push uses payment.phone_number → Correct phone gets prompt
```

**The code at line 1010 in serializers.py:**
```python
phone_number=validated_data.get('phone_number'),  # ✅ Uses YOUR input
```

**The code at line 33 in views_payment_ncba.py:**
```python
phone_number = payment.phone_number  # ✅ Uses saved phone from Payment
```

---

## 🎯 CONFIRMATION TEST

Run this in Django shell to check last payment:

```python
from orders.models import Payment
p = Payment.objects.latest('payment_date')
print(f"Payment Phone: {p.phone_number}")
print(f"Client Phone: {p.client.phone_number if hasattr(p.client, 'phone_number') else 'N/A'}")
```

**If they're the same**, the issue is in the request body, not the code.

---

## ✅ THE CODE IS CORRECT

The backend code correctly:
1. ✅ Takes `phone_number` from request body
2. ✅ Saves it to Payment model
3. ✅ Uses it for STK push

**If wrong number is prompted, the issue is:**
- Frontend sending wrong phone_number in request
- OR Swagger auto-filling from user profile
- OR Request body not matching what you typed

---

## 🔍 DEBUG COMMAND

Check the actual request that was sent:

```bash
# In terminal where server is running, you should see:
# "Created new NCBA payment: ... Phone=XXXXXXXXXX"
```

That log shows what phone number was actually in the request.

---

## 💡 SOLUTION

**If Swagger is auto-filling:**
1. Clear the phone_number field completely
2. Type the new number manually
3. Make sure it's not reverting back
4. Click Execute

**If frontend is the issue:**
- Check frontend code that calls `/payments/initiate/`
- Ensure it sends the phone_number from the form, not from user profile

---

**The backend code is working correctly. The issue is likely in what's being sent to the API.**
