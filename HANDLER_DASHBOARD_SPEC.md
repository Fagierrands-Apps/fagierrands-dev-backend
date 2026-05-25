# 🎯 HANDLER DASHBOARD - COMPLETE SPECIFICATION FOR AI STUDIO

## 📋 PROJECT OVERVIEW
Build a comprehensive Handler Dashboard for FagiErrands - a web application where handlers (administrators) can manage riders, clients, orders, and monitor the entire errand service platform.

---

## 🌐 API BASE URL
**Production:** `https://fagierrands.onrender.com/api`
**Local Testing:** `http://localhost:8000/api`

---

## 🔐 AUTHENTICATION

### Login Endpoint
```
POST /accounts/login/
```

**Request Body:**
```json
{
  "username": "handler_username",
  "password": "handler_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "handler_username",
    "email": "handler@fagierrands.com",
    "user_type": "handler",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Authentication Header for All Requests:**
```
Authorization: Bearer {access_token}
```

---

## 📊 DASHBOARD SECTIONS

### 1. OVERVIEW / HOME PAGE

#### Get Assistant Statistics
```
GET /accounts/assistants/stats/
```

**Response:**
```json
{
  "total_assistants": 45,
  "verified": 30,
  "pending": 10,
  "rejected": 3,
  "not_submitted": 2,
  "online_now": 15,
  "available_for_orders": 12
}
```

**UI Components:**
- 📈 Total Assistants Card (45)
- ✅ Verified Riders Card (30)
- ⏳ Pending Verifications Card (10) - Clickable, navigates to verification page
- ❌ Rejected Card (3)
- 🟢 Online Now Card (15)
- 🚀 Available for Orders Card (12)

---

### 2. RIDER VERIFICATION PAGE

#### Get Pending Verifications
```
GET /accounts/admin/verifications/?status=pending
```

**Query Parameters:**
- `status`: `pending` | `verified` | `rejected` (optional)

**Response:**
```json
[
  {
    "id": 1,
    "user": {
      "id": 25,
      "username": "rider_john",
      "email": "john@example.com",
      "phone_number": "+254712345678",
      "first_name": "John",
      "last_name": "Doe"
    },
    "full_name": "John Doe",
    "id_number": "12345678",
    "address": "123 Nairobi Street",
    "area_of_operation": "Nairobi CBD",
    "driving_license_number": "DL123456",
    "selfie_url": "https://lmwloxheulmybtrnfobz.supabase.co/storage/v1/object/public/user-uploads/rider_docs/25/selfie_1234567890.jpg",
    "id_front_url": "https://lmwloxheulmybtrnfobz.supabase.co/storage/v1/object/public/user-uploads/rider_docs/25/id_front_1234567890.jpg",
    "id_back_url": "https://lmwloxheulmybtrnfobz.supabase.co/storage/v1/object/public/user-uploads/rider_docs/25/id_back_1234567890.jpg",
    "driving_license_url": "https://lmwloxheulmybtrnfobz.supabase.co/storage/v1/object/public/user-uploads/rider_docs/25/driving_license_1234567890.jpg",
    "status": "pending",
    "submitted_at": "2026-05-25T10:30:00Z",
    "reviewed_at": null,
    "rejection_reason": null
  }
]
```

#### Get Single Verification Details
```
GET /accounts/admin/verifications/{id}/
```

**Response:** Same as single item above

#### Approve Rider
```
PATCH /accounts/admin/verifications/{id}/update/
```

**Request Body:**
```json
{
  "status": "verified"
}
```

**Response:**
```json
{
  "id": 1,
  "status": "verified",
  "reviewed_at": "2026-05-25T14:30:00Z",
  "message": "Rider verified successfully. SMS notification sent."
}
```

#### Reject Rider
```
PATCH /accounts/admin/verifications/{id}/update/
```

**Request Body:**
```json
{
  "status": "rejected",
  "rejection_reason": "ID document is not clear. Please resubmit."
}
```

**Response:**
```json
{
  "id": 1,
  "status": "rejected",
  "reviewed_at": "2026-05-25T14:30:00Z",
  "rejection_reason": "ID document is not clear. Please resubmit.",
  "message": "Rider rejected. SMS notification sent."
}
```

**UI Components:**
- 📋 List of pending verifications (cards or table)
- 🖼️ Image viewer for documents (selfie, ID front, ID back, license)
- ✅ Approve button
- ❌ Reject button with reason textarea
- 🔍 Filter by status (pending/verified/rejected)
- 📱 Display rider contact info
- 📍 Show area of operation

---

### 3. ALL RIDERS PAGE

#### Get All Riders
```
GET /accounts/user/list/?user_type=assistant
```

**Query Parameters:**
- `user_type`: `assistant` (required for riders)
- `is_verified`: `true` | `false` (optional)
- `is_online`: `true` | `false` (optional)

**Response:**
```json
[
  {
    "id": 25,
    "username": "rider_john",
    "email": "john@example.com",
    "phone_number": "+254712345678",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "assistant",
    "is_verified": true,
    "is_online": true,
    "phone_verified": true,
    "created_at": "2026-05-20T10:00:00Z",
    "profile": {
      "wallet_points": 150,
      "wallet_balance": "2500.00",
      "plate_number": "KAA 123B",
      "bike_type": "Motorcycle",
      "bike_color": "Red"
    }
  }
]
```

#### Get Single Rider Details
```
GET /accounts/user/{id}/
```

**Response:** Same as single item above

#### Get Rider Dashboard Stats
```
GET /accounts/assistant/dashboard-stats/
```
(Note: This requires the rider's token, but handlers can view it if they have the rider's ID)

**Response:**
```json
{
  "total_orders": 45,
  "completed_orders": 40,
  "cancelled_orders": 3,
  "in_progress_orders": 2,
  "total_earnings": "45000.00",
  "wallet_balance": "2500.00",
  "wallet_points": 150,
  "average_rating": 4.7,
  "total_reviews": 38
}
```

**UI Components:**
- 📊 Table/Grid of all riders
- 🔍 Search by name, phone, email
- 🎯 Filter by: verified status, online status
- 👤 View rider profile (modal or page)
- 📈 View rider statistics
- 🚫 Deactivate/Activate rider
- 📱 Contact rider (call/SMS)

---

### 4. CLIENTS PAGE

#### Get Handler's Assigned Clients
```
GET /accounts/handler/clients/
```

**Response:**
```json
[
  {
    "id": 10,
    "username": "client_jane",
    "email": "jane@example.com",
    "phone_number": "+254723456789",
    "first_name": "Jane",
    "last_name": "Smith",
    "user_type": "user",
    "is_verified": true,
    "phone_verified": true,
    "created_at": "2026-05-15T08:00:00Z",
    "profile": {
      "wallet_points": 50,
      "wallet_balance": "1000.00",
      "address": "456 Westlands, Nairobi"
    },
    "account_manager": {
      "id": 1,
      "username": "handler_john",
      "first_name": "John",
      "last_name": "Handler"
    }
  }
]
```

#### Assign Account Manager to Client
```
PATCH /accounts/user/{client_id}/assign-account-manager/
```

**Request Body:**
```json
{
  "account_manager_id": 1
}
```

**Response:**
```json
{
  "message": "Account manager assigned successfully",
  "client": {
    "id": 10,
    "username": "client_jane",
    "account_manager": {
      "id": 1,
      "username": "handler_john"
    }
  }
}
```

**UI Components:**
- 📋 List of assigned clients
- 👤 View client profile
- 📊 View client order history
- 🔄 Reassign to another handler
- 📱 Contact client

---

### 5. ORDERS MANAGEMENT PAGE

#### Get All Orders
```
GET /orders/
```

**Query Parameters:**
- `status`: `pending` | `assigned` | `in_progress` | `completed` | `cancelled`
- `client`: client_user_id
- `assistant`: rider_user_id
- `order_type`: `shopping` | `pickup_delivery`

**Response:**
```json
[
  {
    "id": 100,
    "title": "Grocery Shopping",
    "description": "Buy items from Carrefour",
    "order_type": "shopping",
    "status": "in_progress",
    "client": {
      "id": 10,
      "username": "client_jane",
      "phone_number": "+254723456789"
    },
    "assistant": {
      "id": 25,
      "username": "rider_john",
      "phone_number": "+254712345678"
    },
    "price": "500.00",
    "assistant_items_total": "450.00",
    "pickup_address": "Carrefour Westlands",
    "delivery_address": "456 Westlands, Nairobi",
    "release_code": "123456",
    "created_at": "2026-05-25T10:00:00Z",
    "assigned_at": "2026-05-25T10:05:00Z",
    "started_at": "2026-05-25T10:10:00Z",
    "completed_at": null
  }
]
```

#### Get Single Order Details
```
GET /orders/{id}/
```

**Response:** Same as single item above + additional fields:
```json
{
  "id": 100,
  "shopping_items": [
    {
      "id": 1,
      "name": "Milk",
      "quantity": 2,
      "estimated_price": "150.00"
    }
  ],
  "images": [
    {
      "id": 1,
      "image_url": "https://supabase.co/.../receipt.jpg",
      "image_type": "receipt",
      "uploaded_at": "2026-05-25T10:15:00Z"
    }
  ],
  "review": {
    "rating": 5,
    "comment": "Excellent service!",
    "created_at": "2026-05-25T11:00:00Z"
  }
}
```

#### Assign Rider to Order
```
PATCH /orders/{id}/assign/
```

**Request Body:**
```json
{
  "assistant_id": 25
}
```

**Response:**
```json
{
  "message": "Rider assigned successfully. SMS sent to rider and client.",
  "order": {
    "id": 100,
    "status": "assigned",
    "assistant": {
      "id": 25,
      "username": "rider_john"
    }
  }
}
```

#### Update Order Status
```
PATCH /orders/{id}/update-status/
```

**Request Body:**
```json
{
  "status": "completed"
}
```

**Response:**
```json
{
  "message": "Order status updated successfully",
  "order": {
    "id": 100,
    "status": "completed",
    "completed_at": "2026-05-25T11:00:00Z"
  }
}
```

**UI Components:**
- 📊 Orders table/grid
- 🔍 Search by order ID, client, rider
- 🎯 Filter by status, order type, date range
- 👁️ View order details (modal)
- 🔄 Assign/Reassign rider
- 📱 Contact client/rider
- 🖼️ View uploaded images (receipts)
- ⭐ View reviews
- 📍 Track order location (if tracking enabled)

---

### 6. ANALYTICS / REPORTS PAGE

#### Get Platform Statistics
```
GET /accounts/assistants/stats/
```
(Already covered above)

**Additional Metrics to Display:**
- 📈 Total orders today/week/month
- 💰 Total revenue today/week/month
- 👥 Active riders today
- 🛒 Orders by type (shopping vs pickup/delivery)
- ⭐ Average platform rating
- 📊 Top performing riders
- 📉 Cancelled orders rate

**UI Components:**
- 📊 Charts (line, bar, pie)
- 📅 Date range selector
- 📥 Export reports (Excel/PDF)
- 🔄 Real-time updates

---

## 🎨 UI/UX DESIGN SPECIFICATIONS

### Color Scheme
- **Primary:** #FF6B35 (Orange - FagiErrands brand)
- **Secondary:** #004E89 (Blue)
- **Success:** #28A745 (Green)
- **Warning:** #FFC107 (Yellow)
- **Danger:** #DC3545 (Red)
- **Background:** #F8F9FA (Light gray)
- **Text:** #212529 (Dark gray)

### Layout
- **Sidebar Navigation:**
  - 🏠 Dashboard
  - 🚴 Riders
  - ✅ Verify Riders (with badge showing pending count)
  - 👥 Clients
  - 📦 Orders
  - 📊 Analytics
  - ⚙️ Settings
  - 🚪 Logout

- **Top Bar:**
  - 🔔 Notifications (new orders, pending verifications)
  - 👤 User profile dropdown
  - 🌙 Dark mode toggle

### Responsive Design
- Mobile-first approach
- Breakpoints: 320px, 768px, 1024px, 1440px
- Collapsible sidebar on mobile
- Touch-friendly buttons (min 44px)

### Key Features
- 🔄 Real-time updates (WebSocket for new orders/verifications)
- 📱 SMS integration display
- 🖼️ Image lightbox for document viewing
- 📊 Interactive charts (Chart.js or Recharts)
- 🔍 Advanced search and filters
- 📄 Pagination (20 items per page)
- ⚡ Loading states and skeletons
- ✅ Success/Error toast notifications
- 🔐 Role-based access control

---

## 🔔 NOTIFICATIONS & REAL-TIME FEATURES

### WebSocket Connection (Optional)
```
wss://fagierrands.onrender.com/ws/handler/{handler_id}/
```

**Events:**
- `new_verification`: New rider submitted documents
- `new_order`: New order created
- `order_assigned`: Order assigned to rider
- `order_completed`: Order completed
- `rider_online`: Rider came online
- `rider_offline`: Rider went offline

---

## 🛠️ TECHNICAL REQUIREMENTS

### Frontend Stack (Recommended)
- **Framework:** React.js or Next.js
- **State Management:** Redux Toolkit or Zustand
- **HTTP Client:** Axios
- **UI Library:** Material-UI, Ant Design, or Tailwind CSS
- **Charts:** Chart.js or Recharts
- **Forms:** React Hook Form + Yup validation
- **Date Handling:** date-fns or Day.js
- **Image Viewer:** react-image-lightbox

### Key Functionalities
1. **Authentication:**
   - Login form with validation
   - Store JWT tokens in localStorage/sessionStorage
   - Auto-refresh tokens before expiry
   - Logout and clear tokens

2. **API Integration:**
   - Axios interceptor for auth headers
   - Error handling (401, 403, 500)
   - Loading states
   - Retry logic for failed requests

3. **Data Management:**
   - Cache frequently accessed data
   - Optimistic updates
   - Pagination handling
   - Search debouncing (300ms)

4. **Image Handling:**
   - Lazy loading
   - Lightbox for full-screen view
   - Zoom in/out functionality
   - Download option

5. **Notifications:**
   - Toast notifications (react-toastify)
   - Badge counts on sidebar
   - Browser notifications (optional)

---

## 📝 SAMPLE CODE SNIPPETS

### API Service (axios-config.js)
```javascript
import axios from 'axios';

