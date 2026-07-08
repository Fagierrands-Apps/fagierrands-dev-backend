# FagiErrands System - Quick Technical Reference

## 🔥 Critical Information

### Deployment
- **Dev Server**: https://dev.fagierrands.com (Auto-deploy on push to `main`)
- **Production**: https://api.errandserver.fagierrands.com (Manual deploy)
- **Hosting**: cPanel with Passenger WSGI
- **CI/CD**: GitHub Actions → FTPS Upload → Auto-restart

### Database
- **Dev**: PostgreSQL `distinc3_dev` on localhost
- **Prod**: PostgreSQL (separate database)
- **Credentials**: See `.env.dev` or `.env.cpanel`

### Key Services
| Service | Purpose | Provider |
|---------|---------|----------|
| SMS | OTP verification | TextPie |
| Email | Verification emails | Brevo SMTP |
| Payment | M-Pesa | NCBA Till/Paybill |
| Storage | Images/Documents | Supabase |
| Maps | Geocoding/Distance | Google Maps API |
| Push | Notifications | FCM (ready) |

---

## 📊 System Flow Diagram

```
┌─────────────┐
│   Client    │ (Mobile App / Web)
└──────┬──────┘
       │
       ↓ HTTPS/WSS
┌─────────────────────────────┐
│    Django REST API          │
│  - JWT Authentication       │
│  - DRF Views & Serializers  │
│  - WebSocket (Channels)     │
└──────┬──────────────────────┘
       │
       ↓
┌──────────────────────────────────────────┐
│           Core Services                   │
├──────────┬──────────┬─────────┬──────────┤
│  Orders  │ Payments │ SMS     │ Storage  │
│  Logic   │ (NCBA)   │(TextPie)│(Supabase)│
└──────────┴──────────┴─────────┴──────────┘
       │
       ↓
┌─────────────────┐      ┌─────────────┐
│   PostgreSQL    │◄────►│    Redis    │
│   (Database)    │      │  (Cache +   │
│                 │      │   Celery)   │
└─────────────────┘      └─────────────┘
```

---

## 🗂️ App Structure

```
fagierrands-dev-backend/
│
├── accounts/           # User management, auth, profiles
│   ├── models.py      # User, Profile, Verification
│   ├── views.py       # Registration, login, OTP
│   └── urls.py        # /api/accounts/*
│
├── orders/            # Order management (MAIN APP)
│   ├── models.py      # 25+ models (Order, Payment, etc.)
│   ├── views.py       # Order CRUD
│   ├── views_handler.py      # Handler dashboard
│   ├── views_handler_rider.py # Rider assignment
│   ├── views_payment_ncba.py  # M-Pesa integration
│   ├── views_errand.py        # Errand-specific logic
│   ├── ncba_service.py        # Payment service layer
│   └── urls.py        # /api/orders/*
│
├── locations/         # Geographic services
│   ├── models.py      # Location (saved addresses)
│   └── views.py       # Autocomplete, distance calc
│
├── notifications/     # Push & in-app notifications
│   ├── models.py      # Notification
│   └── views.py       # List, mark read
│
├── admin_dashboard/   # Business intelligence
│   ├── views.py       # Stats, analytics
│   └── urls.py        # /dashboard/*
│
├── core/              # Shared utilities
│   ├── utils.py       # Phone normalization, distance
│   ├── sms_service.py # TextPie integration
│   └── ncba_payment.py# Payment helpers
│
├── fagierrands/       # Django project settings
│   ├── settings.py    # Main configuration
│   ├── urls.py        # URL routing
│   └── wsgi.py        # WSGI entry (not used on cPanel)
│
├── passenger_wsgi.py  # cPanel WSGI entry point ⚠️
├── requirements.txt   # Python dependencies
├── manage.py          # Django CLI
└── .env.dev           # Environment variables (DEV)
```

---

## 🔑 Key Models Overview

### User Model (`accounts.User`)
```python
- user_type: 'user' | 'assistant' | 'handler' | 'admin' | 'vendor'
- phone_number: Unique, normalized to +254
- email: Optional, with email_verified flag
- is_verified: OTP verified
- profile: OneToOne → Profile
```

### Order Model (`orders.Order`)
```python
Status Flow: Draft → Pending → Assigned → InTransit → PaymentPending → Completed
- user: ForeignKey to User (customer)
- assistant: ForeignKey to User (rider)
- order_type: ForeignKey to OrderType
- pickup/delivery locations: lat/lng + address
- pricing: base_price, extra_charges, total_price
- payment_status: 'pending' | 'initiated' | 'paid' | 'failed'
- timestamps: created_at, assigned_at, delivered_at, etc.
```

