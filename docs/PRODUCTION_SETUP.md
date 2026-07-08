# 🚀 FagiErrands Backend - Production & Development Setup

**Last Updated:** 2026-06-07  
**Repository:** https://github.com/Fagierrands-Apps/fagierrands-dev-backend

---

## 📋 CURRENT SITUATION OVERVIEW

### Repository Structure
This repository now uses a **TWO-BRANCH STRATEGY**:

| Branch | Purpose | Deployed To | Auto-Deploy |
|--------|---------|-------------|-------------|
| **`main`** | Development/Testing | Not deployed | ❌ No |
| **`production-clean`** | Live Production | cPanel Shared Hosting | ✅ Yes (pending setup) |

---

## 🏗️ ARCHITECTURE

### Production Environment (production-clean branch)
- **Hosting:** cPanel Shared Hosting (LiteSpeed)
- **Domain:** https://fagierrandsbackendapi.distinctivecollections.co.ke
- **Server Path:** `/home3/distinc3/fagierrandsbackendapi`
- **Python Version:** 3.11
- **Server:** LiteSpeed with Passenger WSGI
- **Database:** SQLite3 (production database on server)

### Development Environment (main branch)
- **Status:** Local development only
- **Purpose:** Testing new features before production
- **Database:** SQLite3 (local)

---

## 📂 DEPLOYMENT CONFIGURATION

### cPanel Details
- **Account:** distinc3
- **User ID:** 1223
- **WSGI Entry Point:** `passenger_wsgi.py`
- **Process Limit:** 6 child processes (LSAPI_CHILDREN)
- **Protocol:** FTPS for deployment

### Protected Files (NEVER Overwritten on Deploy)
```
.env                    # Environment variables & secrets
db.sqlite3              # Production database
logs/                   # Server logs
media/                  # User uploaded files
```

### Environment Variables (.env on server)
```bash
# Django
SECRET_KEY=<production-secret>
DEBUG=False
ALLOWED_HOSTS=fagierrandsbackendapi.distinctivecollections.co.ke,api.errandserver.fagierrands.com

# Database (SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# SMS Service (TextPie)
TEXTPIE_API_KEY=M176esJGFImYzBlqk9dgKfjuRXE2U3nyHZQvL4hiAWp08rTxwSNDVabtPO5oCc
TEXTPIE_SERVICE_ID=77
SMS_SENDER=FagiErrands

# NCBA Payment Gateway
NCBA_API_URL=<production-ncba-url>
NCBA_USERNAME=Errand@123
NCBA_PASSWORD=<production-password>
NCBA_PAYBILL=880100
NCBA_TILL_NUMBER=852054
NCBA_CALLBACK_URL=https://fagierrandsbackendapi.distinctivecollections.co.ke/api/orders/payments/ncba/callback/

# Google Maps (for geocoding)
GOOGLE_MAPS_API_KEY=<production-key>

# Pricing Configuration
BASE_DELIVERY_FEE=200
PER_KM_RATE=22.1
MINIMUM_ORDER_AMOUNT=200
```

---

## 🔄 DEPLOYMENT WORKFLOW

### Automatic Deployment (Current Setup - FagiErrands-Prod-server)
**NOTE:** This workflow needs to be migrated to `production-clean` branch

1. **Trigger:** Push to `main` branch of FagiErrands-Prod-server
2. **GitHub Actions:** Runs workflow
3. **FTP Upload:** Deploys to cPanel via FTPS
4. **Server:** LiteSpeed auto-restarts app

**Required GitHub Secrets:**
```
FTP_SERVER: ftp.distinctivecollections.co.ke
FTP_USERNAME: <cpanel-ftp-user>
FTP_PASSWORD: <cpanel-ftp-password>
```

### TODO: Migrate to New Branch Structure
- [ ] Update GitHub Actions to deploy `production-clean` branch
- [ ] Test deployment to cPanel
- [ ] Archive/delete FagiErrands-Prod-server repo
- [ ] Delete old `production` branch

---

## 🎯 CORE FEATURES & ENDPOINTS

### Authentication (`/api/accounts/`)
- ✅ User Registration (with SMS OTP verification)
- ✅ Phone number verification
- ✅ Login (JWT tokens)
- ✅ Password reset (SMS OTP)
- ✅ User profile management
- ✅ Handler & Rider management