const API_BASE_URL = 'https://fagierrands.onrender.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh or logout
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### API Calls Example
```javascript
// Get pending verifications
export const getPendingVerifications = () => 
  api.get('/accounts/admin/verifications/?status=pending');

// Approve rider
export const approveRider = (id) => 
  api.patch(`/accounts/admin/verifications/${id}/update/`, { status: 'verified' });

// Reject rider
export const rejectRider = (id, reason) => 
  api.patch(`/accounts/admin/verifications/${id}/update/`, { 
    status: 'rejected',
    rejection_reason: reason 
  });

// Get all riders
export const getAllRiders = (filters = {}) => 
  api.get('/accounts/user/list/', { params: { user_type: 'assistant', ...filters } });

// Get orders
export const getOrders = (filters = {}) => 
  api.get('/orders/', { params: filters });

// Assign rider to order
export const assignRider = (orderId, riderId) => 
  api.patch(`/orders/${orderId}/assign/`, { assistant_id: riderId });
```

---

## ✅ TESTING CHECKLIST

### Authentication
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Token refresh on expiry
- [ ] Logout clears tokens
- [ ] Protected routes redirect to login

### Rider Verification
- [ ] View pending verifications
- [ ] View rider documents (all 4 images)
- [ ] Approve rider (success message + SMS sent)
- [ ] Reject rider with reason (success message + SMS sent)
- [ ] Filter by status (pending/verified/rejected)

### Riders Management
- [ ] View all riders
- [ ] Search riders by name/phone
- [ ] Filter by verified/online status
- [ ] View rider profile
- [ ] View rider statistics

### Orders Management
- [ ] View all orders
- [ ] Filter by status/type
- [ ] View order details
- [ ] Assign rider to order
- [ ] Update order status
- [ ] View order images

### Analytics
- [ ] View dashboard statistics
- [ ] Charts render correctly
- [ ] Date range filtering works

---

## 🚀 DEPLOYMENT NOTES

- API is already deployed at: `https://fagierrands.onrender.com/api`
- All endpoints are live and functional
- SMS notifications are automatically sent on rider approval/rejection
- Images are stored in Supabase cloud storage
- Database is PostgreSQL on Render

---

## 📞 SUPPORT

For API issues or questions:
- Check API documentation: `/api/swagger/` or `/api/redoc/`
- Test endpoints with Postman
- Contact backend team for assistance

---

**END OF SPECIFICATION**
