# FagiErrands API — Deep Testing Guide

**Base URL (Render):** `https://<your-render-url>`  
**Swagger UI:** `https://<your-render-url>/swagger/`  
**Admin Panel:** `https://<your-render-url>/admin/`

Use Swagger or Postman. All authenticated endpoints require:
```
Authorization: Bearer <access_token>
```

---

## SETUP — Get Tokens First

Before testing anything, register and login to get tokens.

---

## 1. AUTH — `/api/accounts/`

### 1.1 Register (Client)
```
POST /api/accounts/register/
{
  "email": "testclient@test.com",
  "password": "Test1234!",
  "first_name": "Test",
  "last_name": "Client",
  "phone_number": "+254700000001",
  "user_type": "client"
}
```
**Expect:** `201` — OTP sent to phone

### 1.2 Register (Assistant/Rider)
```
POST /api/accounts/register/
{
  "email": "testrider@test.com",
  "password": "Test1234!",
  "first_name": "Test",
  "last_name": "Rider",
  "phone_number": "+254700000002",
  "user_type": "assistant"
}
```
**Expect:** `201`

### 1.3 Register (Handler)
```
POST /api/accounts/register/
{
  "email": "testhandler@test.com",
  "password": "Test1234!",
  "first_name": "Test",
  "last_name": "Handler",
  "phone_number": "+254700000003",
  "user_type": "handler"
}
```
**Expect:** `201`

### 1.4 Verify Phone (OTP)
```
POST /api/accounts/verify-phone/
{ "phone_number": "+254700000001", "otp": "<otp_from_sms>" }
```
**Expect:** `200`

### 1.5 Resend OTP
```
POST /api/accounts/resend-otp/
{ "phone_number": "+254700000001" }
```
**Expect:** `200`

### 1.6 Login
```
POST /api/accounts/login/
{ "email": "testclient@test.com", "password": "Test1234!" }
```
**Expect:** `200` — returns `access` and `refresh` tokens  
**Save:** `access_token` for all subsequent requests

### 1.7 Token Refresh
```
POST /api/accounts/token/refresh/
{ "refresh": "<refresh_token>" }
```
**Expect:** `200` — new `access` token

### 1.8 Logout
```
POST /api/accounts/logout/
{ "refresh": "<refresh_token>" }
```
**Expect:** `200` — token blacklisted

### 1.9 Get Profile
```
GET /api/accounts/profile/
```
**Expect:** `200` — user profile data

### 1.10 Update Profile
```
PATCH /api/accounts/profile/
{ "first_name": "Updated" }
```
**Expect:** `200`

### 1.11 Change Password
```
POST /api/accounts/change-password/
{ "old_password": "Test1234!", "new_password": "NewPass1234!" }
```
**Expect:** `200`

### 1.12 Password Reset Request
```
POST /api/accounts/password-reset/request/
{ "email": "testclient@test.com" }
```
**Expect:** `200` — reset email sent

### 1.13 Password Reset Confirm
```
POST /api/accounts/password-reset/reset/
{ "token": "<token_from_email>", "new_password": "Reset1234!" }
```
**Expect:** `200`

### 1.14 Get User Detail
```
GET /api/accounts/user/
```
**Expect:** `200`

### 1.15 List All Users (Admin)
```
GET /api/accounts/user/list/
```
**Expect:** `200` — paginated list

---

## 2. ASSISTANT VERIFICATION — `/api/accounts/assistant/`

### 2.1 Submit Verification Docs
```
POST /api/accounts/assistant/verify/
Content-Type: multipart/form-data
{ "id_front": <file>, "id_back": <file>, "selfie": <file> }
```
**Expect:** `201`

### 2.2 Check Verification Status
```
GET /api/accounts/assistant/verification-status/
```
**Expect:** `200` — `pending | approved | rejected`

### 2.3 Assistant Dashboard Stats
```
GET /api/accounts/assistant/dashboard-stats/
```
**Expect:** `200`

### 2.4 Set Availability
```
POST /api/accounts/assistant/availability/
{ "is_available": true }
```
**Expect:** `200`

### 2.5 List All Assistants
```
GET /api/accounts/assistants/
```
**Expect:** `200`

### 2.6 Admin — List Pending Verifications
```
GET /api/accounts/admin/verifications/
```
**Expect:** `200` (admin token required)

### 2.7 Admin — Approve Verification
```
POST /api/accounts/admin/verifications/<id>/update/
{ "status": "approved" }
```
**Expect:** `200`