### Orders (`/api/orders/`)
- ✅ Draft order creation (4-step errand flow)
- ✅ Add receiver info
- ✅ Order confirmation
- ✅ Price calculation (real-time)
- ✅ Rider assignment tracking
- ✅ Order status updates
- ✅ User order history

### Payments (`/api/orders/payments/`)
- ✅ NCBA/M-Pesa STK Push integration
- ✅ Payment initiation
- ✅ Payment status polling
- ✅ NCBA callback handling
- ✅ Automatic price recalculation at payment

### Admin Dashboard (`/api/admin-dashboard/`)
- ✅ System statistics
- ✅ User management
- ✅ Order overview
- ✅ Payment tracking

### Notifications (`/api/notifications/`)
- ✅ SMS notifications (TextPie)
- ✅ Order status notifications
- ✅ Payment confirmations

### Locations (`/api/locations/`)
- ✅ Location management
- ✅ Address geocoding (fallback)

---

## 🛠️ TECHNICAL STACK

### Backend Framework
- **Django** 4.x
- **Django REST Framework** (DRF)
- **Simple JWT** (Authentication)
- **drf-yasg** (Swagger API docs)

### Key Dependencies
```
Django>=4.2,<5.0
djangorestframework>=3.14.0
djangorestframework-simplejwt>=5.2.2
drf-yasg>=1.21.7
requests>=2.31.0
python-dotenv>=1.0.0
Pillow>=10.0.0
```

### Database
- **Production:** SQLite3 (on cPanel server)
- **Reason:** Shared hosting limitation, no PostgreSQL/MySQL access

### Web Server
- **LiteSpeed** with Passenger WSGI
- **WSGI Entry:** `passenger_wsgi.py`

### Third-Party Integrations
1. **TextPie SMS** - OTP & notifications
2. **NCBA Bank API** - M-Pesa payments via Till
3. **Google Maps API** - Geocoding (fallback only)

---

## 📊 KEY BUSINESS LOGIC

### Pricing Algorithm
```python
BASE_FEE = 200 KES
PER_KM_RATE = 22.1 KES/km

# Parcel Delivery
total_price = BASE_FEE + (distance_km * PER_KM_RATE)

# Cargo (heavier items)
total_price = BASE_FEE + (distance_km * PER_KM_RATE * 1.5)
```

**Important:** Prices are recalculated at payment initiation time to use latest rates from database.

### Order Flow
1. **Draft** → User creates order with addresses
2. **Pending** → User adds receiver info & confirms
3. **PaymentPending** → Order confirmed, waiting for payment
4. **Assigned** → Payment complete, rider assigned
5. **InTransit** → Rider picked up item
6. **Completed** → Delivery successful

### Payment Flow
1. User initiates payment → creates Payment record
2. Backend triggers NCBA STK Push to user's phone
3. User enters M-Pesa PIN on phone
4. M-Pesa processes payment
5. NCBA sends callback to backend
6. Backend updates payment status → triggers order update
7. App polls payment status endpoint until "Completed"

---

## 🔐 SECURITY MEASURES

### Production Security
- ✅ `DEBUG=False`
- ✅ `SECRET_KEY` in environment variables
- ✅ HTTPS enforced (via domain)
- ✅ JWT token authentication
- ✅ CORS configured for specific origins
- ✅ Phone number validation & normalization
- ✅ OTP expiration (10 minutes)
- ✅ Password strength validation

### Protected Data
- User credentials (bcrypt hashing)
- Payment transactions
- Phone numbers (normalized format)
- OTP codes (single-use, time-limited)

---

## 📈 PERFORMANCE & LIMITS

### Current Bottlenecks
1. **LSAPI Process Limit:** 6 child processes
   - **Impact:** Server slow under heavy load
   - **Solution:** Increase LSAPI_CHILDREN in cPanel or reduce polling frequency

2. **Aggressive Polling:** App polls rider-assignment every 3 seconds
   - **Impact:** Server hits process limits
   - **Solution:** Increase polling interval to 5-10 seconds

3. **SQLite Database:** Not optimized for high concurrency
   - **Impact:** Slower queries under load
   - **Future:** Consider PostgreSQL upgrade

### Caching
- Payment status cached for 10 seconds
- Reduces database queries during polling

---

## 🚨 KNOWN ISSUES & FIXES

