# FagiErrands Handler Android App — Backend Reference

This document is the single source of truth for building the Handler Android app.
**Do not modify the backend.** Everything the app needs already exists.

---

## 1. Base URLs

| Environment | URL |
|---|---|
| Production | `https://api.errandserver.fagierrands.com/api` |
| Dev (cPanel) | `https://dev.fagierrands.com/api` |
| Local | `http://localhost:8000/api` |

---

## 2. Authentication

### Login
```
POST /accounts/login/
Content-Type: application/json

Body: { "username": "254712345678", "password": "yourpassword" }

Response 200:
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "user": {
    "id": 1,
    "username": "254712345678",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "254712345678",
    "user_type": "handler",
    "email": "john@example.com"
  }
}
```

### Refresh Token
```
POST /accounts/token/refresh/
Body: { "refresh": "<refresh_token>" }
Response 200: { "access": "<new_access_token>" }
```

### Logout
```
POST /accounts/logout   (no trailing slash — mobile compatibility)
Header: Authorization: Bearer <access_token>
Body: { "refresh": "<refresh_token>" }
```

### Auth Rules
- All protected endpoints require: `Authorization: Bearer <access_token>`
- On 401: auto-refresh once using refresh token, retry, then force logout
- Store tokens in EncryptedSharedPreferences
- Phone numbers are stored as `254XXXXXXXXX` (no + prefix, no leading 0)

---

## 3. User Roles

