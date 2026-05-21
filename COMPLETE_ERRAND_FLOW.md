# Complete Errand Flow - From Onboarding to Completion

## 📱 THE COMPLETE USER JOURNEY

---

## PART 1: CLIENT ONBOARDING

### Step 1: Registration
**Story:** Sarah wants to send a package to her friend.

**Endpoint:** `POST /api/accounts/register/`

**Request:**
```json
{
  "phone_number": "+254712345678",
  "email": "sarah@example.com",
  "password": "SecurePass123",
  "first_name": "Sarah",
  "last_name": "Mwangi",
  "user_type": "client"
}
```

**Response:**
```json
{
  "message": "Registration successful. Please verify your phone number.",
  "user_id": 101,
  "phone_number": "+254712345678"
}
```

**What Happens:**
- Account created in database
- OTP sent to phone via SMS
- User status: `unverified`

---

### Step 2: Phone Verification
**Story:** Sarah receives OTP "123456" on her phone.

**Endpoint:** `POST /api/accounts/verify-phone/`

**Request:**
```json
{
  "phone_number": "+254712345678",
  "otp": "123456"
}
```

**Response:**
```json
{
  "message": "Phone verified successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 101,
    "phone_number": "+254712345678",
    "email": "sarah@example.com",
    "first_name": "Sarah",
    "user_type": "client"
  }
}
```

**What Happens:**
- Phone verified ✅
- JWT tokens generated
- User can now login
- User status: `active`

---

### Step 3: Login (Future Sessions)
**Story:** Sarah opens the app the next day.

**Endpoint:** `POST /api/accounts/login/`

**Request:**
```json
{
  "phone_number": "+254712345678",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 101,
    "phone_number": "+254712345678",
    "first_name": "Sarah",
    "user_type": "client"
  }
}
```

**What Happens:**
- Credentials validated
- New JWT tokens issued
- User logged in

---

## PART 2: ERRAND PLACEMENT

### Step 4: Calculate Price
**Story:** Sarah wants to send a package from Westlands to Karen.

**Endpoint:** `POST /api/orders/errands/calculate-price/`

**Request:**
```json
{
  "pickup_latitude": -1.2676,
  "pickup_longitude": 36.8070,
  "delivery_latitude": -1.3197,
  "delivery_longitude": 36.7076,
  "order_type_id": 1
}
```

**Response:**
```json
{
  "distance": 8.5,
  "estimated_duration": 25,
  "price": 450.00,
  "breakdown": {
    "base_price": 200.00,
    "distance_charge": 250.00
  }
}
```

**What Happens:**
- Distance calculated using Google Maps
- Price computed based on distance
- Estimated time provided

---

### Step 5: Create Draft Errand
**Story:** Sarah agrees with the price and starts creating the errand.

**Endpoint:** `POST /api/orders/errands/draft/`

**Request:**
```json
{
  "order_type_id": 1,
  "title": "Package Delivery",
  "description": "Birthday gift for my friend",
  "pickup_address": "Westlands, Nairobi",
  "pickup_latitude": -1.2676,
  "pickup_longitude": 36.8070,
  "delivery_address": "Karen, Nairobi",
  "delivery_latitude": -1.3197,
  "delivery_longitude": 36.7076,
  "estimated_value": 5000.00
}
```

**Response:**
```json
{
  "id": 501,
  "status": "draft",
  "title": "Package Delivery",
  "price": 450.00,
  "created_at": "2026-05-21T21:00:00Z"
}
```

**What Happens:**
- Draft order created
- Status: `draft`
- Not visible to riders yet

---

### Step 6: Upload Package Images
**Story:** Sarah takes photos of the package.

**Endpoint:** `POST /api/orders/errands/501/upload-image/`

**Request:** (multipart/form-data)
```
image: [file1.jpg]
image: [file2.jpg]
stage: before
```

**Response:**
```json
{
  "message": "Images uploaded successfully",
  "images": [
    {
      "id": 1001,
      "image_url": "https://storage.example.com/orders/501/img1.jpg",
      "stage": "before"
    },
    {
      "id": 1002,
      "image_url": "https://storage.example.com/orders/501/img2.jpg",
      "stage": "before"
    }
  ]
}
```

**What Happens:**
- Images uploaded to cloud storage
- URLs saved to database
- Proof of package condition

---

### Step 7: Add Receiver Information
**Story:** Sarah adds her friend's contact details.

**Endpoint:** `PUT /api/orders/errands/501/receiver-info/`

**Request:**
```json
{
  "recipient_name": "Jane Kamau",
  "contact_number": "+254723456789",
  "alternative_contact_name": "John Kamau",
  "alternative_contact_number": "+254734567890"
}
```

**Response:**
```json
{
  "message": "Receiver information updated",
  "order_id": 501,
  "recipient_name": "Jane Kamau",
  "contact_number": "+254723456789"
}
```

**What Happens:**
- Receiver details saved
- Rider will use this for delivery

