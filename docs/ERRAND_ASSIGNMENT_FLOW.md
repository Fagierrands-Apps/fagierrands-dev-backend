# Errand Assignment Flow - Complete Journey

## The Story

### Part 1: Customer Places Errand
1. Customer creates a draft errand with pickup/delivery details
2. Customer uploads images (optional)
3. Customer adds receiver information
4. Customer confirms the order → Status becomes "pending"
5. System notifies available handlers/riders

### Part 2: Handler Assigns Rider
1. Handler logs into the system
2. Handler fetches pending orders
3. Handler assigns a rider to the order → Status becomes "assigned"
4. **Customer app receives notification with rider information**

### Part 3: Rider Completes Errand
1. Rider starts the errand → Status becomes "in_progress"
2. Rider completes delivery → Status becomes "completed"

---

## API Endpoints Flow

### STEP 1: Create Draft Errand
**Endpoint:** `POST /api/orders/errands/draft/`

**Request:**
```json
{
  "order_type_id": 1,
  "title": "tea leaves",
  "description": "tea leaves for chai",
  "pickup_address": "next gen mall",
  "delivery_address": "kilimani",
  "pickup_latitude": 0,
  "pickup_longitude": 0,
  "delivery_latitude": 0,
  "delivery_longitude": 0,
  "distance": 20
}
```

**Response:**
```json
{
  "order_id": 9,
  "status": "draft",
  "pricing_breakdown": {
    "base_fee": 200,
    "distance_fee": 260,
    "total": 460,
    "distance_km": 20
  },
  "next_step": "Upload images and add receiver contact info"
}
```

---

### STEP 2: Upload Images (Optional)
**Endpoint:** `POST /api/orders/errands/{order_id}/upload-image/`

**Response:**
```json
{
  "image_id": 2,
  "image": {
    "id": 2,
    "image_url": "http://localhost:8000/media/order_images/download_57BMBdr.jpeg",
    "description": "image",
    "stage": "before",
    "uploaded_at": "2026-04-12T22:19:27.705502+03:00"
  },
  "total_images": 1
}
```

---

### STEP 3: Add Receiver Info
**Endpoint:** `POST /api/orders/errands/{order_id}/receiver-info/`

**Request:**
```json
{
  "recipient_name": "janabi",
  "contact_number": "0796605409",
  "estimated_value": 30000
}
```

**Response:**
```json
{
  "message": "Receiver info updated",
  "order": {
    "id": 9,
    "recipient_name": "janabi",
    "contact_number": "0796605409",
    "status": "draft"
  }
}
```

---

### STEP 4: Confirm Order
**Endpoint:** `POST /api/orders/errands/{order_id}/confirm/`

**Response:**
```json
{
  "message": "Errand confirmed successfully!",
  "order_id": 9,
  "status": "pending",
  "order": {
    "id": 9,
    "title": "tea leaves",
    "pickup_address": "next gen mall",
    "delivery_address": "kilimani",
    "recipient_name": "janabi",
    "contact_number": "0796605409",
    "price": "460.00",
    "status": "pending"
  },
  "notifications_sent": true
}
```

---

## Handler/Admin Assignment Flow

### STEP 5: Handler Login
**Endpoint:** `POST /api/accounts/login/`

**Note:** Same login endpoint for all users. Uses phone_number for login.

**Request:**
```json
{
  "phone_number": "0712345678",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 5,
  "email": "handler@fagierrands.com",
  "user_type": "handler",
  "is_verified": true,
  "email_verified": false
}
```

---

### STEP 6: Handler Fetches Pending Orders
**Endpoint:** `GET /api/orders/pending/`

**Response:**
```json
[
  {
    "id": 9,
    "title": "tea leaves",
    "pickup_address": "next gen mall",
    "delivery_address": "kilimani",
    "status": "pending",
    "price": "460.00",
    "created_at": "2026-04-12T22:09:11.563615+03:00"
  }
]
```

---

### STEP 7: Handler Assigns Rider to Order
**Endpoint:** `POST /api/orders/{order_id}/assign/`

**Request:**
```json
{
  "assistant_id": 12
}
```

**Response:**
```json
{
  "message": "Rider assigned successfully",
  "order_id": 9,
  "status": "assigned",
  "assigned_at": "2026-04-12T22:30:15.123456+03:00",
  "rider": {
    "id": 12,
    "name": "John Kamau",
    "phone_number": "0712345678",
    "plate_number": "KCA 123B",
    "profile_picture": "http://localhost:8000/media/riders/john_kamau.jpg"
  }
}
```

**🔔 Customer App Receives Notification with Rider Info**

---

### STEP 7.5: Customer App Polls for Rider Assignment (Alternative to Push Notification)
**Endpoint:** `GET /api/orders/{order_id}/rider-assignment/`

**Purpose:** Customer app polls this endpoint every few seconds to check if a rider has been assigned.

**Response (No rider yet):**
```json
{
  "order_id": 9,
  "status": "pending",
  "rider_assigned": false,
  "message": "Searching for available rider..."
}
```

**Response (Rider assigned):**
```json
{
  "order_id": 9,
  "status": "assigned",
  "rider_assigned": true,
  "assigned_at": "2026-04-12T22:30:15.123456+03:00",
  "rider": {
    "id": 12,
    "name": "John Kamau",
    "phone_number": "0712345678",
    "profile_picture": "http://localhost:8000/media/profiles/john.jpg",
    "rating": 4.8,
    "is_online": true
  }
}
```

---

## Rider Execution Flow

### STEP 8: Rider Starts Errand
**Endpoint:** `POST /api/orders/{order_id}/status/`

**Request:**
```json
{
  "status": "in_progress"
}
```

**Response:**
```json
{
  "id": 9,
  "status": "in_progress",
  "started_at": "2026-04-12T22:35:00.123456+03:00"
}
```

---

### STEP 9: Rider Completes Errand
**Endpoint:** `POST /api/orders/{order_id}/status/`

**Request:**
```json
{
  "status": "completed"
}
```

**Response:**
```json
{
  "id": 9,
  "status": "completed",
  "completed_at": "2026-04-12T23:00:00.123456+03:00"
}
```

---

## Complete Flow Diagram

```
CUSTOMER
   ↓
1. POST /api/orders/errands/draft/ → draft
   ↓
2. POST /api/orders/errands/{id}/upload-image/ → images added
   ↓
3. POST /api/orders/errands/{id}/receiver-info/ → receiver added
   ↓
4. POST /api/orders/errands/{id}/confirm/ → pending
   ↓
   ↓ (notifications sent to handlers)
   ↓
HANDLER
   ↓
5. POST /api/auth/login/ → authenticated
   ↓
6. GET /api/orders/errands/pending/ → sees pending orders
   ↓
7. POST /api/orders/errands/{id}/assign-rider/ → assigned
   ↓
   ↓ 🔔 CUSTOMER RECEIVES RIDER INFO NOTIFICATION
   ↓
RIDER
   ↓
8. POST /api/orders/errands/{id}/start/ → in_progress
   ↓
9. POST /api/orders/errands/{id}/complete/ → completed
```

---

## Key Points

- **Status Flow:** draft → pending → assigned → in_progress → completed
- **Rider Info Sent:** When handler assigns rider (Step 7), customer immediately receives rider details
- **Customer Notification:** Includes rider name, phone, photo, vehicle info, and rating
- **Real-time Updates:** Customer can track order status changes throughout the journey
