# 📖 FagiErrands: Complete System Journey

**A Simple Story of How Everything Works**

*From signing up to completing an errand - every step explained simply*

---

## 👥 Meet Our Users

- **Sarah** - A busy client who needs help with errands
- **David** - A rider who delivers for FagiErrands  
- **James** - A handler who manages everything

**Base URL:** `https://fagierrands.onrender.com/api`

---

# PART 1: GETTING STARTED

## 📱 Sarah Signs Up (Client)

**What Sarah does:**
Opens the app → Taps "Sign Up" → Enters her details

**API:**
```
POST /accounts/register/
```

**Sarah sends:**
```json
{
  "username": "sarah_mwangi",
  "email": "sarah@example.com", 
  "password": "SecurePass123!",
  "phone_number": "+254712345678",
  "first_name": "Sarah",
  "last_name": "Mwangi",
  "user_type": "user"
}
```

**System does:**
1. Creates Sarah's account
2. Generates code: `123456`
3. Sends SMS

**📱 SMS to Sarah:**
```
FagiErrands: Your verification code is 123456. 
Valid for 10 minutes.
```

**Sarah gets back:**
```json
{
  "message": "User registered successfully. Please verify your phone number.",
  "user_id": 101
}
```

---

**What Sarah does next:**
Enters the code `123456` from SMS

**API:**
```
POST /accounts/verify-phone/
```

**Sarah sends:**
```json
{
  "phone_number": "+254712345678",
  "code": "123456"
}
```

**Sarah gets back:**
```json
{
  "message": "Phone number verified successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 101,
    "username": "sarah_mwangi",
    "user_type": "user",
    "is_phone_verified": true
  }
}
```

**✅ Sarah is ready to place orders!**

---

## 🏍️ David Signs Up (Rider)

**What David does:**
Opens app → Selects "Join as Rider" → Fills form → Uploads 4 photos (selfie, ID front, ID back, license)

**API:**
```
POST /accounts/rider/register/
```

**David sends:**
```json
{
  "username": "david_rider",
  "email": "david@example.com",
  "password": "RiderPass123!",
  "phone_number": "+254723456789",
  "first_name": "David",
  "last_name": "Omondi",
  "full_name": "David Omondi Otieno",
  "id_number": "12345678",
  "address": "123 Ngong Road, Nairobi",
  "area_of_operation": "Westlands, Kilimani",
  "driving_license_number": "DL987654",
  "profile_picture": <selfie.jpg>,
  "id_front_image": <id_front.jpg>,
  "id_back_image": <id_back.jpg>,
  "driving_license_image": <license.jpg>
}
```

**System does:**
1. Creates David's account
2. Uploads 4 photos to Supabase cloud
3. Saves photo URLs
4. Generates code: `789012`
5. Sends SMS

**📱 SMS to David:**
```
FagiErrands: Your verification code is 789012. 
Valid for 10 minutes.
```

**David gets back:**
```json
{
  "message": "Rider registration successful. Please verify your phone number.",
  "user_id": 102,
  "verification_status": "pending",
  "documents_uploaded": {
    "selfie_url": "https://supabase.co/.../selfie.jpg",
    "id_front_url": "https://supabase.co/.../id_front.jpg",
    "id_back_url": "https://supabase.co/.../id_back.jpg",
    "driving_license_url": "https://supabase.co/.../license.jpg"
  }
}
```

---

**What David does next:**
Enters code `789012` from SMS

**API:**
```
POST /accounts/verify-phone/
```

**David sends:**
```json
{
  "phone_number": "+254723456789",
  "code": "789012"
}
```

**David gets back:**
```json
{
  "message": "Phone number verified successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 102,
    "username": "david_rider",
    "user_type": "assistant",
    "is_phone_verified": true,
    "verification_status": "pending"
  }
}
```

**⏳ David waits for James to approve him...**

---

## 👔 James Approves David (Handler)

