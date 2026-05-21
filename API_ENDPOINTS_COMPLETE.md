# Complete API Endpoints - Categorized

## 1. ONBOARDING & AUTHENTICATION

### Registration
- `POST /api/accounts/register/` - Register new user (client/rider)
- `POST /api/accounts/verify-phone/` - Verify phone with OTP
- `POST /api/accounts/resend-otp/` - Resend OTP code

### Login & Authentication
- `POST /api/accounts/login/` - Login with phone/email and password
- `POST /api/accounts/token/refresh/` - Refresh JWT token
- `POST /api/accounts/logout/` - Logout user

### Password Management
- `POST /api/accounts/password-reset/request/` - Request password reset OTP
- `POST /api/accounts/password-reset/verify/` - Verify OTP and reset password
- `POST /api/accounts/change-password/` - Change password (authenticated)

### Profile Management
- `GET /api/accounts/profile/` - Get user profile
- `PUT /api/accounts/profile/` - Update user profile
- `POST /api/accounts/profile/upload-picture/` - Upload profile picture

### Assistant/Rider Verification
- `POST /api/accounts/assistant/verification/` - Submit verification documents
- `GET /api/accounts/assistant/verification/status/` - Check verification status

---

## 2. ERRAND PLACEMENT (CLIENT)

### Price Calculation
- `POST /api/orders/errands/calculate-price/` - Calculate errand price
- `POST /api/orders/errands/calculate-price-with-route/` - Calculate with route details

### Draft Errand Creation
- `POST /api/orders/errands/draft/` - Create draft errand
- `GET /api/orders/errands/<order_id>/` - Get draft errand details
- `DELETE /api/orders/errands/<order_id>/delete/` - Delete draft errand

### Image Upload
- `POST /api/orders/errands/<order_id>/upload-image/` - Upload errand images

### Receiver Information
- `PUT /api/orders/errands/<order_id>/receiver-info/` - Update receiver details

### Confirm & Place Errand
- `POST /api/orders/errands/<order_id>/confirm/` - Confirm and place errand

---

## 3. ORDER MANAGEMENT (CLIENT)

### View Orders
- `GET /api/orders/` - List all client orders
- `GET /api/orders/<order_id>/` - Get specific order details
- `GET /api/orders/pending/` - Get pending orders

### Order Status
- `GET /api/orders/<order_id>/payment-status/` - Check payment status
- `GET /api/orders/<order_id>/rider-status/` - Check rider assignment status
- `GET /api/orders/<order_id>/rider-details/` - Get assigned rider details

### Order Tracking
- `GET /api/orders/<order_id>/tracking/` - Get order tracking info
- `POST /api/orders/<order_id>/tracking/initialize/` - Initialize tracking

### Order Actions
- `PUT /api/orders/<order_id>/status/` - Update order status
- `POST /api/orders/<order_id>/review/` - Submit order review

---

## 4. HANDLER DASHBOARD

### View Orders
- `GET /api/orders/handler/all/` - Get all orders for handler

### Assign Rider
- `POST /api/orders/<order_id>/assign/` - Assign rider to order

### Quote Management
- `GET /api/orders/handler/quotes/` - View all quotes
- `POST /api/orders/handler/quotes/<quote_id>/review/` - Approve/reject quote

---

## 5. RIDER/ASSISTANT

### Available Orders
- `GET /api/orders/available/` - Get available orders to accept
- `GET /api/orders/assistant/` - Get assigned orders

### Accept Order
- `POST /api/orders/<order_id>/accept/` - Accept an order

### Order Updates
- `PUT /api/orders/<order_id>/status/` - Update order status
- `POST /api/orders/<order_id>/images/` - Upload order images

### Availability
- `POST /api/accounts/assistant/availability/` - Set availability status

---

## 6. PAYMENT

### Initiate Payment
- `POST /api/orders/payments/initiate/` - Initiate payment for order

### Payment Processing
- `POST /api/orders/payments/<payment_id>/process/` - Process NCBA payment
- `POST /api/orders/payments/ncba/qr-generate/` - Generate QR code

### Payment Status
- `GET /api/orders/payments/<payment_id>/` - Get payment status
- `GET /api/orders/<order_id>/payment-status/` - Get order payment status

### Payment Actions
- `POST /api/orders/payments/<payment_id>/cancel/` - Cancel payment

### Webhook
- `POST /api/orders/payments/ncba/callback/` - NCBA payment callback

---

## 7. LOCATIONS & MAPS

### Location Management
- `GET /api/locations/locations/` - List user locations
- `POST /api/locations/locations/` - Add new location
- `GET /api/locations/<location_id>/` - Get location details
- `PUT /api/locations/<location_id>/` - Update location
- `DELETE /api/locations/<location_id>/` - Delete location

### Current Location
- `GET /api/locations/current/` - Get current location
- `PUT /api/locations/current/update/` - Update current location

