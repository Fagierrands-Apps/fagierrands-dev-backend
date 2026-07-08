# FagiErrands Backend System - Deep Architecture Analysis

## 📋 System Overview

**FagiErrands** is a Django-based errand delivery platform that connects users with riders (assistants) for various delivery and service tasks.

### Tech Stack
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL (Dev/Prod) + SQLite (Testing)
- **Authentication**: JWT (Simple JWT)
- **Server**: cPanel with Passenger WSGI
- **Deployment**: GitHub Actions + FTPS to cPanel
- **Storage**: Supabase (file storage)
- **SMS**: TextPie API
- **Email**: Brevo SMTP
- **Payments**: NCBA M-Pesa Till/Paybill
- **Maps**: Google Maps API
- **Task Queue**: Celery + Redis
- **WebSockets**: Django Channels + Redis

---

## 🏗️ Architecture Components

### 1. Core Django Apps

#### **accounts/** - User Management
- Custom User model extending AbstractUser
- User types: `user`, `assistant` (rider), `handler`, `admin`, `vendor`
- Phone number verification (OTP via SMS)
- Email verification with tokens
- Profile management with wallet points
- Rider verification system (documents, vehicle info)
- Referral system

**Key Models:**
- `User` - Extended auth user with phone & user_type
- `Profile` - Wallet points, ratings, stats
- `AssistantVerification` - Rider onboarding
- `WalletTransaction` - Points credits/debits
- `EmailVerification` / `OTPVerification`

#### **orders/** - Core Business Logic
- Order lifecycle management (Draft → Completed)
- Multiple order types: Regular delivery, Cargo, Handyman services, Banking, Shopping
- Real-time tracking with GPS waypoints
- Payment processing (NCBA M-Pesa)
- Rider assignment algorithm
- Rating & feedback system
- SOS alerts for rider safety

**Key Models:**
- `Order` - Main order entity (8 statuses)
- `OrderType` - Parcel, Cargo, etc.
- `Payment` - Transaction records
- `OrderTracking` - GPS tracking history
- `CargoDeliveryDetails` - Heavy cargo specifics
- `HandymanOrder` - Home service orders
- `SOSAlert` - Emergency alerts
- `ShoppingItem` - Shopping list items
- `BankingOrder` - Banking errands

**Order Status Flow:**
```
Draft → Pending → Assigned → InTransit → PaymentPending → Completed
                                    ↓
                                Cancelled
```

#### **locations/** - Geographic Services
- Address autocomplete (Google Maps)
- Coordinate validation
- Distance calculation
- Saved locations per user

**Key Models:**
- `Location` - User saved addresses

#### **notifications/** - Push & In-App
- Real-time notifications
- Push notifications (FCM ready)
- SMS notifications via TextPie
- Email notifications

**Key Models:**
- `Notification` - In-app notification records

#### **admin_dashboard/** - Business Intelligence
- Dashboard statistics
- Order analytics
- User metrics
- Revenue tracking
- Handler (dispatcher) views

#### **marketplace/** (Planned)
- Vendor listings
- Product catalog
- E-commerce integration

---

## 🔐 Authentication & Security

### JWT Authentication
- Access Token: 1 day expiry (configurable)
- Refresh Token: 7 days expiry (configurable)
- Token rotation on refresh
- Blacklisting on logout

### User Registration Flow
1. User registers with email/phone
2. OTP sent via TextPie SMS
3. User verifies OTP
4. Account activated
5. Email verification (optional)

### Rider Onboarding
1. User registers as `assistant`
2. Submits verification docs:
   - Vehicle type & registration
   - Driver's license
   - ID number
3. Admin reviews and approves
4. Rider can receive assignments

---

## 💳 Payment System

### NCBA M-Pesa Integration
- **Till Number**: 852054
- **Paybill Number**: 880100
- **Methods**: STK Push (automated), Manual entry
- **Callback URL**: Webhook for payment confirmation

### Payment Flow
1. Order created (status: `Pending`)
2. User initiates payment
3. STK Push sent to phone
4. User enters M-Pesa PIN
5. NCBA callback received
6. Payment verified
7. Order status → `Assigned` or `InTransit`

### Wallet System
- Users earn points on completed orders
- Points redeemable for discounts
- Referral bonuses
- Transaction history tracked

---

## 🚚 Order Management

### Order Creation
```python
POST /api/orders/
{
  "order_type": "parcel",
  "pickup_address": "Nairobi CBD",
  "pickup_lat": -1.286389,
  "pickup_lng": 36.817223,
  "delivery_address": "Westlands",
  "delivery_lat": -1.268655,
  "delivery_lng": 36.806027,
  "receiver_name": "John Doe",
  "receiver_phone": "+254712345678",
  "item_description": "Documents",
  "payment_method": "mpesa"
}
```

### Automatic Pricing
```python
distance_km = calculate_distance(pickup, delivery)
base_price = settings.BASE_PRICE_PER_KM * distance_km
extra_charges = 0  # Weight, urgency, etc.
total_price = base_price + extra_charges
```