**What James does:**
Logs into handler dashboard → Sees David's application → Reviews 4 photos → Clicks "Approve"

**API James uses:**
```
GET /accounts/admin/verifications/?status=pending
```

**James sees:**
```json
[
  {
    "id": 5,
    "user": {
      "id": 102,
      "username": "david_rider",
      "first_name": "David",
      "phone_number": "+254723456789"
    },
    "full_name": "David Omondi Otieno",
    "id_number": "12345678",
    "selfie_url": "https://supabase.co/.../selfie.jpg",
    "id_front_url": "https://supabase.co/.../id_front.jpg",
    "id_back_url": "https://supabase.co/.../id_back.jpg",
    "driving_license_url": "https://supabase.co/.../license.jpg",
    "status": "pending"
  }
]
```

---

**What James does:**
Clicks "Approve" button

**API:**
```
PATCH /accounts/admin/verifications/5/update/
```

**James sends:**
```json
{
  "status": "verified"
}
```

**System does:**
1. Marks David as verified
2. Activates David's account
3. Sends SMS to David

**📱 SMS to David:**
```
FagiErrands: Congratulations! Your rider account has been 
approved. You can now start accepting orders.
```

**James gets back:**
```json
{
  "id": 5,
  "status": "verified",
  "message": "Rider verified successfully. SMS notification sent."
}
```

**✅ David is now an active rider!**

---

# PART 2: PLACING AN ORDER

## 🛒 Sarah Places a Shopping Order

**What Sarah does:**
Opens app → Taps "New Order" → Selects "Shopping" → Fills details

**API:**
```
POST /orders/shopping/
```

**Sarah sends:**
```json
{
  "title": "Weekend Groceries",
  "description": "Need items from Naivas",
  "pickup_address": "Naivas Supermarket, Westlands",
  "pickup_latitude": -1.2674,
  "pickup_longitude": 36.8108,
  "delivery_address": "Apartment 5B, Riverside Drive",
  "delivery_latitude": -1.2701,
  "delivery_longitude": 36.8089,
  "shopping_items": [
    {"name": "Milk - 2 liters", "quantity": 2},
    {"name": "Bread", "quantity": 1},
    {"name": "Eggs - Tray", "quantity": 1}
  ]
}
```

**System does:**
1. Creates order with status `pending`
2. Calculates price: KSh 200 (base fee for 1.5km)
3. Sends SMS to Sarah

**📱 SMS to Sarah:**
```
FagiErrands: Your order 'Weekend Groceries' has been placed 
successfully. Order ID: #1001. We'll notify you when a rider 
is assigned.
```

**Sarah gets back:**
```json
{
  "id": 1001,
  "title": "Weekend Groceries",
  "status": "pending",
  "price": 200.00,
  "distance": 1.5,
  "shopping_items": [
    {"id": 1, "name": "Milk - 2 liters", "quantity": 2},
    {"id": 2, "name": "Bread", "quantity": 1},
    {"id": 3, "name": "Eggs - Tray", "quantity": 1}
  ]
}
```

**⏳ Order is waiting for a rider...**

---

# PART 3: ASSIGNING A RIDER

## 👔 James Assigns David to Sarah's Order

**What James does:**
Opens handler dashboard → Sees Sarah's order → Selects David → Clicks "Assign"

**API James uses to see orders:**
```
GET /orders/?status=pending
```

**James sees:**
```json
[
  {
    "id": 1001,
    "title": "Weekend Groceries",
    "status": "pending",
    "price": 200.00,
    "client_name": "Sarah Mwangi",
    "pickup_address": "Naivas Supermarket, Westlands",
    "delivery_address": "Apartment 5B, Riverside Drive"
  }
]
```

---

**API James uses to see available riders:**
```
GET /accounts/available-assistants/
```

**James sees:**
```json
[
  {
    "id": 102,
    "first_name": "David",
    "last_name": "Omondi",
    "phone_number": "+254723456789",
    "is_available": true,
    "current_orders": 0,
    "rating": 4.8
  }
]
```

