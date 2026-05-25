# 🚀 FagiErrands Backend

**Version**: 2.0.0  
**Last Updated**: 2026-05-25

A Django REST API backend for FagiErrands - an on-demand errand service platform connecting clients with verified riders.

---

## 📚 Documentation

### Essential Reading (in order)

1. **[CURRENT_STATUS.md](CURRENT_STATUS.md)** - Start here! Current state of the project
2. **[FAGIERRANDS_COMPLETE_JOURNEY.md](FAGIERRANDS_COMPLETE_JOURNEY.md)** - Complete user journey with all endpoints
3. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - How to deploy to Render
4. **[API_ENDPOINTS_COMPLETE.md](API_ENDPOINTS_COMPLETE.md)** - API reference

---

## ✨ Key Features

### 🎉 NEW: One-Step Rider Registration
- Register with all documents in single request
- Automatic upload to Supabase cloud storage
- Organized folder structure per rider
- SMS verification integrated
- Handler approval workflow

### 📦 Complete Order Management
- Shopping errands
- Pickup & delivery
- Real-time tracking
- Release code security
- Image uploads (receipts, etc.)
- Reviews & ratings

### 📱 SMS Notifications
- 8 SMS per order journey
- TextPie API integration
- OTP verification
- Order status updates

### ☁️ Supabase Storage
- Cloud-based image storage
- Public URLs for easy access
- Organized folder structure
- Automatic backups

### 🔐 Security
- Phone verification required
- Document verification for riders
- Release code for order completion
- JWT authentication
- Handler approval system

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL
- Supabase account
- TextPie API key

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/fagierrands-dev-backend.git
cd fagierrands-dev-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/fagierrands

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# SMS
TEXTPIE_API_KEY=your-textpie-api-key

# M-Pesa (optional)
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
```

---

## 📡 API Endpoints

### Authentication
```
POST   /api/accounts/register/              - Register client/handler
POST   /api/accounts/rider/register/        - Register rider with documents (NEW!)
POST   /api/accounts/verify-phone/          - Verify phone number
POST   /api/accounts/login/                 - Login
POST   /api/accounts/token/refresh/         - Refresh JWT token
```

### Rider Management
```
GET    /api/accounts/pending-verifications/ - List pending riders
PATCH  /api/accounts/assistant-verification/{id}/approve/ - Approve rider
GET    /api/accounts/available-assistants/  - List available riders
```

### Orders
```
POST   /api/orders/shopping/                - Create shopping order
POST   /api/orders/pickup-delivery/         - Create pickup/delivery order
GET    /api/orders/{id}/                    - View order details
PATCH  /api/orders/{id}/assign/             - Assign rider
PATCH  /api/orders/{id}/update-status/      - Update status
POST   /api/orders/{id}/images/             - Upload images
POST   /api/orders/{id}/review/             - Leave review
```

See [API_ENDPOINTS_COMPLETE.md](API_ENDPOINTS_COMPLETE.md) for full API documentation.

---

## 🗄️ Database Schema

### Key Models

**User**
- username, email, phone_number
- user_type: `user` | `assistant` | `handler`
- is_phone_verified, wallet_points

**AssistantVerification** (NEW!)
- full_name, id_number, address
- area_of_operation, driving_license_number
- selfie_url, id_front_url, id_back_url, driving_license_url (Supabase)
- status: `pending` | `approved` | `rejected`

**Order**
- client, assistant, handler (ForeignKeys)
- title, description, status
- price, assistant_items_total
- release_code (6 digits)
- pickup_address, delivery_address
- created_at, assigned_at, started_at, completed_at

---

## ☁️ Supabase Storage Structure

```
user-uploads/  (bucket)
├── rider_docs/
│   └── {user_id}/
│       ├── selfie_{timestamp}.jpg
│       ├── id_front_{timestamp}.jpg
│       ├── id_back_{timestamp}.jpg
│       └── driving_license_{timestamp}.jpg
│
├── order_images/
│   └── {order_id}/
│       └── receipt_{timestamp}.jpg
│
└── profile_pictures/
    └── {user_id}_{timestamp}.jpg
```

---

## 📱 SMS Flow

1. **Account Verification** - Client/Rider registration
2. **Rider Approval** - Handler approves rider
3. **Order Confirmation** - Client creates order
4. **Rider Assigned** - Handler assigns rider
5. **Order Started** - Rider starts order (includes release code)
6. **Order Completed** - Rider completes order
7. **Payment Confirmation** - Payment successful

**Cost**: ~KSh 6.40 per order (8 SMS × KSh 0.80)

---

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### Test Rider Registration
```bash
curl -X POST http://localhost:8000/api/accounts/rider/register/ \
  -F "username=test_rider" \
  -F "email=test@example.com" \
  -F "password=TestPass123!" \
  -F "password2=TestPass123!" \
  -F "first_name=Test" \
  -F "last_name=Rider" \
  -F "phone_number=+254712345678" \
  -F "full_name=Test Rider Full" \
  -F "id_number=12345678" \
  -F "address=123 Test St" \
  -F "area_of_operation=Nairobi" \
  -F "driving_license_number=DL123456" \
  -F "profile_picture=@/path/to/selfie.jpg" \
  -F "id_front_image=@/path/to/id_front.jpg" \
  -F "id_back_image=@/path/to/id_back.jpg" \
  -F "driving_license_image=@/path/to/license.jpg"
```

---

## 🚀 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

### Quick Deploy to Render

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy to production"
git push origin main

# 2. Render auto-deploys

# 3. Run migrations on Render
python manage.py migrate
python manage.py collectstatic --noinput
```

---

## 📊 Project Status

### ✅ Working
- Client registration & verification
- Rider registration with documents (NEW!)
- Handler approval system
- Order creation & management
- SMS notifications
- Supabase image storage
- Release code security
- Reviews & ratings
- Wallet points

### ⚠️ Needs Attention
- Database connection (deploy to Render to fix)
- Orders URLs temporarily disabled
- Payment integration testing
- Commented code cleanup

See [CURRENT_STATUS.md](CURRENT_STATUS.md) for detailed status.

---

## 🛠️ Tech Stack

- **Framework**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL (Render)
- **Storage**: Supabase
- **SMS**: TextPie API
- **Authentication**: JWT (Simple JWT)
- **Payment**: M-Pesa (planned)
- **Hosting**: Render

---

## 📁 Project Structure

```
fagierrands-dev-backend/
├── accounts/           # User management, authentication
├── orders/             # Order management
├── locations/          # Location services
├── notifications/      # Push notifications
├── marketplace/        # Marketplace features
├── admin_dashboard/    # Admin panel
├── voice/              # Voice features
├── config/             # Django settings
├── docs/               # Documentation
└── requirements.txt    # Dependencies
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

This project is proprietary and confidential.

---

## 📞 Support

For issues or questions:
- Check [FAGIERRANDS_COMPLETE_JOURNEY.md](FAGIERRANDS_COMPLETE_JOURNEY.md) for detailed flow
- Check [CURRENT_STATUS.md](CURRENT_STATUS.md) for known issues
- Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment help

---

## 🎉 What's New in v2.0.0

- ✨ **One-step rider registration** with document upload
- ☁️ **Supabase cloud storage** for all images
- 📁 **Organized folder structure** per user/order
- 📱 **Complete SMS flow** with 8 notification types
- 🔐 **Enhanced security** with release codes
- 📚 **Comprehensive documentation** of entire journey

---

**Built with ❤️ for FagiErrands**