---

### Step 8: Confirm Errand
**Story:** Sarah reviews everything and confirms.

**Endpoint:** `POST /api/orders/errands/501/confirm/`

**Request:**
```json
{
  "confirm": true
}
```

**Response:**
```json
{
  "message": "Errand confirmed successfully",
  "order_id": 501,
  "status": "pending",
  "payment_required": true,
  "amount": 450.00
}
```

**What Happens:**
- Status changed: `draft` → `pending`
- Order now visible to handlers
- Payment required before assignment

---

### Step 9: Initiate Payment
**Story:** Sarah proceeds to pay for the errand.

**Endpoint:** `POST /api/orders/payments/initiate/`

**Request:**
```json
{
  "order_id": 501,
  "payment_method": "mpesa",
  "phone_number": "+254712345678"
}
```

**Response:**
```json
{
  "payment_id": 2001,
  "status": "pending",
  "amount": 450.00,
  "message": "STK push sent to your phone"
}
```

**What Happens:**
- Payment record created
- M-Pesa STK push sent
- Sarah enters PIN on phone

---

### Step 10: Payment Confirmation
**Story:** Sarah enters PIN, payment processes.

**Endpoint:** `GET /api/orders/501/payment-status/`

**Response:**
```json
{
  "payment_status": "completed",
  "transaction_id": "QGH7K2M9P1",
  "amount": 450.00,
  "paid_at": "2026-05-21T21:05:00Z",
  "order_status": "pending"
}
```

**What Happens:**
- Payment confirmed ✅
- Order ready for assignment
- Handler can now see the order

---

## PART 3: HANDLER ASSIGNS RIDER

### Step 11: Handler Views Orders
**Story:** Mike (handler) logs in to assign riders.

**Endpoint:** `GET /api/orders/handler/all/`

**Response:**
```json
{
  "orders": [
    {
      "id": 501,
      "title": "Package Delivery",
      "client": "Sarah Mwangi",
      "pickup_address": "Westlands, Nairobi",
      "delivery_address": "Karen, Nairobi",
      "status": "pending",
      "payment_status": "completed",
      "price": 450.00,
      "created_at": "2026-05-21T21:00:00Z"
    }
  ]
}
```

**What Happens:**
- Handler sees all paid orders
- Can view order details
- Decides which rider to assign

---

### Step 12: Handler Assigns Rider
**Story:** Mike assigns David (rider) to the errand.

**Endpoint:** `POST /api/orders/501/assign/`

**Request:**
```json
{
  "assistant_id": 201
}
```

**Response:**
```json
{
  "message": "Rider assigned successfully",
  "order_id": 501,
  "rider": {
    "id": 201,
    "name": "David Omondi",
    "phone_number": "+254745678901"
  },
  "status": "assigned",
  "assigned_at": "2026-05-21T21:10:00Z"
}
```

**What Happens:**
- Status changed: `pending` → `assigned`
- Rider notified via push notification
- Client can now see rider details

---

## PART 4: CLIENT GETS RIDER INFO

### Step 13: Client Checks Rider Details
**Story:** Sarah wants to know who her rider is.

**Endpoint:** `GET /api/orders/501/rider-details/`

**Response:**
```json
{
  "assigned": true,
  "rider": {
    "id": 201,
    "name": "David Omondi",
    "phone_number": "+254745678901",
    "profile_image": "https://storage.example.com/profiles/david.jpg",
    "plate_number": "KCA 123D"
  },
  "order_status": "assigned",
  "assigned_at": "2026-05-21T21:10:00Z"
}
```

**What Happens:**
- Sarah sees rider's name
- Can call rider if needed
- Sees vehicle plate number

---

## PART 5: RIDER ACCEPTS & COMPLETES

### Step 14: Rider Views Assigned Orders
**Story:** David (rider) opens his app.

**Endpoint:** `GET /api/orders/assistant/`

**Response:**
```json
{
  "orders": [
    {
      "id": 501,
      "title": "Package Delivery",
      "pickup_address": "Westlands, Nairobi",
      "delivery_address": "Karen, Nairobi",
      "recipient_name": "Jane Kamau",
      "contact_number": "+254723456789",
      "status": "assigned",
      "price": 450.00
    }
  ]
}
```

**What Happens:**
- David sees order details
- Gets pickup and delivery addresses
- Sees receiver contact info

---

### Step 15: Rider Accepts Order
**Story:** David confirms he'll do the delivery.

**Endpoint:** `POST /api/orders/501/accept/`

**Response:**
```json
{
  "message": "Order accepted successfully",
  "order_id": 501,
  "status": "assigned"
}
```

**What Happens:**
- Order confirmed by rider
- Client notified
- Rider heads to pickup location

---

### Step 16: Rider Starts Journey
**Story:** David picks up the package and starts delivery.

**Endpoint:** `PUT /api/orders/501/status/`

**Request:**
```json
{
  "status": "in_progress"
}
```