### Rider Assignment
**Intelligent Assignment Algorithm:**
1. Find available riders within radius
2. Check rider capacity
3. Consider rider ratings
4. Prioritize proximity to pickup
5. Assign and notify rider
6. Rider accepts/rejects (30s timeout)

### Real-Time Tracking
- GPS updates every 30 seconds
- Waypoint recording
- ETA calculation
- Live location sharing with user

---

## 📂 File Storage - Supabase

### Configuration
```python
SUPABASE_URL = 'https://lmwloxheulmybtrnfobz.supabase.co'
SUPABASE_BUCKET_NAME = 'user-uploads'
```

### Supported Files
- Order images (item photos)
- Cargo photos
- Rider documents (ID, license, registration)
- Profile avatars
- Proof of delivery photos

---

## 📱 SMS Notifications - TextPie

### Use Cases
- OTP verification codes
- Order confirmation
- Rider assignment notification
- Delivery completion
- Payment receipts

### Configuration
```python
TEXTPIE_API_KEY = 'M176esJ...'
TEXTPIE_SERVICE_ID = '77'
TEXTPIE_SHORTCODE = 'FagiErrands'
```

---

## 🚀 Deployment Architecture

### Development Server
- **URL**: https://dev.fagierrands.com
- **Server**: cPanel (distinc3 hosting)
- **Path**: `/dev.fagierrands.com/`
- **Database**: PostgreSQL (`distinc3_dev`)
- **Branch**: `main`
- **Auto-Deploy**: On push to `main`

### Production Server
- **URL**: https://api.errandserver.fagierrands.com
- **Server**: cPanel (distinc3 hosting)
- **Path**: `/home3/distinc3/fagierrandsbackendapi/`
- **Database**: PostgreSQL (separate from dev)
- **Branch**: `production`
- **Deploy**: Manual (planned auto-deploy)

### GitHub Actions CI/CD
```yaml
Trigger: Push to main
Steps:
  1. Checkout code
  2. Deploy via FTPS
  3. Exclude: .git, .env, db.sqlite3, logs, media
  4. Upload to cPanel
  5. Passenger auto-restarts
```

### Protected Files (Never Overwritten)
- `.env` - Environment variables
- `db.sqlite3` - Database
- `logs/` - Application logs
- `media/` - User uploads

---

## 📊 Database Schema

### Key Relationships
```
User (1) ───< (M) Order
User (1) ───< (M) Profile
User (1) ───< (M) WalletTransaction

Order (1) ───< (M) Payment
Order (1) ───< (M) OrderImage
Order (1) ───< (M) OrderTracking
Order (1) ───< (1) OrderRating
Order (1) ───< (1) CargoDeliveryDetails
Order (M) ───> (1) OrderType
Order (M) ───> (1) User (assistant)

OrderTracking (1) ───< (M) TrackingWaypoint
OrderTracking (1) ───< (M) TrackingLocationHistory
```

### Indexes & Optimizations
- `order_number` - Unique, indexed
- `phone_number` - Unique, indexed (User)
- `status` - Indexed (Order, Payment)
- Composite index on `(user, status)` for queries

---

## 🔌 API Endpoints Structure

### Authentication
- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/verify-otp/` - OTP verification
- `POST /api/accounts/login/` - JWT login
- `POST /api/accounts/token/refresh/` - Refresh token
- `POST /api/accounts/logout/` - Token blacklist

### Orders (User)
- `GET /api/orders/` - List user orders
- `POST /api/orders/` - Create order
- `GET /api/orders/{id}/` - Order details
- `POST /api/orders/{id}/cancel/` - Cancel order
- `POST /api/orders/{id}/rate/` - Rate rider

### Orders (Rider)
- `GET /api/orders/available/` - Available orders
- `POST /api/orders/{id}/accept/` - Accept order
- `POST /api/orders/{id}/pickup/` - Mark picked up
- `POST /api/orders/{id}/deliver/` - Mark delivered
- `POST /api/orders/{id}/track/` - Update GPS location
- `POST /api/orders/sos/` - Emergency alert

### Payments
- `POST /api/orders/payments/initiate/` - Start payment
- `POST /api/orders/payments/ncba/callback/` - NCBA webhook
- `GET /api/orders/payments/{id}/status/` - Payment status

### Locations
- `POST /api/locations/autocomplete/` - Address search
- `POST /api/locations/validate/` - Coordinate validation
- `POST /api/locations/distance/` - Distance calculation

### Dashboard (Handler/Admin)
- `GET /dashboard/stats/` - Overall statistics
- `GET /dashboard/orders/` - All orders
- `GET /dashboard/riders/` - Rider management
- `GET /dashboard/users/` - User management

---

## 🎯 Business Rules

### Order Rules
1. **Minimum Order Amount**: KES 100
2. **Base Price**: KES 50/km (configurable)
3. **Payment Required**: Before rider assignment (or COD enabled)
4. **Cancellation**: Free before rider assigned, fee after pickup
5. **Rider Assignment Timeout**: 30 seconds to accept
6. **Delivery Confirmation**: OTP or signature required

### Pricing Rules
```python
# Base calculation
base_price = distance_km * BASE_PRICE_PER_KM