### 2.8 Admin — Reject Verification
```
POST /api/accounts/admin/verifications/<id>/update/
{ "status": "rejected", "admin_notes": "Documents unclear" }
```
**Expect:** `200`

---

## 3. HANDLER FLOWS — `/api/accounts/handler/`

### 3.1 Handler — Get My Clients
```
GET /api/accounts/handler/clients/
```
**Expect:** `200`

### 3.2 Handler — Get All Clients
```
GET /api/accounts/handler/clients/all/
```
**Expect:** `200`

### 3.3 Handler — Dashboard Stats
```
GET /api/accounts/handler/dashboard-stats/
```
**Expect:** `200`

### 3.4 Handler — Create Order for Client
```
POST /api/accounts/handler/orders/create-for-client/
{
  "client_id": 1,
  "pickup_address": "Nairobi CBD",
  "pickup_lat": -1.2921,
  "pickup_lng": 36.8219,
  "delivery_address": "Westlands",
  "delivery_lat": -1.2676,
  "delivery_lng": 36.8108,
  "order_type": 1
}
```
**Expect:** `201`

### 3.5 Handler — Confirm Order
```
POST /api/accounts/handler/orders/<order_id>/confirm/
```
**Expect:** `200`

### 3.6 Handler — Cancel Order
```
POST /api/accounts/handler/orders/<order_id>/cancel/
```
**Expect:** `200`

### 3.7 Handler — View Client Orders
```
GET /api/accounts/handler/clients/<client_id>/orders/
```
**Expect:** `200`

### 3.8 Admin — Change User Type
```
POST /api/accounts/admin/users/<user_id>/change-type/
{ "user_type": "handler" }
```
**Expect:** `200`

### 3.9 Admin — Assign Account Manager
```
POST /api/accounts/user/<user_id>/assign-account-manager/
{ "manager_id": 2 }
```
**Expect:** `200`

---

## 4. ORDERS — `/api/orders/`

### 4.1 Get Pricing Config
```
GET /api/orders/config/
```
**Expect:** `200` — base prices, per km rates

### 4.2 Calculate Price (Real-time)
```
POST /api/orders/calculate-pricing/
{
  "pickup_latitude": -1.2921,
  "pickup_longitude": 36.8219,
  "delivery_latitude": -1.2676,
  "delivery_longitude": 36.8108,
  "order_type": "parcel"
}
```
**Expect:** `200` — price breakdown

### 4.3 Create Order (Direct)
```
POST /api/orders/create/
{
  "pickup_address": "Nairobi CBD",
  "pickup_lat": -1.2921,
  "pickup_lng": 36.8219,
  "delivery_address": "Westlands",
  "delivery_lat": -1.2676,
  "delivery_lng": 36.8108,
  "order_type": 1,
  "payment_method": "mpesa"
}
```
**Expect:** `201` — order with `order_number`

### 4.4 List My Orders (Client)
```
GET /api/orders/my-orders/
```
**Expect:** `200`

### 4.5 Order Detail
```
GET /api/orders/<order_id>/
```
**Expect:** `200`

### 4.6 Cancel Order
```
POST /api/orders/<order_id>/cancel/
```
**Expect:** `200`

### 4.7 Order Tracking
```
GET /api/orders/<order_id>/tracking/
```
**Expect:** `200`

### 4.8 Rate Order
```
POST /api/orders/<order_id>/rate/
{ "rating": 5, "comment": "Great service" }
```
**Expect:** `201`

### 4.9 Order Stats
```
GET /api/orders/stats/
```
**Expect:** `200`

---

## 5. ERRAND FLOW (Step-by-step) — `/api/orders/errands/`

### 5.1 Create Draft
```
POST /api/orders/errands/draft/
{
  "pickup_address": "Nairobi CBD",
  "pickup_lat": -1.2921,
  "pickup_lng": 36.8219,
  "delivery_address": "Westlands",
  "delivery_lat": -1.2676,
  "delivery_lng": 36.8108,
  "order_type": 1
}
```
**Expect:** `201` — `status: Draft`

### 5.2 Upload Image
```
POST /api/orders/errands/<order_id>/upload-image/
Content-Type: multipart/form-data
{ "image": <file> }
```
**Expect:** `200`

### 5.3 Add Receiver Info
```
POST /api/orders/errands/<order_id>/receiver-info/
{
  "receiver_name": "John Doe",
  "receiver_phone": "+254700000099"
}
```
**Expect:** `200`

