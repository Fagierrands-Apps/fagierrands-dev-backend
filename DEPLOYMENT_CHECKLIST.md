# Deployment Checklist - Render

## ✅ PRE-DEPLOYMENT CHECKS

### 1. Code Status
- ✅ New endpoint added: `/api/orders/<order_id>/rider-details/`
- ✅ Swagger documentation added
- ✅ URL routing configured
- ✅ Authentication & permissions set

### 2. Migrations Status
**Total Unapplied:** 56 migrations

**Critical Migrations:**
- locations.0002_waypoint_routecalculation
- marketplace (2 migrations)
- notifications (3 migrations)
- orders (40+ migrations)
- sessions
- token_blacklist

**Action Required:** Run migrations on Render after deployment

### 3. Environment Variables (Render)
**Required:**
- ✅ DATABASE_URL (auto-configured by Render)
- ✅ SECRET_KEY
- ✅ DEBUG=False
- ✅ ALLOWED_HOSTS (include render domain)
- ⚠️ GOOGLE_MAPS_API_KEY (currently empty)
- ✅ TEXTPIE_API_KEY
- ✅ TEXTPIE_SERVICE_ID
- ✅ TEXTPIE_SHORTCODE

**Optional but Recommended:**
- SUPABASE_URL
- SUPABASE_KEY
- SUPABASE_BUCKET_NAME

### 4. Dependencies
**Check requirements.txt includes:**
- ✅ Django
- ✅ djangorestframework
- ✅ drf-yasg (Swagger)
- ✅ psycopg2-binary (PostgreSQL)
- ✅ gunicorn
- ✅ whitenoise

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Commit & Push Changes
```bash
cd /home/fagitone/Documents/GitHub/fagierrands-dev-backend

# Check status
git status

# Add new files
git add orders/views_rider_details.py
git add COMPLETE_ERRAND_FLOW.md
git add API_ENDPOINTS_COMPLETE.md
git add RIDER_DETAILS_ENDPOINT.md
git add AUTOSUGGEST_TEST_RESULTS.md

# Commit
git commit -m "Add rider details endpoint and documentation"

# Push to main
git push origin main
```

### Step 2: Render Auto-Deploy
- Render will automatically detect the push
- Build will start automatically
- Wait for build to complete (~5-10 minutes)

### Step 3: Run Migrations on Render
**Option A: Via Render Shell**
1. Go to Render Dashboard
2. Select your service
3. Click "Shell" tab
4. Run:
```bash
python manage.py migrate
```

**Option B: Via Build Command**
Update build command in `render.yaml`:
```yaml
buildCommand: pip install -r requirements.txt && python manage.py migrate
```

### Step 4: Verify Deployment
Test these URLs:
- `https://your-app.onrender.com/swagger/` - Swagger UI
- `https://your-app.onrender.com/api/orders/` - Orders API
- `https://your-app.onrender.com/admin/` - Admin panel

---

## 🧪 POST-DEPLOYMENT TESTING

### Test 1: Swagger UI
```
URL: https://your-app.onrender.com/swagger/
Expected: Swagger documentation loads
Check: New rider-details endpoint appears
```

### Test 2: Authentication
```
Endpoint: POST /api/accounts/login/
Body: {
  "phone_number": "+254712345678",
  "password": "your_password"
}
Expected: Returns access_token
```

### Test 3: Rider Details Endpoint
```
Endpoint: GET /api/orders/{order_id}/rider-details/
Headers: Authorization: Bearer {token}
Expected: Returns rider details or "not assigned" message
```

### Test 4: Errand Flow
Follow the complete flow from `COMPLETE_ERRAND_FLOW.md`:
1. Register → Verify → Login
2. Calculate price → Create draft
3. Upload images → Confirm
4. Initiate payment
5. Check rider details

---

## 📋 SWAGGER ENDPOINTS TO VERIFY

### New Endpoints:
- ✅ `GET /api/orders/{order_id}/rider-details/` - Get assigned rider

### Existing Critical Endpoints:
- ✅ `POST /api/accounts/register/` - Registration
- ✅ `POST /api/accounts/verify-phone/` - Phone verification
- ✅ `POST /api/accounts/login/` - Login
- ✅ `POST /api/orders/errands/calculate-price/` - Price calculation
- ✅ `POST /api/orders/errands/draft/` - Create draft
- ✅ `POST /api/orders/errands/{id}/confirm/` - Confirm errand
- ✅ `POST /api/orders/payments/initiate/` - Payment
- ✅ `POST /api/orders/{id}/assign/` - Assign rider
- ✅ `GET /api/orders/{id}/tracking/` - Track order

---

## ⚠️ KNOWN ISSUES & FIXES

### Issue 1: Missing Google Maps API Key
**Impact:** Location autocomplete won't work
**Fix:** Add `GOOGLE_MAPS_API_KEY` to Render environment variables

### Issue 2: Unapplied Migrations
**Impact:** Some features may not work
**Fix:** Run `python manage.py migrate` in Render shell

### Issue 3: Static Files
**Impact:** Admin panel styling may be missing
**Fix:** Ensure `whitenoise` is in requirements.txt and configured

---

## 🔧 RENDER CONFIGURATION

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
gunicorn fagierrandsbackup.wsgi:application
```

### Environment Variables to Set:
```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-app.onrender.com,fagierrands-backend.onrender.com
GOOGLE_MAPS_API_KEY=your-google-maps-key
```

---

## 📊 DEPLOYMENT CHECKLIST

### Before Deployment:
- [ ] All code committed and pushed
- [ ] requirements.txt updated
- [ ] Environment variables configured on Render
- [ ] Database backup taken (if needed)

### During Deployment:
- [ ] Build completes successfully
- [ ] No build errors in logs
- [ ] Service starts without errors

### After Deployment:
- [ ] Run migrations
- [ ] Test Swagger UI
- [ ] Test authentication endpoints
- [ ] Test new rider-details endpoint
- [ ] Test complete errand flow
- [ ] Check error logs

---

## 🆘 TROUBLESHOOTING

### Build Fails
1. Check Render build logs
2. Verify requirements.txt syntax
3. Check Python version compatibility

### Migrations Fail
1. Check database connection
2. Verify DATABASE_URL is set
3. Check for conflicting migrations

### Endpoints Return 500
1. Check Render logs
2. Verify environment variables
3. Check database migrations applied

### Swagger Not Loading
1. Check `drf-yasg` in requirements.txt
2. Verify URL configuration
3. Check static files serving

---

## 📞 SUPPORT RESOURCES

- **Render Docs:** https://render.com/docs
- **Django Docs:** https://docs.djangoproject.com
- **DRF Docs:** https://www.django-rest-framework.org
- **Swagger Docs:** https://drf-yasg.readthedocs.io

---

## ✅ READY TO DEPLOY?

Run this command to start:
```bash
cd /home/fagitone/Documents/GitHub/fagierrands-dev-backend
git add -A
git commit -m "Add rider details endpoint with Swagger docs"
git push origin main
```

Then monitor Render dashboard for auto-deployment!