### Set Default
- `POST /api/locations/<location_id>/set-default/` - Set default location

### Autocomplete & Geocoding
- `GET /api/locations/autocomplete/` - Google Places autocomplete
- `GET /api/locations/reverse-geocode/` - Reverse geocode coordinates

### Distance Calculation
- `POST /api/locations/calculate-distance/` - Calculate distance between points

### Map Configuration
- `GET /api/locations/map-config/` - Get Google Maps API config

---

## 8. NOTIFICATIONS

### Push Notifications
- `POST /api/notifications/register-device/` - Register device for push
- `GET /api/notifications/` - Get user notifications
- `PUT /api/notifications/<notification_id>/read/` - Mark as read

### Broadcast
- `GET /api/notifications/broadcast/` - Get broadcast notifications

---

## 9. HANDYMAN SERVICES

### Service Types
- `GET /api/orders/handyman/service-types/` - List service types

### Create Order
- `POST /api/orders/handyman/orders/` - Create handyman order
- `GET /api/orders/handyman/orders/` - List handyman orders
- `GET /api/orders/handyman/orders/<order_id>/` - Get order details

### Quotes
- `POST /api/orders/handyman/orders/<order_id>/quote/` - Submit quote
- `GET /api/orders/handyman/orders/<order_id>/quotes/` - View quotes
- `POST /api/orders/quotes/<quote_id>/submit/` - Submit quote details
- `POST /api/orders/quotes/<quote_id>/images/` - Upload quote images

### Order Management
- `PUT /api/orders/handyman/orders/<order_id>/status/` - Update status
- `POST /api/orders/handyman/orders/<order_id>/assign/` - Assign service provider
- `POST /api/orders/handyman/orders/<order_id>/images/` - Upload images

### Payment
- `POST /api/orders/handyman/orders/<order_id>/final-payment/` - Process final payment

### Service Provider
- `GET /api/orders/quotes/` - Get my quotes
- `GET /api/orders/service-provider/dashboard/` - Service provider dashboard

---

## 10. BANKING SERVICES

### Banks
- `GET /api/orders/banking/banks/` - List available banks

### Banking Orders
- `POST /api/orders/banking/orders/` - Create banking order
- `GET /api/orders/banking/orders/` - List banking orders
- `GET /api/orders/banking/orders/<order_id>/` - Get order details
- `POST /api/orders/banking/orders/<order_id>/cancel/` - Cancel order

---

## 11. MARKETPLACE

### Products
- `GET /api/marketplace/products/` - List products
- `POST /api/marketplace/products/` - Create product
- `GET /api/marketplace/products/<product_id>/` - Get product details
- `PUT /api/marketplace/products/<product_id>/` - Update product
- `DELETE /api/marketplace/products/<product_id>/` - Delete product

### Orders
- `POST /api/marketplace/orders/` - Create marketplace order
- `GET /api/marketplace/orders/` - List marketplace orders
- `GET /api/marketplace/orders/<order_id>/` - Get order details

---

## 12. ADMIN DASHBOARD

### Statistics
- `GET /api/admin/dashboard/stats/` - Get dashboard statistics
- `GET /api/admin/dashboard/revenue/` - Get revenue data

### User Management
- `GET /api/admin/users/` - List all users
- `GET /api/admin/users/<user_id>/` - Get user details

### Order Management
- `GET /api/admin/orders/` - List all orders
- `GET /api/admin/orders/<order_id>/` - Get order details

---

## COMPLETE FLOW EXAMPLE

### Client Journey
1. `POST /api/accounts/register/` - Register
2. `POST /api/accounts/verify-phone/` - Verify phone
3. `POST /api/accounts/login/` - Login
4. `POST /api/orders/errands/calculate-price/` - Calculate price
5. `POST /api/orders/errands/draft/` - Create draft
6. `POST /api/orders/errands/<id>/upload-image/` - Upload images
7. `PUT /api/orders/errands/<id>/receiver-info/` - Add receiver
8. `POST /api/orders/errands/<id>/confirm/` - Confirm errand
9. `POST /api/orders/payments/initiate/` - Pay
10. `GET /api/orders/<id>/rider-details/` - Get rider info
11. `GET /api/orders/<id>/tracking/` - Track order

### Rider Journey
1. `POST /api/accounts/register/` - Register as rider
2. `POST /api/accounts/assistant/verification/` - Submit documents
3. `POST /api/accounts/login/` - Login
4. `GET /api/orders/available/` - View available orders
5. `POST /api/orders/<id>/accept/` - Accept order
6. `PUT /api/orders/<id>/status/` - Update to "in_progress"
7. `POST /api/orders/<id>/images/` - Upload delivery proof
8. `PUT /api/orders/<id>/status/` - Update to "completed"

### Handler Journey
1. `POST /api/accounts/login/` - Login
2. `GET /api/orders/handler/all/` - View all orders
3. `POST /api/orders/<id>/assign/` - Assign rider to order