### 5.4 Calculate Price
```
POST /api/orders/errands/calculate-price/
{ "order_id": <order_id> }
```
**Expect:** `200` — price breakdown

### 5.5 Confirm Order
```
POST /api/orders/errands/<order_id>/confirm/
```
**Expect:** `200` — `status: Pending`

### 5.6 Get Errand Detail
```
GET /api/orders/errands/<order_id>/
```
**Expect:** `200`

---

## 6. HANDLER ORDER MANAGEMENT — `/api/orders/handler/`

### 6.1 All Orders
```
GET /api/orders/handler/all/
```
**Expect:** `200`

### 6.2 Pending Orders
```
GET /api/orders/handler/pending/
```
**Expect:** `200` — only `Pending` status orders

### 6.3 Assign Order to Rider
```
POST /api/orders/handler/<order_id>/assign/
{ "assistant_id": <rider_user_id> }
```
**Expect:** `200` — `status: Assigned`

### 6.4 Update Order Status
```
PATCH /api/orders/<order_id>/status/
{ "status": "InTransit" }
```
**Expect:** `200`

### 6.5 List All Orders (Admin view)
```
GET /api/orders/
```
**Expect:** `200`

### 6.6 Assign Order (Admin)
```
POST /api/orders/<order_id>/assign/
{ "assistant_id": <rider_user_id> }
```
**Expect:** `200`

---

## 7. RIDER/ASSISTANT FLOWS — `/api/orders/assistant/`

### 7.1 Available Orders (Rider sees unassigned)
```
GET /api/orders/assistant/available/
```
**Expect:** `200`

### 7.2 My Orders
```
GET /api/orders/assistant/my-orders/
```
**Expect:** `200`

### 7.3 Order History
```
GET /api/orders/assistant/history/
```
**Expect:** `200`

### 7.4 Accept Order
```
POST /api/orders/assistant/<order_id>/accept/
```
**Expect:** `200`

### 7.5 Start Delivery
```
POST /api/orders/assistant/<order_id>/start/
```
**Expect:** `200` — `status: InTransit`

### 7.6 Update Status
```
POST /api/orders/assistant/<order_id>/update-status/
{ "status": "InTransit" }
```
**Expect:** `200`

### 7.7 Complete Delivery
```
POST /api/orders/assistant/<order_id>/complete/
```
**Expect:** `200` — `status: Completed`

### 7.8 Available Orders (old endpoint)
```
GET /api/orders/available/
```
**Expect:** `200`

### 7.9 Accept Order (old endpoint)
```
POST /api/orders/<order_id>/accept/
```
**Expect:** `200`

### 7.10 My Deliveries (old endpoint)
```
GET /api/orders/my-deliveries/
```
**Expect:** `200`

### 7.11 Rider Assignment Info
```
GET /api/orders/<order_id>/rider-assignment/
```
**Expect:** `200`

---

## 8. PAYMENTS — `/api/orders/payments/`

### 8.1 Initiate Payment
```
POST /api/orders/payments/initiate/
{
  "order_id": <order_id>,
  "phone_number": "+254700000001",
  "amount": 500
}
```
**Expect:** `200` — STK push triggered

### 8.2 Payment Detail
```
GET /api/orders/payments/<payment_id>/
```
**Expect:** `200`

### 8.3 Process Payment
```
POST /api/orders/payments/<payment_id>/process/
```
**Expect:** `200`

### 8.4 NCBA Callback (Webhook — simulate)
```
POST /api/orders/payments/ncba/callback/
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "xxx",
      "CheckoutRequestID": "xxx",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully."
    }
  }
}
```
**Expect:** `200`

### 8.5 Generate QR Code
```
POST /api/orders/payments/ncba/qr-generate/
{ "order_id": <order_id> }
```
**Expect:** `200` — QR data

### 8.6 Order Payment Status
```
GET /api/orders/<order_id>/payment-status/
```
**Expect:** `200` — `pending | paid | failed`

---

## 9. SOS ALERTS — `/api/orders/sos-alerts/`

### 9.1 List SOS Alerts (Admin/Handler)
```
GET /api/orders/sos-alerts/
```
**Expect:** `200`

### 9.2 Resolve SOS Alert
```
POST /api/orders/sos-alerts/<alert_id>/resolve/
```
**Expect:** `200`

---

## 10. LOCATIONS — `/api/locations/`

### 10.1 Autocomplete
```
GET /api/locations/autocomplete/?q=Nairobi
```
**Expect:** `200` — list of place suggestions

