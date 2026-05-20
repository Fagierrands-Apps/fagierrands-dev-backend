# SWAGGER TESTING GUIDE - ERRAND LIFECYCLE

## Access Swagger UI
**URL:** `http://localhost:8000/swagger/` or `http://your-domain/swagger/`

---

## TEST SEQUENCE

### 1. REGISTER USER (Client)
**Endpoint:** `POST /api/accounts/register/`
**Body:**
```json
{
  "username": "testclient",
  "email": "client@test.com",
  "phone_number": "+254712345678",
  "password": "Test@1234",
  "password2": "Test@1234",
  "user_type": "client",
  "first_name": "Test",
  "last_name": "Client"
}
```
**Expected Response:**
```json
{
  "message": "Registration successful. OTP sent to your phone number.",
  "phone_number": "+254712345678",
  "next_step": "verify_phone"
}
```

---

### 2. VERIFY PHONE
**Endpoint:** `POST /api/accounts/verify-phone/`
**Body:**
```json
{
  "phone_number": "+254712345678",
  "otp": "123456"
}
```
**Expected Response:**
```json
{
  "message": "Phone verified successfully",
  "user": {...},
  "access": "eyJ0eXAiOiJKV1Qi...",
  "refresh": "eyJ0eXAiOiJKV1Qi..."
}
```
**Save the `access` token for next requests!**

---

### 3. REGISTER RIDER
**Endpoint:** `POST /api/accounts/register/`
**Body:**
```json
{
  "username": "testrider",
  "email": "rider@test.com",
  "phone_number": "+254722334455",
  "password": "Test@1234",
  "password2": "Test@1234",
  "user_type": "assistant",
  "first_name": "Test",
  "last_name": "Rider"
}
```
Then verify with OTP (same as step 2)

---

### 4. CREATE DRAFT ERRAND (Client Token)
**Endpoint:** `POST /api/orders/errands/draft/`
**Authorization:** Bearer {client_access_token}
**Body:**
```json
{
  "order_type_id": 1,
  "title": "Package Delivery",
  "description": "Deliver documents",
  "pickup_address": "Westlands Mall",
  "delivery_address": "Yaya Centre",
  "pickup_latitude": -1.286389,
  "pickup_longitude": 36.817223,
  "delivery_latitude": -1.292066,
  "delivery_longitude": 36.821945,
  "distance": 5.2
}
```
**Expected Response:**
```json
{
  "order_id": 13,
  "status": "draft",
  "pricing_breakdown": {...},
  "next_step": "Upload images and add receiver contact info"
}
```
**Save the `order_id`!**

---

### 5. ADD RECEIVER INFO (Client Token)
**Endpoint:** `POST /api/orders/errands/{order_id}/receiver-info/`
**Authorization:** Bearer {client_access_token}
**Body:**
```json
{
  "recipient_name": "Jane Doe",
  "contact_number": "+254733445566",
  "estimated_value": 5000
}
```

---

### 6. CONFIRM ERRAND (Client Token)
**Endpoint:** `POST /api/orders/errands/{order_id}/confirm/`
**Authorization:** Bearer {client_access_token}
**Body:** None required
**Expected Response:**
```json
{
  "message": "Errand confirmed successfully!",
  "order_id": 13,
  "status": "pending",
  "notifications_sent": true
}
```

---

### 7. RIDER ACCEPTS ORDER (Rider Token)
**Endpoint:** `POST /api/orders/{order_id}/accept/`
**Authorization:** Bearer {rider_access_token}
**Body:** None required
**Expected Response:**
```json
{
  "success": true,
  "message": "Order accepted successfully",
  "order": {
    "id": 13,
    "status": "assigned"
  }
}
```

---

### 8. RIDER STARTS ERRAND (Rider Token)
**Endpoint:** `PUT /api/orders/{order_id}/status/`
**Authorization:** Bearer {rider_access_token}
**Body:**
```json
{
  "status": "in_progress",
  "pickup_latitude": -1.286389,
  "pickup_longitude": 36.817223,
  "pickup_address": "Rider current location"
}
```
**Expected Response:**
```json
{
  "id": 13,
  "status": "in_progress",
  "started_at": "2026-05-20T20:30:00Z"
}
```

---

### 9. RIDER COMPLETES WORK (Rider Token)
**Endpoint:** `PUT /api/orders/{order_id}/status/`
**Authorization:** Bearer {rider_access_token}
**Body:**
```json
{
  "status": "completed"
}
```
**Expected Response:**
```json
{
  "id": 13,
  "status": "payment_pending"
}
```
**Note:** Status automatically changes to `payment_pending` (not `completed`)

---

### 10. CLIENT CONFIRMS & PAYS (Client Token)
**Endpoint:** `PUT /api/orders/{order_id}/status/`
**Authorization:** Bearer {client_access_token}
**Body:**
```json
{
  "status": "completed"
}
```
**Expected Response:**
```json
{
  "id": 13,
  "status": "completed",
  "completed_at": "2026-05-20T20:45:00Z"
}
```

---

## ALTERNATIVE FLOWS

### HANDLER ASSIGNS RIDER (Handler Token)
**Endpoint:** `PUT /api/orders/{order_id}/assign/`
**Authorization:** Bearer {handler_access_token}
**Body:**
```json
{
  "assistant_id": 5
}
```

### CLIENT CANCELS ORDER (Client Token)
**Endpoint:** `PUT /api/orders/{order_id}/status/`
**Authorization:** Bearer {client_access_token}
**Body:**
```json
{
  "status": "cancelled"
}
```

---

## SWAGGER AUTHORIZATION

1. Click **Authorize** button (top right)
2. Enter: `Bearer {your_access_token}`
3. Click **Authorize**
4. Now all requests will include the token

---

## COMMON ISSUES

1. **401 Unauthorized:** Token expired or not set
2. **403 Forbidden:** Wrong user type for action
3. **404 Not Found:** Order doesn't exist or wrong ID
4. **400 Bad Request:** Invalid status transition or missing fields

---

All endpoints now have proper Swagger documentation with request/response examples!
