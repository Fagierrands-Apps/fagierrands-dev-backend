# Render Environment Variables
**Copy these into Render → Your Service → Environment → Add Environment Variables**

---

## 🔴 REQUIRED — App won't start without these

| Key | Value |
|-----|-------|
| `SECRET_KEY` | `9r1%hz2tdkhu39#6f^^_z(&0u&1g8=^cy_$(907_fs#tni-1r7` *(use a new one for Render)* |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | *(add your Render URL after first deploy — see below)* |
| `DATABASE_URL` | *(auto-set by Render PostgreSQL — copy from your DB dashboard)* |
| `USE_SQLITE` | `False` |

---

## 💳 NCBA Payment (Test Mode)

| Key | Value |
|-----|-------|
| `NCBA_USERNAME` | `Errand@123` |
| `NCBA_PASSWORD` | `9Y7a24B5TNxxKimfnGz9MTbdn960JY57ASC/r6KOCQNnR220v52od6a2ajgEaipL` |
| `NCBA_TILL_NO` | `852054` |
| `NCBA_PAYBILL_NO` | `880100` |
| `NCBA_TRANSACTION_TYPE` | `CustomerPayBillOnline` |
| `NCBA_USE_TILL_AS_ACCOUNT` | `False` |
| `NCBA_CALLBACK_URL` | `https://<your-render-url>/api/orders/payments/ncba/callback/` |
| `NCBA_CALLBACK_SECRET` | `f124f2bc7807204348790fb0142c488496dd194c7e91a0e01b64a52813545c6e` |
| `NCBA_ALLOWED_IPS` | *(leave blank for now — add after getting IPs from NCBA)* |

---

## 🔒 Security

| Key | Value |
|-----|-------|
| `SECURE_SSL_REDIRECT` | `True` |
| `SECURE_HSTS_SECONDS` | `31536000` |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` |
| `SESSION_COOKIE_SECURE` | `True` |
| `CSRF_COOKIE_SECURE` | `True` |
| `JWT_ACCESS_TOKEN_LIFETIME` | `1` |
| `JWT_REFRESH_TOKEN_LIFETIME` | `7` |

---

## 📧 Email (Brevo)

| Key | Value |
|-----|-------|
| `EMAIL_HOST` | `smtp-relay.brevo.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_HOST_USER` | `no-reply@fagitone.com` |
| `EMAIL_HOST_PASSWORD` | *(your Brevo SMTP password)* |
| `DEFAULT_FROM_EMAIL` | `no-reply@fagitone.com` |

---

## 📦 Supabase Storage

| Key | Value |
|-----|-------|
| `SUPABASE_URL` | `https://lmwloxheulmybtrnfobz.supabase.co` |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxtd2xveGhldWxteWJ0cm5mb2J6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5NzcxMjMsImV4cCI6MjA5NDU1MzEyM30.O8ScKmH9pIrejFClsOWDvyhFvBXIsPeHE95dSQ4VlN0` |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxtd2xveGhldWxteWJ0cm5mb2J6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODk3NzEyMywiZXhwIjoyMDk0NTUzMTIzfQ.OTHbQrAj1mwRNsEjT3Mgj41rqFaJDp56lsEKoUAqcp0` |
| `SUPABASE_BUCKET_NAME` | `user-uploads` |

---

## 📱 SMS (TextPie)

| Key | Value |
|-----|-------|
| `TEXTPIE_API_KEY` | `M176esJGFImYzBlqk9dgKfjuRXE2U3nyHZQvL4hiAWp08rTxwSNDVabtPO5oCc` |
| `TEXTPIE_SERVICE_ID` | `77` |
| `TEXTPIE_SHORTCODE` | `FagiErrands` |

---

## 🗺️ Google Maps

| Key | Value |
|-----|-------|
| `GOOGLE_MAPS_API_KEY` | `AIzaSyDT22XW8FHw6Pd1lNkh1UxDXSN6HrBUtsQ` |

---

## 🌐 URLs & CORS

| Key | Value |
|-----|-------|
| `BASE_URL` | `https://<your-render-url>` |
| `FRONTEND_URL` | `https://fagierrands-handler-dashboard.vercel.app` |

---

## ⚙️ Django Admin (auto-create on build)

| Key | Value |
|-----|-------|
| `DJANGO_ADMIN_USER` | `admin` |
| `DJANGO_ADMIN_EMAIL` | `admin@fagierrands.com` |
| `DJANGO_ADMIN_PASSWORD` | *(choose a strong password)* |

---

## 📋 Step-by-Step Render Setup

### 1. Create PostgreSQL database on Render
- Render Dashboard → New → PostgreSQL
- Name: `fagierrands-db`
- Plan: Free (for testing)
- Copy the **Internal Database URL** → paste as `DATABASE_URL`

### 2. Create Web Service
- Render Dashboard → New → Web Service
- Connect your GitHub repo: `Fagierrands-Apps/fagierrands-dev-backend`
- **Build Command:** `./build.sh`
- **Start Command:** `./render-start.sh`
- **Environment:** Python 3

### 3. Add all environment variables above

### 4. After first deploy — update ALLOWED_HOSTS
Your Render URL will be something like `fagierrands-dev-backend.onrender.com`

Update:
```
ALLOWED_HOSTS=localhost,127.0.0.1,fagierrands-dev-backend.onrender.com
NCBA_CALLBACK_URL=https://fagierrands-dev-backend.onrender.com/api/orders/payments/ncba/callback/
BASE_URL=https://fagierrands-dev-backend.onrender.com
```

### 5. Verify deployment
```
https://fagierrands-dev-backend.onrender.com/api/
https://fagierrands-dev-backend.onrender.com/admin/
```