### 10.2 Reverse Geocode
```
GET /api/locations/reverse-geocode/?lat=-1.2921&lng=36.8219
```
**Expect:** `200` — address string

### 10.3 Calculate Distance
```
POST /api/locations/calculate-distance/
{
  "pickup_lat": -1.2921, "pickup_lng": 36.8219,
  "delivery_lat": -1.2676, "delivery_lng": 36.8108
}
```
**Expect:** `200` — `distance_km`

### 10.4 Map Config
```
GET /api/locations/map-config/
```
**Expect:** `200` — Google Maps API key (public)

### 10.5 Save Location
```
POST /api/locations/saved/
{ "name": "Home", "address": "Nairobi", "lat": -1.2921, "lng": 36.8219 }
```
**Expect:** `201`

### 10.6 List Saved Locations
```
GET /api/locations/saved/
```
**Expect:** `200`

### 10.7 Delete Saved Location
```
DELETE /api/locations/saved/<location_id>/
```
**Expect:** `204`

### 10.8 Update Current Location
```
POST /api/locations/update-current/
{ "lat": -1.2921, "lng": 36.8219 }
```
**Expect:** `200`

### 10.9 Get Rider Location
```
GET /api/locations/rider/<rider_id>/
```
**Expect:** `200`

---

## 11. NOTIFICATIONS — `/api/notifications/`

### 11.1 List Notifications
```
GET /api/notifications/
```
**Expect:** `200`

### 11.2 Unread Count
```
GET /api/notifications/unread-count/
```
**Expect:** `200` — `{ "count": N }`

### 11.3 Mark as Read
```
POST /api/notifications/<notification_id>/read/
```
**Expect:** `200`

### 11.4 Mark All Read
```
POST /api/notifications/mark-all-read/
```
**Expect:** `200`

### 11.5 Delete Notification
```
DELETE /api/notifications/<notification_id>/delete/
```
**Expect:** `204`

### 11.6 Delete All
```
DELETE /api/notifications/delete-all/
```
**Expect:** `200`

### 11.7 Register Push Token
```
POST /api/notifications/register-token/
{ "token": "<fcm_device_token>", "device_type": "android" }
```
**Expect:** `201`

### 11.8 Unregister Push Token
```
POST /api/notifications/unregister-token/
{ "token": "<fcm_device_token>" }
```
**Expect:** `200`

---

## 12. ADMIN DASHBOARD — `/dashboard/`

### 12.1 Dashboard Stats
```
GET /dashboard/stats/
```
**Expect:** `200`

### 12.2 Handler Stats
```
GET /dashboard/handler-stats/
```
**Expect:** `200`

### 12.3 Overview
```
GET /dashboard/overview/
```
**Expect:** `200`

### 12.4 Live Metrics
```
GET /dashboard/live-metrics/
```
**Expect:** `200`

### 12.5 Calculate Metrics
```
POST /dashboard/calculate-metrics/
```
**Expect:** `200`

### 12.6 All Users
```
GET /dashboard/users/
```
**Expect:** `200`

### 12.7 All Riders
```
GET /dashboard/riders/
```
**Expect:** `200`

### 12.8 All Orders
```
GET /dashboard/orders/
```
**Expect:** `200`

### 12.9 Pending Verifications
```
GET /dashboard/verifications/
```
**Expect:** `200`

### 12.10 Approve Rider
```
POST /dashboard/verifications/<verification_id>/approve/
```
**Expect:** `200`

### 12.11 Reject Rider
```
POST /dashboard/verifications/<verification_id>/reject/
{ "reason": "Invalid documents" }
```
**Expect:** `200`

### 12.12 Suspend User
```
POST /dashboard/users/<user_id>/suspend/
```
**Expect:** `200`

### 12.13 Activate User
```
POST /dashboard/users/<user_id>/activate/
```
**Expect:** `200`

### 12.14 Export Data
```
GET /dashboard/export/
```
**Expect:** `200` — CSV/Excel download

### 12.15 Daily Metrics
```
GET /dashboard/daily-metrics/
GET /dashboard/daily-metrics/time_series/
```
**Expect:** `200`

### 12.16 User Retention
```
GET /dashboard/user-retention/
GET /dashboard/user-retention/cohort_analysis/
```
**Expect:** `200`

### 12.17 Service Performance
```
GET /dashboard/service-performance/
GET /dashboard/service-performance/service_comparison/
```
**Expect:** `200`