### Payment Model (`orders.Payment`)
```python
- order: ForeignKey to Order
- amount, final_amount (after wallet points)
- payment_method: 'ncba' | 'mpesa' | 'card'
- status: 'Pending' | 'Processing' | 'Completed' | 'Failed'
- mpesa_checkout_request_id: STK push tracking
- transaction_reference: NCBA receipt number
```

---

## 🛣️ Critical API Endpoints

### Authentication
```http
POST /api/accounts/register/
POST /api/accounts/verify-otp/
POST /api/accounts/login/
POST /api/accounts/token/refresh/
```

### Order Lifecycle (User)
```http
POST /api/orders/                    # Create order
GET  /api/orders/{id}/               # Get order details
POST /api/orders/{id}/cancel/        # Cancel order
GET  /api/orders/                    # List my orders
```

### Order Lifecycle (Rider)
```http
GET  /api/orders/available/          # Available orders
POST /api/orders/{id}/accept/        # Accept assignment
POST /api/orders/{id}/pickup/        # Mark picked up
POST /api/orders/{id}/deliver/       # Mark delivered
POST /api/orders/{id}/track/         # Update GPS location
POST /api/orders/sos/                # Emergency SOS
```

### Payments
```http
POST /api/orders/payments/initiate/       # Start payment
POST /api/orders/payments/ncba/callback/  # Webhook (NCBA)
GET  /api/orders/payments/{id}/status/    # Check status
```

### Locations
```http
POST /api/locations/autocomplete/    # Address search
POST /api/locations/distance/        # Calculate distance
```

---

## 💻 Common Commands

### Development
```bash
# Start dev server
python manage.py runserver

# Make migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Shell access
python manage.py shell

# Load fixtures
python manage.py loaddata fixtures/order_types.json
```

### Deployment
```bash
# Push to dev
git add .
git commit -m "Your message"
git push origin main  # Auto-deploys to dev.fagierrands.com

# Deploy to production (manual)
git checkout production
git merge main
git push origin production
# Then manually FTP or use deployment script
```

### Testing
```bash
# Run all tests
python manage.py test

# Test specific app
python manage.py test accounts

# Coverage report
coverage run --source='.' manage.py test
coverage report
```

---

## 🔒 Security Checklist

### Environment Variables
- ✅ Never commit `.env` files
- ✅ Use different secrets for dev/prod
- ✅ Rotate keys periodically

### API Security
- ✅ JWT authentication enforced
- ✅ HTTPS only in production
- ⚠️ Add rate limiting (TODO)
- ⚠️ Implement API key rotation
- ✅ CORS configured

### Database
- ✅ Use strong passwords
- ✅ Separate dev/prod databases
- ⚠️ Enable query logging in dev only
- ✅ Regular backups configured

---

## 🐛 Debugging Tips

### Check Logs
```bash
# Django logs
tail -f logs/django.log

# Error logs (cPanel)
tail -f stderr.log

# Passenger restart (cPanel)
touch tmp/restart.txt
```

### Common Issues

**Issue**: "No module named 'fagierrands'"
```bash
# Solution: Check PYTHONPATH in passenger_wsgi.py
sys.path.insert(0, os.path.dirname(__file__))
```

**Issue**: Payment callback not working
```bash
# Solution: Check NCBA_CALLBACK_URL in settings
# Ensure URL is publicly accessible
# Verify webhook signature
```

**Issue**: SMS not sending
```bash
# Solution: Check TextPie credits
# Verify API key is correct
# Check phone number format (+254)
```

**Issue**: Database connection error
```bash
# Solution: Check PostgreSQL is running
sudo systemctl status postgresql
# Verify DB credentials in .env
```

---

## 📞 Quick Contacts

| Component | Value |
|-----------|-------|
| Dev Server | https://dev.fagierrands.com |
| API Docs | https://dev.fagierrands.com/swagger/ |
| Admin Panel | https://dev.fagierrands.com/admin/ |
| GitHub Repo | Fagierrands-Apps/fagierrands-dev-backend |
| SMS Support | TextPie Dashboard |
| Email Support | Brevo Dashboard |

---

## 🎯 Priority Tasks

### High Priority
1. Implement API rate limiting
2. Add payment idempotency checks
3. Setup Celery for async tasks
4. Add comprehensive logging
5. Implement proper error tracking (Sentry)

### Medium Priority
1. Optimize database queries (N+1 issues)
2. Add caching layer (Redis)
3. Improve rider assignment algorithm
4. Add automated tests
5. Setup CI/CD for production

### Low Priority
1. Refactor views (some are too large)
2. Add API versioning
3. Improve documentation
4. Add performance monitoring
5. Implement feature flags

---

**Last Updated**: June 29, 2026  
**Maintained By**: Development Team  
**Status**: 🟢 Active Development