---

**What James does:**
Clicks "Assign David" button

**API:**
```
PATCH /orders/1001/assign/
```

**James sends:**
```json
{
  "assistant_id": 102
}
```

**System does:**
1. Updates order status to `assigned`
2. Links David to order
3. Sends SMS to Sarah
4. Sends notification to David

**📱 SMS to Sarah:**
```
FagiErrands: David Omondi has been assigned to your order 
'Weekend Groceries'. Track your order in the app.
```

**📱 Notification to David:**
```
New Order Assigned: 'Weekend Groceries'
Pickup: Naivas Supermarket, Westlands
```

**James gets back:**
```json
{
  "id": 1001,
  "status": "assigned",
  "assistant": {
    "id": 102,
    "first_name": "David",
    "phone_number": "+254723456789"
  }
}
```

**✅ David has been assigned!**

---

# PART 4: COMPLETING THE ORDER

## 🏍️ David Starts the Order

**What David does:**
Opens app → Sees new order → Taps "View Details" → Arrives at Naivas → Taps "Start Order"

**API David uses to see order:**
```
GET /orders/1001/
```

**David sees:**
```json
{
  "id": 1001,
  "title": "Weekend Groceries",
  "status": "assigned",
  "client": {
    "first_name": "Sarah",
    "phone_number": "+254712345678"
  },
  "pickup_address": "Naivas Supermarket, Westlands",
  "delivery_address": "Apartment 5B, Riverside Drive",
  "shopping_items": [
    {"name": "Milk - 2 liters", "quantity": 2},
    {"name": "Bread", "quantity": 1},
    {"name": "Eggs - Tray", "quantity": 1}
  ]
}
```

---

**What David does:**
Taps "Start Order" button

**API:**
```
PATCH /orders/1001/update-status/
```

**David sends:**
```json
{
  "status": "in_progress"
}
```

**System does:**
1. Updates status to `in_progress`
2. Generates release code: `456789`
3. Sends SMS to Sarah with code

**📱 SMS to Sarah:**
```
FagiErrands: Your order 'Weekend Groceries' has started. 
Release code: 456789. Share this code with the rider upon delivery.
```

**David gets back:**
```json
{
  "id": 1001,
  "status": "in_progress",
  "release_code": "456789",
  "started_at": "2026-05-24T11:30:00Z"
}
```

**🛒 David is now shopping!**

---

## 📸 David Uploads Receipt

**What David does:**
Finishes shopping → Pays → Takes photo of receipt → Uploads in app

**API:**
```
POST /orders/1001/images/
```

**David sends:**
```
image: <receipt_photo.jpg>
description: "Receipt from Naivas"
stage: "receipt"
```

**System does:**
1. Uploads photo to Supabase cloud
2. Saves photo URL

**David gets back:**
```json
{
  "id": 1,
  "image_url": "https://supabase.co/.../receipt.jpg",
  "description": "Receipt from Naivas",
  "uploaded_at": "2026-05-24T11:45:00Z"
}
```

---

## 🏍️ David Delivers to Sarah

**What David does:**
Rides to Sarah's apartment → Calls Sarah → Sarah gives release code `456789` → David enters code → Taps "Complete"

**API:**
```
PATCH /orders/1001/update-status/
```

**David sends:**
```json
{
  "status": "completed",
  "release_code": "456789"
}
```

**System does:**
1. Checks if code matches `456789` ✅
2. Updates status to `completed`
3. Adds 10 points to Sarah's wallet
4. Sends SMS to Sarah

**📱 SMS to Sarah:**
```
FagiErrands: Your order 'Weekend Groceries' has been completed! 
Thank you for using FagiErrands. Please rate your experience.
```

**David gets back:**
```json
{
  "id": 1001,
  "status": "completed",
  "completed_at": "2026-05-24T12:15:00Z",
  "message": "Order completed successfully"
}
```

