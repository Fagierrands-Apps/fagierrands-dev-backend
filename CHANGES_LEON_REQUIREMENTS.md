# Changes Made Per Leon's Requirements

**Date**: 2026-05-26  
**Requested by**: Leon (App Developer)

## Summary

Added status polling endpoint for order tracking. Riders register through unified endpoint and use existing assistant verification system.

---

## 1. ✅ Unified Registration Endpoint

### Registration Flow
All users (clients, riders, handlers) use: `POST /api/accounts/register/`

**For Riders**:
```json
{
  "username": "rider123",
  "email": "rider@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+254712345678",
  "user_type": "assistant"
}
```

Then verify phone: `POST /api/accounts/verify-phone/`

Riders get verified through existing assistant verification system at: `POST /api/accounts/assistant/verify/`

---

## 2. ✅ Status Polling Endpoint

### Endpoint
`GET /api/orders/{order_id}/status/`

**Authentication**: Required (Bearer token)

**Response (Pending)**:
```json
{
  "order_id": 123,
  "status": "pending",
  "created_at": "2026-05-26T10:30:00Z",
  "updated_at": "2026-05-26T10:30:00Z"
}
```

**Response (Assigned - with rider details)**:
```json
{
  "order_id": 123,
  "status": "assigned",
  "created_at": "2026-05-26T10:30:00Z",
  "updated_at": "2026-05-26T10:35:00Z",
  "assigned_at": "2026-05-26T10:35:00Z",
  "rider": {
    "id": 45,
    "name": "John Doe",
    "phone": "+254712345678",
    "profile_picture": "https://...",
    "rating": 4.5
  }
}
```

### Usage in App
```javascript
// Poll every 5 seconds until rider is assigned
const pollOrderStatus = async (orderId) => {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/orders/${orderId}/status/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    if (data.status === 'assigned' && data.rider) {
      clearInterval(interval);
      showRiderDetails(data.rider);
    }
  }, 5000);
};
```

---

## 3. Files Modified

### orders/views.py
- Added `OrderStatusPollingView` class

### orders/urls.py
- Added `path('<int:order_id>/status/', OrderStatusPollingView.as_view())`

---

## 4. Testing

### Test Registration
```bash
# Register rider
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_rider",
    "email": "rider@test.com",
    "password": "TestPass123!",
    "password2": "TestPass123!",
    "first_name": "Test",
    "last_name": "Rider",
    "phone_number": "+254712345678",
    "user_type": "assistant"
  }'

# Verify phone
curl -X POST http://localhost:8000/api/accounts/verify-phone/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+254712345678",
    "otp": "123456"
  }'
```

### Test Status Polling
```bash
curl -X GET http://localhost:8000/api/orders/123/status/ \
  -H "Authorization: Bearer <token>"
```

---

**Built with ❤️ for FagiErrands**