**Response:**
```json
{
  "message": "Order status updated",
  "order_id": 501,
  "status": "in_progress",
  "started_at": "2026-05-21T21:20:00Z"
}
```

**What Happens:**
- Status changed: `assigned` → `in_progress`
- Client can track rider
- Real-time location updates start

---

### Step 17: Client Tracks Rider
**Story:** Sarah wants to see where David is.

**Endpoint:** `GET /api/orders/501/tracking/`

**Response:**
```json
{
  "order_id": 501,
  "status": "in_progress",
  "rider": {
    "name": "David Omondi",
    "phone_number": "+254745678901"
  },
  "current_location": {
    "latitude": -1.2800,
    "longitude": 36.7900,
    "updated_at": "2026-05-21T21:25:00Z"
  },
  "estimated_arrival": "2026-05-21T21:35:00Z"
}
```

**What Happens:**
- Sarah sees rider's location on map
- Gets estimated arrival time
- Can call rider if needed

---

### Step 18: Rider Completes Delivery
**Story:** David delivers the package to Jane.

**Endpoint:** `POST /api/orders/501/images/`

**Request:** (multipart/form-data)
```
image: [delivery_proof.jpg]
stage: after
```

**Response:**
```json
{
  "message": "Delivery proof uploaded",
  "image_url": "https://storage.example.com/orders/501/delivery.jpg"
}
```

**What Happens:**
- David takes photo of delivered package
- Proof uploaded to system
- Ready to mark as complete

---

### Step 19: Mark Order Complete
**Story:** David marks the delivery as done.

**Endpoint:** `PUT /api/orders/501/status/`

**Request:**
```json
{
  "status": "completed"
}
```

**Response:**
```json
{
  "message": "Order completed successfully",
  "order_id": 501,
  "status": "completed",
  "completed_at": "2026-05-21T21:35:00Z"
}
```

**What Happens:**
- Status changed: `in_progress` → `completed`
- Client notified
- Payment released to rider
- Sarah gets 10 wallet points

---

## PART 6: POST-DELIVERY

### Step 20: Client Reviews Order
**Story:** Sarah rates her experience.

**Endpoint:** `POST /api/orders/501/review/`

**Request:**
```json
{
  "rating": 5,
  "comment": "Fast and professional delivery. Package arrived safely!"
}
```

**Response:**
```json
{
  "message": "Review submitted successfully",
  "order_id": 501,
  "rating": 5
}
```

**What Happens:**
- Review saved
- Rider's rating updated
- Order fully closed

---

## 📊 COMPLETE FLOW SUMMARY

```
CLIENT JOURNEY:
Register → Verify Phone → Login → Calculate Price → Create Draft → 
Upload Images → Add Receiver → Confirm → Pay → Get Rider Info → 
Track Delivery → Receive Package → Review

HANDLER JOURNEY:
Login → View Orders → Assign Rider

RIDER JOURNEY:
Login → View Assigned Orders → Accept → Start Journey → 
Upload Delivery Proof → Complete

STATUS PROGRESSION:
draft → pending → assigned → in_progress → completed
```

---

## 🔑 KEY ENDPOINTS BY ROLE

### Client (Sarah)
1. `POST /api/accounts/register/` - Sign up
2. `POST /api/accounts/verify-phone/` - Verify
3. `POST /api/accounts/login/` - Login
4. `POST /api/orders/errands/calculate-price/` - Get price
5. `POST /api/orders/errands/draft/` - Create errand
6. `POST /api/orders/errands/{id}/upload-image/` - Add photos
7. `PUT /api/orders/errands/{id}/receiver-info/` - Add receiver
8. `POST /api/orders/errands/{id}/confirm/` - Confirm
9. `POST /api/orders/payments/initiate/` - Pay
10. `GET /api/orders/{id}/rider-details/` - See rider
11. `GET /api/orders/{id}/tracking/` - Track
12. `POST /api/orders/{id}/review/` - Review

### Handler (Mike)
1. `POST /api/accounts/login/` - Login
2. `GET /api/orders/handler/all/` - View orders
3. `POST /api/orders/{id}/assign/` - Assign rider

### Rider (David)
1. `POST /api/accounts/login/` - Login
2. `GET /api/orders/assistant/` - View orders
3. `POST /api/orders/{id}/accept/` - Accept
4. `PUT /api/orders/{id}/status/` - Update status
5. `POST /api/orders/{id}/images/` - Upload proof

---

## 💡 IMPORTANT NOTES

1. **Authentication:** All endpoints (except register/login) require Bearer token
2. **Payment:** Order must be paid before rider assignment
3. **Images:** Upload before and after photos for proof
4. **Tracking:** Real-time location updates during delivery
5. **Notifications:** Push notifications at each status change
6. **Wallet Points:** Client earns 10 points on completion

---

## 🚀 NEXT STEPS

- Test each endpoint in Postman
- Implement in mobile app
- Add error handling
- Set up push notifications
- Configure payment gateway