**✅ Order complete!**

---

## ⭐ Sarah Leaves a Review

**What Sarah does:**
Opens app → Sees "Rate your order" → Gives 5 stars → Writes comment

**API:**
```
POST /orders/1001/review/
```

**Sarah sends:**
```json
{
  "rating": 5,
  "comment": "David was very professional and fast! Highly recommend!"
}
```

**System does:**
1. Saves review
2. Updates David's average rating
3. Sends notification to David

**📱 Notification to David:**
```
New Review: Sarah Mwangi rated you 5 stars!
"David was very professional and fast!"
```

**Sarah gets back:**
```json
{
  "id": 1,
  "order": 1001,
  "rating": 5,
  "comment": "David was very professional and fast! Highly recommend!",
  "created_at": "2026-05-24T12:20:00Z"
}
```

**⭐⭐⭐⭐⭐ Perfect rating!**

---

# SUMMARY: ALL ENDPOINTS USED

## 🔐 Authentication
```
POST /accounts/register/              - Sign up (client/handler)
POST /accounts/rider/register/        - Sign up (rider with documents)
POST /accounts/verify-phone/          - Verify phone with OTP
POST /accounts/login/                 - Login
POST /accounts/token/refresh/         - Refresh token
```

## 👥 User Management
```
GET  /accounts/user/                  - Get my profile
GET  /accounts/user/{id}/             - Get user by ID
PATCH /accounts/user/{id}/            - Update user
GET  /accounts/available-assistants/  - Get available riders
```

## ✅ Rider Verification (Handler only)
```
GET   /accounts/admin/verifications/           - List all verifications
GET   /accounts/admin/verifications/{id}/      - View one verification
PATCH /accounts/admin/verifications/{id}/update/ - Approve/Reject rider
```

## 📦 Orders
```
POST  /orders/shopping/               - Create shopping order
POST  /orders/pickup-delivery/        - Create pickup/delivery order
GET   /orders/                        - List all orders (with filters)
GET   /orders/{id}/                   - View order details
PATCH /orders/{id}/assign/            - Assign rider (handler)
PATCH /orders/{id}/update-status/     - Update status (rider/handler)
POST  /orders/{id}/images/            - Upload images (rider)
POST  /orders/{id}/review/            - Leave review (client)
```

## 📊 Handler Dashboard
```
GET /accounts/assistants/stats/       - Get rider statistics
GET /accounts/handler/clients/        - Get assigned clients
GET /orders/?status=pending           - Get pending orders
```

---

# 📱 SMS FLOW (8 SMS per order)

1. **Client Registration** - OTP code
2. **Rider Registration** - OTP code  
3. **Rider Approval** - "Congratulations! You're approved"
4. **Order Created** - "Order placed successfully"
5. **Rider Assigned** - "David has been assigned"
6. **Order Started** - "Order started. Release code: 456789"
7. **Order Completed** - "Order completed! Please rate"
8. **Payment Confirmed** - "Payment received" (if M-Pesa integrated)

**Cost:** ~KSh 6.40 per order (8 SMS × KSh 0.80)

---

# 🎯 ORDER TYPES

## 1. Shopping Errand
- Client provides shopping list
- Rider buys items
- Rider uploads receipt
- Rider delivers to client

## 2. Pickup & Delivery
- Client has package ready
- Rider picks up package
- Rider delivers to destination
- No shopping involved

## 3. Cargo (Future)
- Large items
- Multiple stops
- Special handling

---

# 🔑 KEY FEATURES

✅ **One-step rider registration** with document upload  
✅ **Cloud storage** for all images (Supabase)  
✅ **Release code security** for order completion  
✅ **SMS notifications** at every step  
✅ **Real-time tracking** (optional)  
✅ **Wallet points** for clients  
✅ **Reviews & ratings** for riders  
✅ **Handler approval** for riders  

---

**END OF JOURNEY** 🎉

*Everything from signup to completion - simple and clear!*