### 12.18 Customer Satisfaction
```
GET /dashboard/customer-satisfaction/
GET /dashboard/customer-satisfaction/nps_trend/
GET /dashboard/customer-satisfaction/rating_distribution/
```
**Expect:** `200`

---

## 13. FULL END-TO-END FLOWS

### Flow A — Client Places & Pays for Order
1. Register client → verify phone → login
2. `POST /api/orders/errands/draft/` → get `order_id`
3. `POST /api/orders/errands/<id>/receiver-info/`
4. `POST /api/orders/errands/<id>/confirm/` → status = `Pending`
5. `POST /api/orders/payments/initiate/` → STK push
6. Simulate callback → `POST /api/orders/payments/ncba/callback/`
7. `GET /api/orders/<id>/payment-status/` → `paid`

### Flow B — Handler Assigns Rider
1. Login as handler
2. `GET /api/orders/handler/pending/` → find the order
3. `POST /api/orders/handler/<id>/assign/` with `assistant_id`
4. Order status → `Assigned`

### Flow C — Rider Completes Delivery
1. Login as rider
2. `GET /api/orders/assistant/my-orders/`
3. `POST /api/orders/assistant/<id>/start/` → `InTransit`
4. `POST /api/orders/assistant/<id>/complete/` → `Completed`
5. Client rates: `POST /api/orders/<id>/rate/`

### Flow D — Admin Onboards a Rider
1. Rider registers → submits verification docs
2. Admin: `GET /dashboard/verifications/`
3. Admin: `POST /dashboard/verifications/<id>/approve/`
4. Rider: `GET /api/accounts/assistant/verification-status/` → `approved`
5. Rider: `POST /api/accounts/assistant/availability/` → `is_available: true`

---

## 14. SECURITY TESTS

| Test | How | Expect |
|---|---|---|
| Access protected endpoint without token | `GET /api/orders/` (no header) | `401` |
| Access admin endpoint as client | `GET /dashboard/users/` with client token | `403` |
| Access another user's order | `GET /api/orders/<other_user_order_id>/` | `403` or `404` |
| Use expired token | Use old `access` token after expiry | `401` |
| Use blacklisted refresh token | Logout then try `POST /token/refresh/` | `401` |
| SQL injection in query param | `GET /api/orders/?search=' OR 1=1--` | `200` (safe, no crash) |

---

## 15. ERROR CASE TESTS

| Test | Endpoint | Expect |
|---|---|---|
| Login with wrong password | `POST /api/accounts/login/` | `401` |
| Register duplicate email | `POST /api/accounts/register/` | `400` |
| Register duplicate phone | `POST /api/accounts/register/` | `400` |
| Confirm order that doesn't exist | `POST /api/orders/errands/9999/confirm/` | `404` |
| Initiate payment with 0 amount | `POST /api/orders/payments/initiate/` | `400` |
| Calculate price with missing coords | `POST /api/orders/calculate-pricing/` | `400` |
| Cancel already completed order | `POST /api/orders/<id>/cancel/` | `400` |
| Rider accept already assigned order | `POST /api/orders/assistant/<id>/accept/` | `400` |

---

## 16. RENDER-SPECIFIC CHECKS

After deploying to Render, verify:

- [ ] `GET /` → returns HTML landing page (not 500)
- [ ] `GET /swagger/` → Swagger UI loads
- [ ] `GET /admin/` → Django admin login page loads
- [ ] `GET /api/orders/config/` → returns pricing config (no DB error)
- [ ] Check Render logs for any startup errors
- [ ] Confirm `DEBUG=False` in Render env vars
- [ ] Confirm `ALLOWED_HOSTS` includes the Render domain
- [ ] Confirm `DATABASE_URL` is set (if using PostgreSQL on Render)
- [ ] Run `python manage.py migrate` via Render shell after first deploy
- [ ] Run `python manage.py collectstatic` via Render shell

---

## 17. CHECKLIST BEFORE cPANEL DEPLOY

- [ ] All tests above pass on Render
- [ ] `DEBUG=False` confirmed
- [ ] All security headers active (`SECURE_HSTS_SECONDS`, `SESSION_COOKIE_SECURE`, etc.)
- [ ] `ALLOWED_HOSTS` set to production domain only
- [ ] `NCBA_CALLBACK_URL` points to production domain
- [ ] `BASE_URL` points to production domain
- [ ] Email sending tested (password reset flow)
- [ ] SMS OTP tested (registration flow)
- [ ] Payment callback tested end-to-end
- [ ] No `500` errors in any endpoint
- [ ] Admin panel accessible and functional