### Recent Fixes (2026-06-07)
1. ✅ **Fixed:** Payment status endpoint crash - changed `payment_date` to `created_at`
2. ✅ **Fixed:** Missing settings import in `orders/views_errand.py`
3. ✅ **Fixed:** Price recalculation at payment time (ignores app cache)
4. ✅ **Added:** Better error logging for debugging

### Active Issues
1. **Geocoding Accuracy:** When app sends coordinates as `0.0`, backend geocoding returns wrong locations
   - **Workaround:** App should send proper coordinates
   
2. **Server Process Limits:** Frequent 503 errors under load
   - **Solution:** Increase LSAPI_CHILDREN or optimize polling

---

## 📝 MIGRATION HISTORY

### Why This Repo Structure?
**Previous Setup:**
- `fagierrands-dev-backend` - Old dev code (too many dependencies, cPanel deployment failed)
- `fagierrandsbackup` - Ancient backup
- `FagiErrands-Prod-server` - Clean rebuild (currently deployed)

**Problem:** Maintaining 3 separate codebases was unsustainable

**Solution:** Consolidated to ONE repo with TWO branches:
- Development in `main`
- Production in `production-clean`

### Production Baseline (production-clean branch)
- Created: 2026-06-07
- Source: Clean working code from FagiErrands-Prod-server
- Removed: 25,000+ lines of unused dev code
- Status: ✅ Stable, deployed, working in production

---

## 🎯 FUTURE ROADMAP

### Short Term (Next Sprint)
- [ ] Finish GitHub Actions migration to `production-clean` branch
- [ ] Test auto-deployment
- [ ] Archive old repos
- [ ] Increase server process limits

### Feature Backlog (main branch → test → migrate to production)
- [ ] Add marketplace endpoints
- [ ] Implement push notifications (Expo)
- [ ] Add email verification
- [ ] Implement wallet/points system
- [ ] Add referral rewards
- [ ] Handler dashboard features
- [ ] Rider app features

### Infrastructure Upgrades
- [ ] Consider VPS hosting for better performance
- [ ] Migrate to PostgreSQL
- [ ] Add Redis caching
- [ ] Implement proper background tasks (Celery)

---

## 🧑‍💻 DEVELOPMENT WORKFLOW

### Working on New Features
1. **Branch:** Work in `main` branch
2. **Test:** Test locally with SQLite
3. **Verify:** Ensure no complex dependencies (cPanel limitation)
4. **Migrate:** Cherry-pick or merge to `production-clean`
5. **Deploy:** Push `production-clean` → auto-deploys to cPanel

### Adding New Endpoints
1. Create in `main` branch
2. Test with Postman/Swagger
3. Document in README
4. Merge to `production-clean` when stable
5. Update mobile app

### Database Changes
1. Create migration in `main`
2. Test locally
3. Merge to `production-clean`
4. SSH to server and run: `python manage.py migrate`

---

## 📞 SUPPORT & CONTACTS

### Important Links
- **Production API:** https://fagierrandsbackendapi.distinctivecollections.co.ke
- **Alternative Domain:** https://api.errandserver.fagierrands.com
- **Swagger Docs:** https://fagierrandsbackendapi.distinctivecollections.co.ke/swagger/
- **Admin Panel:** https://fagierrandsbackendapi.distinctivecollections.co.ke/admin/
- **GitHub Repo:** https://github.com/Fagierrands-Apps/fagierrands-dev-backend

### Server Access
- **cPanel:** https://distinctivecollections.co.ke:2083
- **FTP:** ftp.distinctivecollections.co.ke
- **SSH:** (if available via cPanel)

### Monitoring
- Check deployment: GitHub Actions logs
- Check errors: `/home3/distinc3/fagierrandsbackendapi/logs/django.log`
- Check server errors: cPanel → Errors

---

## ✅ CHECKLIST FOR NEW DEVELOPERS

- [ ] Clone repo: `git clone <repo-url>`
- [ ] Checkout production: `git checkout production-clean`
- [ ] Review this document fully
- [ ] Check `.env.example` for required environment variables
- [ ] Understand two-branch workflow
- [ ] Test locally before pushing to production
- [ ] Never commit `.env`, `db.sqlite3`, or `media/` files
- [ ] Use descriptive commit messages
- [ ] Test endpoints with Swagger before deploying

---

**End of Documentation**  
*For questions or updates, contact the development team.*