| user_type | Description |
|---|---|
| `user` | Client placing orders |
| `assistant` | Rider fulfilling deliveries |
| `handler` | Dispatcher (this app's user) |
| `admin` | Platform admin |

Handler endpoints check `user_type in ['handler', 'admin']` — both work.

---

## 4. Order Endpoints (Handler)

### Get Pending Orders (POLL THIS)
```
GET /orders/handler/pending/
Header: Authorization: Bearer <token>

Response 200: [ ...Order objects ]
```
Poll every 30 seconds. This is the core feed.

### Get All Orders (with filters)
```
GET /orders/handler/all/
Query params:
  ?status=Pending|Assigned|InTransit|PaymentPending|Completed|Cancelled
  ?search=<order_number or client name>
  ?client_id=<user_id>

Response 200: [ ...Order objects ]
```

### Get Order Stats
```
GET /orders/stats/
Response 200:
{
  "total_orders": 120,
  "pending_orders": 5,
  "assigned_orders": 3,
  "in_progress_orders": 2,
  "completed_orders": 100,
  "cancelled_orders": 10,
  "total_revenue": 45000.00
}
```

### Assign Order to Rider
```
POST /orders/handler/<order_id>/assign/
Body: { "assistant_id": 42 }

Response 200:
{
  "message": "Order assigned successfully",
  "order": { ...Order object }
}
```

### Update Order Status
```
PATCH /orders/<order_id>/status/
Body: { "status": "Cancelled" }
```

### Cancel Order
```
POST /accounts/handler/orders/<order_id>/cancel/
Response 200: { "message": "Order cancelled", "order_id": 5 }
```

---

## 5. Client Endpoints (Handler)

### List All Clients
```
GET /accounts/handler/clients/all/
Response 200: [ ...User objects ]
```

### Get Client's Orders
```
GET /accounts/handler/clients/<client_id>/orders/
Response 200: [ ...Order objects ]
```

### Filter Orders by Client Phone
```
GET /orders/?client_phone=254712345678
Response 200: [ ...Order objects ]
```

---

## 6. Rider (Assistant) Endpoints

### List All Riders
```
GET /accounts/assistants/
Response 200: [ ...User objects with user_type="assistant" ]
```

### Rider Availability Stats
```
GET /accounts/assistants/stats/
Response 200:
{
  "total_assistants": 20,
  "verified_assistants": 15,
  "active_assistants": 10
}
```

---

## 7. Data Models

### Order Object
```json
{
  "id": 101,
  "order_number": "ORD-17234567891234",
  "user": { ...User },
  "client": { ...User },
  "assistant": null,
  "order_type": { "id": 1, "name": "Normal Delivery", "code": "parcel" },
  "title": "Deliver package",
  "item_description": "Small box",
  "pickup_address": "Westlands, Nairobi",
  "pickup_lat": -1.2673,
  "pickup_lng": 36.8031,
  "delivery_address": "Karen, Nairobi",
  "delivery_lat": -1.3192,
  "delivery_lng": 36.7128,
  "receiver_name": "Jane Doe",
  "receiver_phone": "254798765432",
  "distance_km": "5.20",
  "base_price": "200.00",
  "total_price": "200.00",
  "payment_method": "mpesa",
  "payment_status": "pending",
  "status": "Pending",
  "created_at": "2026-07-16T08:00:00+03:00",
  "assigned_at": null,
  "delivered_at": null,
  "cancelled_at": null,
  "images": []
}
```

### User Object
```json
{
  "id": 5,
  "username": "254712345678",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone_number": "254712345678",
  "user_type": "assistant",
  "is_verified": true,
  "is_active": true
}
```

### Order Status Flow
```
Draft → Pending → Assigned → InTransit → PaymentPending → Completed
                                                         ↘ Cancelled (any stage)
```

---

## 8. Order Types

| id | name | code | Pricing |
|---|---|---|---|
| 1 | Normal Delivery | `parcel` | KES 200 flat ≤7.5km, +KES 23/km after |
| 2 | Cargo | `cargo` | KES 500 flat ≤7.5km, +KES 28/km after |

---

## 9. Pricing Calculation (read-only reference)

```
POST /orders/calculate-pricing/
Body: {
  "order_type": "parcel",   // or "cargo"
  "distance_km": 10.5
}
Response: {
  "base_fee": 200,
  "distance_fee": 69.0,
  "total": 269.0,
  "distance_km": 10.5
}
```

---

## 10. Complete URL Map (Handler-relevant only)

```
# Auth
POST   /accounts/login/
POST   /accounts/logout
POST   /accounts/token/refresh/

# Orders
GET    /orders/handler/pending/          ← POLL THIS
GET    /orders/handler/all/
GET    /orders/stats/
POST   /orders/handler/<id>/assign/
PATCH  /orders/<id>/status/

# Clients
GET    /accounts/handler/clients/all/
GET    /accounts/handler/clients/<id>/orders/
GET    /orders/?client_phone=254XXXXXXXXX

# Riders
GET    /accounts/assistants/
GET    /accounts/assistants/stats/

# Cancel
POST   /accounts/handler/orders/<id>/cancel/
```

---

## 11. Error Response Format

```json
{ "error": "Human readable message" }
{ "detail": "Not found." }
```
HTTP status codes: 200, 201, 400, 401, 403, 404, 500

---

## 12. Important Notes for Android Dev

1. **No trailing slash on logout** — use `/accounts/logout` not `/accounts/logout/`
2. **APPEND_SLASH = False** in Django settings — send URLs exactly as listed above
3. **Phone format** — always send as `254XXXXXXXXX` (no +, no leading 0)
4. **JWT lifetime** — access token: 1 day, refresh token: 7 days
5. **Pagination** — default page size is 20, but handler endpoints return ALL results (no pagination)
6. **CORS** — `https://api.errandserver.fagierrands.com` is whitelisted
7. **Time zone** — all timestamps are `Africa/Nairobi` (UTC+3)
8. **`user` vs `client` field** — Order object has both `user` and `client` fields pointing to the same person. Use `client` first, fall back to `user`
9. **Status case-sensitive** — `Pending`, `Assigned`, `InTransit`, `Completed`, `Cancelled` (capital first letter)
10. **Rider = Assistant** — `user_type="assistant"` is the rider. The field is called `assistant` in Order objects.

---

## 13. Swagger / API Explorer

Live interactive docs (requires running server):
- `https://api.errandserver.fagierrands.com/swagger/`
- `https://api.errandserver.fagierrands.com/redoc/`