# Cargo surcharge
if order_type == 'cargo':
    if weight > 50:  # kg
        extra_charges += 500
    if need_helpers:
        extra_charges += (helpers_count * 300)

# Time-based surge (future)
if peak_hours:
    total_price *= 1.3  # 30% surge

# Final price
total_price = base_price + extra_charges
```

### Wallet Points
- **Earning Rate**: 1 point per KES 100 spent
- **Redemption Rate**: 1 point = KES 1
- **Maximum Redemption**: 50% of order value
- **Expiry**: Points expire after 1 year

### Referral Program
- **Referrer Bonus**: 100 points
- **Referee Bonus**: 50 points
- **Conditions**: Referee must complete first order

---

## 🛠️ Core Utilities

### `/core/utils.py`
- `normalize_phone_number()` - Standardize to +254 format
- `generate_order_number()` - Unique order IDs
- `calculate_distance()` - Haversine formula
- `generate_otp()` - 6-digit codes

### `/core/sms_service.py`
- `send_sms()` - TextPie integration
- `send_otp()` - OTP delivery
- Template support for messages

### `/core/ncba_payment.py`
- `initiate_stk_push()` - Trigger payment
- `query_transaction_status()` - Check payment
- `verify_callback()` - Validate webhooks

---

## 📈 Monitoring & Logging

### Log Files
- `logs/django.log` - Application logs
- `stderr.log` - Error tracking

### Logging Levels
- **INFO**: Normal operations
- **WARNING**: Potential issues
- **ERROR**: Failures requiring attention
- **DEBUG**: Development debugging (only in DEV)

### Key Metrics Tracked
- Order creation rate
- Payment success rate
- Rider response time
- Average delivery time
- User retention
- Revenue per order

---

## ⚙️ Environment Variables

### Required Variables
```bash
# Core
DEBUG=True/False
SECRET_KEY=<django-secret>
ALLOWED_HOSTS=domain.com

# Database
DB_NAME=distinc3_dev
DB_USER=distinc3_dev-user
DB_PASSWORD=<password>
DB_HOST=localhost
DB_PORT=5432

# APIs
GOOGLE_MAPS_API_KEY=<key>
TEXTPIE_API_KEY=<key>
SUPABASE_URL=<url>
SUPABASE_KEY=<key>

# Payment
NCBA_USERNAME=<username>
NCBA_PASSWORD=<password>
NCBA_TILL_NO=852054
```

---

## 🔧 Development Setup

### Local Development
```bash
# Clone repository
git clone https://github.com/Fagierrands-Apps/fagierrands-dev-backend.git
cd fagierrands-dev-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.dev .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Access at http://localhost:8000
```

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Rollback migration
python manage.py migrate app_name 0001_previous_migration
```

---

## 🚨 Known Issues & Considerations

### Current Limitations
1. **Queue System**: Queue position field deprecated, needs proper queuing
2. **Rider Assignment**: Basic algorithm, needs ML-based optimization
3. **Payment Callbacks**: Single endpoint, needs idempotency handling
4. **WebSocket Scaling**: Channels needs Redis cluster for production scale
5. **File Storage**: Supabase bucket has size limits

### Security Considerations
1. **API Keys**: Hardcoded in settings.py (should use environment only)
2. **CORS**: Wildcard allowed in dev (restrict in production)
3. **Rate Limiting**: Not implemented (add DRF throttling)
4. **CSRF**: Disabled for API (ensure JWT validation is strict)

### Performance Optimizations Needed
1. Database query optimization (select_related, prefetch_related)
2. Redis caching for frequently accessed data
3. Celery for async tasks (email, SMS)
4. Database connection pooling
5. Static file compression (WhiteNoise configured)

---

## 📚 Documentation Links

- **Swagger API Docs**: `/swagger/`
- **ReDoc API Docs**: `/redoc/`
- **Admin Panel**: `/admin/`
- **GitHub Repo**: https://github.com/Fagierrands-Apps/fagierrands-dev-backend

---

## 🎯 Next Steps / Roadmap

### Immediate Priorities
- [ ] Implement proper queue system for orders
- [ ] Add rate limiting to API endpoints
- [ ] Setup Celery for async tasks
- [ ] Add comprehensive API tests
- [ ] Implement payment idempotency
- [ ] Add rider earnings tracking
- [ ] Setup monitoring (Sentry/New Relic)

### Future Features
- [ ] Multi-stop deliveries
- [ ] Scheduled deliveries
- [ ] Subscription plans
- [ ] Corporate accounts
- [ ] Driver app (separate mobile app)
- [ ] Advanced analytics dashboard
- [ ] AI-powered route optimization

---

## 👥 Contact & Support

- **Repository Issues**: https://github.com/Fagierrands-Apps/fagierrands-dev-backend/issues
- **Email**: support@fagierrands.com
- **Documentation**: See `/reports/` and `/scripts_and_docs/` directories

---

**Last Updated**: June 29, 2026
**System Status**: ✅ Active Development
**Current Version**: 1.0
