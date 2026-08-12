# FagiErrands Backend Security Assessment
**Date:** August 12, 2026  
**System:** Production Django REST Backend with NCBA M-Pesa Integration  
**Scope:** Full stack security including auth, payments, data storage, APIs, and deployment

---

## EXECUTIVE SUMMARY

**Overall Security Rating: 4.5/10 — CRITICAL ISSUES PRESENT**

The system has foundational security measures in place (JWT auth, HTTPS config, middleware blocking) but contains **multiple critical vulnerabilities that pose immediate risk to production data and financial transactions**. The most severe issues relate to secrets management, payment callback validation, and lack of rate limiting.

### Critical Issues (Fix Immediately)
1. ❌ Hardcoded secrets in environment files (.env.dev/.env.cpanel)
2. ❌ NCBA payment callback accepts unauthenticated requests
3. ❌ No rate limiting on authentication or OTP endpoints
4. ❌ Sensitive database credentials stored in plain text in GitHub

### High Priority Issues (Fix Within 1 Week)
1. ⚠️ Missing CORS origin validation in certain scenarios
2. ⚠️ Swagger/API docs publicly accessible in production
3. ⚠️ No file upload validation or size limits
4. ⚠️ Potential IDOR vulnerabilities in order endpoints

### Medium Priority Issues (Fix Within 1 Month)
1. 📋 No request validation on webhook endpoints
2. 📋 Missing audit logging for sensitive operations
3. 📋 OTP expiry not enforced in all code paths
4. 📋 Insufficient input validation on location queries

---

## DETAILED SECURITY RATING BY CATEGORY

### 1. AUTHENTICATION & SESSION MANAGEMENT
**Rating: 5/10 — Moderate with High-Risk Gaps**

#### ✅ What's Working Well
- JWT tokens with configurable lifetime (default 1 day access, 7 days refresh)
- Token refresh rotation enabled (`ROTATE_REFRESH_TOKENS = True`)
- Token blacklist after rotation (`BLACKLIST_AFTER_ROTATION = True`)
- Custom User model with phone-based auth
- OTP verification for phone numbers (10-minute expiry)
- Password validation using Django's built-in validators

#### ❌ Critical Vulnerabilities

**1. No Rate Limiting on Authentication Endpoints**
- `/api/accounts/register/` — unlimited registration attempts
- `/api/accounts/verify-phone/` — OTP brute-force possible (6-digit = 1M combinations)
- `/api/accounts/resend-otp/` — unlimited OTP generation
- **Risk:** Account enumeration, OTP brute-force attacks
- **Evidence:** SECURITY_SCAN_BRIEF.md identifies this; no throttle/rate_limit in codebase

**2. Weak OTP Security**
```python
# From accounts/views.py
OTPVerification.objects.filter(
    phone_number=phone, otp=otp, is_used=False,
    expires_at__gt=timezone.now()
).first()
```
- **Issue:** No tracking of failed attempts; attacker can try unlimited OTP codes
- **Issue:** No protection against timing attacks
- **Missing:** Failed attempt counter, lockout mechanism

**3. Account Enumeration via Error Messages**
- Error messages distinguish between "user not found" and "invalid OTP"
- Attacker can enumerate valid phone numbers in the system
- **Fix:** Return generic error for both cases

**4. Unverified Registration Flow**
- Users can register without phone verification initially
- `is_verified=False` users can potentially access certain endpoints
- **Issue:** Inconsistent verification state handling

#### 📋 Medium Issues
- No session timeout configuration visible
- No concurrent session limits
- No suspicious login detection

---

### 2. PAYMENT PROCESSING & WEBHOOKS
**Rating: 3/10 — CRITICAL VULNERABILITY**

#### ❌ CRITICAL: Unauthenticated Payment Callbacks

```python
# From orders/views_payment_ncba.py - NCBACallbackView
class NCBACallbackView(APIView):
    permission_classes = [permissions.AllowAny]  # ← CRITICAL
    
    def post(self, request):
        expected_secret = settings.NCBA_CALLBACK_SECRET if hasattr(settings, 'NCBA_CALLBACK_SECRET') else None
        if expected_secret:
            provided = request.headers.get('X-Callback-Secret') or request.GET.get('secret')
            if provided != expected_secret:
                return Response({'status': 'error'}, status=status.HTTP_403_FORBIDDEN)
        response = NCBAWebhookHandler.handle_callback(request.data)
        return Response(response)
```

**Exploitable Scenario:**
```bash
# Attacker can mark any payment as complete without authentication:
curl -X POST https://api.errandserver.fagierrands.com/api/orders/payments/ncba/callback/ \
  -H "Content-Type: application/json" \
  -d '{
    "OrderID": 123,
    "TransactionStatus": "SUCCESS",
    "Amount": 500000
  }'
```

**Risk Level:** HIGHEST — Direct financial fraud
- Payments can be marked complete without real M-Pesa transaction
- Orders automatically fulfill on fake completion
- Funds never received but marked as paid
- Attacker can complete orders without payment

**Required Fixes:**
1. Implement HMAC signature validation using NCBA_CALLBACK_SECRET
2. Verify IP whitelist (restrict to NCBA servers only)
3. Add timestamp validation (prevent replay attacks)
4. Implement idempotency key for callback processing

#### ⚠️ High Issues

**1. No Replay Attack Protection**
- Same webhook can be posted multiple times
- No idempotency key tracking
- Order could be completed multiple times

**2. Amount Tampering**
- Webhook data not validated against original request
- Backend doesn't verify: "amount charged = amount initiated"
- Client could fake paying 100 KES for 1000 KES order

**3. Missing Webhook Validation Framework**
- No signature verification standard
- Callback secret configured but **not enforced** if missing
- No request timeout on NCBA_CALLBACK_URL

#### 📋 Medium Issues
- Payment status polling in frontend not secured (401 check is good, but could be optimized)
- No reconciliation job to detect missing payment confirmations
- No alerting for suspicious payment patterns

---

### 3. DATABASE & CREDENTIAL STORAGE
**Rating: 2/10 — CRITICAL MISHANDLING**

#### ❌ CRITICAL: Secrets Exposed in Environment Files

**Problem:** Database credentials and API keys are stored in plaintext in tracked files:

```env
# From .env.cpanel (in production)
DB_PASSWORD=Pa7swrd1990@
NCBA_USERNAME=Errand@123
NCBA_PASSWORD=9Y7a24B5TNxxKimfnGz9MTbdn960JY57ASC/r6KOCQNnR220v52od6a2ajgEaipL
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxtd2xveGhldWxteWJ0cm5mb2J6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODk3NzEyMywiZXhwIjoyMDk0NTUzMTIzfQ.OTHbQrAj1mwRNsEjT3Mgj41rqFaJDp56lsEKoUAqcp0
```

**Risk:**
- If repository ever leaks (accidental push, GitHub compromise, social engineering), **ALL services fully compromised**
- Attacker gains:
  - Full PostgreSQL database access
  - M-Pesa payment gateway access (credentials to NCBA)
  - Supabase service role (full bucket/database access)
  - TextPie SMS gateway access
  - Google Maps API abuse

**Evidence of Mishandling:**
```python
# settings.py has partial protection but with gaps
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    warnings.warn("SECRET_KEY is not set — using insecure default...")
    SECRET_KEY = 'insecure-default-key-change-me-in-production'
```

The fallback key reveals intention, but production uses env files which contain real secrets.

#### ⚠️ High Issues

**1. Database Connection Not Using SSL**
```python
dj_database_url.config(
    env='DATABASE_URL',
    conn_max_age=600,
    ssl_require=False,  # ← INSECURE
)
```
- Credentials transmitted in plaintext over network
- Man-in-the-middle vulnerability on production network
- Fix: Change to `ssl_require=True`

**2. Service Role Key Stored Insecurely**
- SUPABASE_SERVICE_ROLE_KEY grants full database/storage access
- Should only exist on server, never in version control
- Used for admin operations; if leaked, attacker has complete Supabase control

**3. Multiple Hardcoded Credentials in Settings**
```python
# Default values exist in settings.py, should only be in env
TEXTPIE_SHORTCODE = 'FagiErrands'
SMS_SENDER_ID = 'FagiErrands'
```
While these seem harmless, they normalize storing secrets in code.

---

### 4. AUTHORIZATION & ACCESS CONTROL
**Rating: 5/10 — Moderate with IDOR Risks**

#### ✅ What's Working Well
- `IsAuthenticated` requirement on most endpoints
- Role-based checks using `user_type` field
- Admin access gated via `is_admin()` function
- CSRF enabled and configured for trusted origins

#### ❌ IDOR (Insecure Direct Object Reference) Risks

**1. Order Access Control**
```python
# From admin_dashboard/views.py
def is_admin(user):
    return user.user_type in ['admin', 'handler']
```

**Issue:** Definition too broad. "Handler" user_type can act like admin.
- Can a handler access orders from other handler assignments?
- Can a handler modify payment status?
- No evidence of per-order ownership verification in all views

**2. User Profile Access**
```python
# Assumed from endpoint structure - /api/accounts/{user_id}
# Does it verify request.user == target_user?
```
**Missing:** Explicit check in code reviewed; likely vulnerable to user enumeration

**3. Location Data Privacy**
- Real-time location queries (`locations/views.py`)
- Can users query other users' locations?
- No confirmation of ownership verification shown

#### ⚠️ High Issues
- No object-level permission decorators observed
- Reliance on endpoint-level checks only
- User-handler-rider relationships not validated in nested endpoints

---

### 5. API & ENDPOINT SECURITY
**Rating: 4/10 — Multiple Public Exposure Issues**

#### ❌ CRITICAL: Public Swagger/API Docs

```python
# swagger and redoc endpoints are AllowAny by default
# Located at /swagger/, /redoc/
```

**Risk:**
- Full API schema publicly visible
- All endpoint paths and parameters exposed
- Attacker learns internal structure immediately
- Can enumerate endpoints to find misconfigurations

**Fix:**
```python
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': True,  # Require auth to view docs
    'SECURITY_DEFINITIONS': {...},
}
```

#### ⚠️ High Issues

**1. CORS Misconfiguration Risk**
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',      # OK for dev
    'https://fagierrands-handler-dashboard.vercel.app',
    'https://fagiserver.fagitone.com',
    'https://api.errandserver.fagierrands.com',  # Allowing own domain
]
```
- Allowing `api.errandserver.fagierrands.com` as origin creates subdomain attack surface
- If one subdomain compromised, all others accessible
- Better: Specify exact frontend domains only

**2. No Input Validation on File Uploads**
- Supabase bucket uploads allow any file type
- No size limits visible in code
- No virus scanning integration

**3. Missing Content Security Policy (CSP)**
- No CSP headers configured
- Vulnerable to XSS if frontend reflects user input
- Missing: `X-Content-Type-Options: nosniff`

#### 📋 Medium Issues
- Endpoint discovery via 404 patterns
- No API versioning for backward compatibility
- Rate limiting completely absent

---

### 6. DATA PROTECTION
**Rating: 6/10 — Adequate with Gaps**

#### ✅ What's Working Well
- HTTPS/SSL configured for production (SECURE_SSL_REDIRECT=True)
- HSTS enabled (31536000 seconds = 1 year)
- Session and CSRF cookies marked secure
- Static files served via WhiteNoise with compression
- Django's CSRF protection enabled by default

#### ⚠️ High Issues

**1. Unencrypted Sensitive Data at Rest**
- User phone numbers stored in plaintext
- OTP codes visible in database
- Payment amounts logged without protection
- No encryption at rest for Supabase

**2. Logging Exposure**
```python
# logs/django.log accessible on server
# Could contain:
# - Authorization headers (JWT tokens)
# - Sensitive query parameters
# - User PII
# - Payment information
```

**3. No PII Masking in Logs**
- Phone numbers, payment amounts logged unmasked
- No sanitization of sensitive fields

#### 📋 Medium Issues
- No backup encryption strategy documented
- No data retention/deletion policies
- Media files not encrypted

---

### 7. DEPLOYMENT & INFRASTRUCTURE
**Rating: 5/10 — Moderate with Automation Risks**

#### ✅ What's Working Well
- cPanel with FTPS (encrypted) for deployment
- GitHub Actions automation for CI/CD
- Protected files excluded from deployment (db.sqlite3, .env, logs/)
- Passenger WSGI application isolation

#### ⚠️ High Issues

**1. Auto-Deployment on Main Branch**
- Any commit to `main` triggers automatic deployment
- GitHub branch protection not confirmed
- If attacker gains GitHub access, deployment immediate

**2. Debug Flag Risk**
```python
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```
- Defaults to False (good)
- But if DEBUG=False not set, could expose stack traces
- Better: Fail hard if not explicitly set

**3. ALLOWED_HOSTS Handling**
```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```
- Defaults to safe localhost
- But if env var missing, could be exploited
- Better: Require explicit configuration

#### 📋 Medium Issues
- No Web Application Firewall (WAF) mentioned
- No DDoS protection visible
- cPanel default security not documented
- No secrets rotation policy

---

### 8. SPECIFIC VULNERABILITY EXAMPLES

#### A. OTP Brute Force Attack
```
Attacker targets: POST /api/accounts/verify-phone/
1. Register account (AllowAny)
2. Try OTP codes sequentially: 000000, 000001, 000002, ...
3. No rate limit = try ~1000 codes/second
4. Success in ~16 minutes on average
5. Account verified, attacker has access

No mitigation:
- No throttle decorator observed
- No failed attempt tracking
- No account lockout
```

**Cost to Attacker:** $0 (client can do it)  
**Impact:** Account takeover for any user

#### B. Payment Spoofing
```
Real flow:
1. Client initiates payment (POST /api/orders/payments/initiate/)
2. NCBA sends STK push to phone
3. User enters M-Pesa PIN
4. NCBA calls callback: POST /api/orders/payments/ncba/callback/
5. Order marked paid

Attack flow:
1. Attacker intercepts callback URL (public, no auth)
2. POST to /api/orders/payments/ncba/callback/ with fake success
3. Order marked paid without real transaction
4. Goods/service delivered
5. No payment received but order completed

Mitigation present but ineffective:
- Callback secret CHECKED but optional
- if expected_secret: (defaults to checking NCBA_CALLBACK_SECRET if exists)
- If NCBA_CALLBACK_SECRET not set, NO validation occurs
- Production env file has NCBA_CALLBACK_SECRET empty or missing
```

**Cost to Attacker:** $0 (network access)  
**Impact:** Unlimited fraud, complete order theft

#### C. Service Account Key Exposure
```
Leaked: SUPABASE_SERVICE_ROLE_KEY
Attacker can:
- Read entire user database (user table with phone numbers, emails)
- Modify all orders and payments
- Delete storage bucket files
- Reset passwords for all users
- Transfer funds in wallet system
```

---

## REMEDIATION ROADMAP

### PHASE 1: EMERGENCY (This Week)
**Focus:** Stop critical vulnerabilities from being exploited

```markdown
1. Rotate all credentials immediately
   - [ ] Change NCBA_PASSWORD
   - [ ] Regenerate SUPABASE_SERVICE_ROLE_KEY
   - [ ] Rotate TEXTPIE_API_KEY
   - [ ] Generate new SECRET_KEY
   - [ ] Update database password
   
2. Fix payment callback security
   - [ ] Implement HMAC-SHA256 signature validation
   - [ ] Verify NCBA_CALLBACK_SECRET on every request (not optional)
   - [ ] Add IP whitelist for NCBA callbacks
   - [ ] Implement idempotency key tracking
   
3. Remove secrets from repository
   - [ ] Delete .env.dev and .env.cpanel from git history
   - [ ] Use GitHub Actions Secrets instead
   - [ ] Use cPanel's environment variable system
   - [ ] Verify no secrets in git log: git log -p --all -S "PASSWORD"
   
4. Implement rate limiting
   - [ ] Install django-ratelimit or DRF throttling
   - [ ] Rate limit: /api/accounts/register/ → 5 per minute per IP
   - [ ] Rate limit: /api/accounts/verify-phone/ → 10 per minute per phone
   - [ ] Rate limit: /api/accounts/resend-otp/ → 3 per 30 seconds per phone
```

### PHASE 2: HIGH PRIORITY (Week 2-3)
**Focus:** Fix authorization and data exposure

```markdown
1. Authentication hardening
   - [ ] Add failed attempt tracking for OTP
   - [ ] Implement account lockout after 5 failed OTP attempts
   - [ ] Add generic error messages (don't distinguish "user not found")
   - [ ] Add suspicious login detection (impossible travel)
   
2. Authorization improvements
   - [ ] Add explicit IDOR tests for order/user access
   - [ ] Implement django-guardian for object-level permissions
   - [ ] Verify handler can only access assigned orders
   - [ ] Verify rider can only access self-assigned orders
   
3. Data protection
   - [ ] Enable SSL requirement for PostgreSQL connections
   - [ ] Implement request/response logging without PII
   - [ ] Add audit trail for sensitive operations (payments, admin actions)
   - [ ] Encrypt sensitive fields: phone numbers, OTP codes
   
4. API security
   - [ ] Require authentication for /swagger/ and /redoc/
   - [ ] Add Content-Security-Policy headers
   - [ ] Add X-Content-Type-Options: nosniff
   - [ ] Implement file upload validation (type, size, virus scan)
```

### PHASE 3: MEDIUM PRIORITY (Month 1)
**Focus:** Robustness and monitoring

```markdown
1. Monitoring & logging
   - [ ] Centralized logging (DataDog, ELK, CloudWatch)
   - [ ] Alert on failed payment callbacks
   - [ ] Alert on repeated OTP failures
   - [ ] Alert on failed admin access attempts
   
2. Infrastructure
   - [ ] Add Web Application Firewall (Cloudflare, AWS WAF)
   - [ ] Implement DDoS protection
   - [ ] Add API versioning for backward compatibility
   - [ ] Secrets rotation policy (quarterly)
   
3. Testing & compliance
   - [ ] Implement OWASP Top 10 security tests
   - [ ] Load testing for rate limiting
   - [ ] Penetration testing contract
   - [ ] GDPR/data protection audit
```

---

## DETAILED FIXES FOR CRITICAL ISSUES

### Fix 1: Payment Callback Validation

**Before (Vulnerable):**
```python
class NCBACallbackView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        expected_secret = settings.NCBA_CALLBACK_SECRET if hasattr(settings, 'NCBA_CALLBACK_SECRET') else None
        if expected_secret:  # ← Optional check!
            provided = request.headers.get('X-Callback-Secret') or request.GET.get('secret')
            if provided != expected_secret:
                return Response({'status': 'error'}, status=status.HTTP_403_FORBIDDEN)
        # Process without validation if secret not set
        response = NCBAWebhookHandler.handle_callback(request.data)
        return Response(response)
```

**After (Secure):**
```python
import hmac
import hashlib
from django.http import HttpResponse

class NCBACallbackView(APIView):
    permission_classes = [permissions.AllowAny]  # External webhook
    
    def post(self, request):
        # 1. Verify HMAC signature
        signature = request.headers.get('X-Signature')
        if not signature:
            logger.warning(f"Callback rejected: missing signature from {request.META.get('REMOTE_ADDR')}")
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        secret = settings.NCBA_CALLBACK_SECRET
        if not secret:
            logger.error("NCBA_CALLBACK_SECRET not configured")
            return Response({'error': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Compute expected signature
        payload = request.body  # Raw body
        expected_sig = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_sig):
            logger.warning(f"Callback rejected: invalid signature")
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # 2. Verify timestamp (prevent replay within 5 minutes)
        timestamp = request.headers.get('X-Timestamp')
        if not timestamp:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        callback_time = int(timestamp)
        now = int(timezone.now().timestamp())
        if abs(now - callback_time) > 300:  # 5 minute window
            logger.warning(f"Callback rejected: stale timestamp {callback_time}")
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # 3. Verify IP (whitelist NCBA servers)
        client_ip = request.META.get('REMOTE_ADDR')
        NCBA_IPS = settings.get('NCBA_CALLBACK_IPS', [])
        if NCBA_IPS and client_ip not in NCBA_IPS:
            logger.warning(f"Callback rejected: unauthorized IP {client_ip}")
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # 4. Check idempotency
        transaction_id = request.data.get('TransactionID')
        idempotency_key = f"ncba_callback_{transaction_id}"
        if cache.get(idempotency_key):
            # Duplicate callback, return success but don't reprocess
            logger.info(f"Duplicate callback detected: {transaction_id}")
            return Response({'status': 'success'})
        
        # 5. Process callback
        response = NCBAWebhookHandler.handle_callback(request.data)
        
        # Mark as processed
        cache.set(idempotency_key, True, 86400)  # 24 hours
        
        return Response(response)
```

**Environment Configuration:**
```env
# .env.cpanel
NCBA_CALLBACK_SECRET=your_random_256_bit_hex_string_here_minimum_32_chars
NCBA_CALLBACK_IPS=196.43.100.1,196.43.100.2  # NCBA IP whitelist
```

---

### Fix 2: OTP Brute Force Protection

**Install Django Rate Limiting:**
```bash
pip install djangorestframework
# DRF throttling is built-in
```

**Configuration:**
```python
# settings.py
REST_FRAMEWORK = {
    # ... existing config ...
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# Per-endpoint throttling config (add to settings)
OTP_THROTTLE = '10/hour'  # 10 OTP attempts per hour per phone/user
```

**View Implementation:**
```python
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.decorators import throttle_classes

class OTPThrottle(SimpleRateThrottle):
    scope = 'otp'
    
    def get_cache_key(self):
        if self.request.user.is_authenticated:
            return f"otp_{self.request.user.id}"
        return f"otp_{self.request.data.get('phone_number', 'unknown')}"

class OTPFailureThrottle(SimpleRateThrottle):
    """Track failed OTP attempts"""
    scope = 'otp_failures'
    
    def get_cache_key(self):
        phone = self.request.data.get('phone_number')
        return f"otp_failures_{phone}"

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPThrottle, OTPFailureThrottle])
def verify_phone(request):
    phone = normalize_phone_number(request.data.get('phone_number'))
    otp = request.data.get('otp')
    
    # Check for lockout
    lockout_key = f"otp_lockout_{phone}"
    if cache.get(lockout_key):
        return Response(
            {'error': 'Too many attempts. Try again after 15 minutes.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    otp_obj = OTPVerification.objects.filter(
        phone_number=phone, otp=otp, is_used=False,
        expires_at__gt=timezone.now()
    ).first()
    
    if not otp_obj:
        # Track failure
        failure_key = f"otp_failures_{phone}"
        failures = cache.get(failure_key, 0) + 1
        cache.set(failure_key, failures, 3600)  # 1 hour window
        
        if failures >= 5:
            # Lockout for 15 minutes
            cache.set(lockout_key, True, 900)
            return Response(
                {'error': 'Too many failed attempts. Try again after 15 minutes.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Generic error message (no enumeration)
        return Response(
            {'error': 'Invalid verification code. Please try again.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Clear failure tracking on success
    cache.delete(f"otp_failures_{phone}")
    
    # Process verification...
    user = User.objects.filter(phone_number=phone).first()
    # ... rest of logic
```

**Throttle Rates Configuration:**
```python
# settings.py
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'otp': '10/hour',
    'otp_failures': '5/15min',
}
```

---

### Fix 3: Remove Secrets from Repository

**Step 1: Use GitHub Actions Secrets**
```yaml
# .github/workflows/deploy.yml
name: Deploy to cPanel
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Create .env file
        run: |
          cat > .env.cpanel << EOF
          DEBUG=False
          SECRET_KEY=${{ secrets.SECRET_KEY }}
          DB_NAME=${{ secrets.DB_NAME }}
          DB_USER=${{ secrets.DB_USER }}
          DB_PASSWORD=${{ secrets.DB_PASSWORD }}
          DB_HOST=${{ secrets.DB_HOST }}
          NCBA_USERNAME=${{ secrets.NCBA_USERNAME }}
          NCBA_PASSWORD=${{ secrets.NCBA_PASSWORD }}
          NCBA_CALLBACK_SECRET=${{ secrets.NCBA_CALLBACK_SECRET }}
          SUPABASE_URL=${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY=${{ secrets.SUPABASE_KEY }}
          SUPABASE_SERVICE_ROLE_KEY=${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          # ... all other secrets
          EOF
      
      - name: Deploy to cPanel
        run: |
          # Your FTP deployment logic here
          # Never include .env files in git
```

**Step 2: Clean Git History**
```bash
# Remove secrets from entire history (DANGEROUS - do carefully)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env.cpanel .env.dev' \
  --prune-empty --tag-name-filter cat -- --all

# Verify secrets are removed
git log -p --all -S "Pa7swrd1990@" | head -20

# Force push (REQUIRES CAUTION)
git push origin --force --all
git push origin --force --tags
```

**Step 3: Update .gitignore**
```
# .gitignore
.env
.env.local
.env.dev
.env.cpanel
.env.production
.env.*.local
*.key
*.pem
db.sqlite3
/media
/logs
```

---

## TESTING SECURITY FIXES

### Test 1: Verify OTP Throttling
```python
# tests/test_otp_security.py
from django.test import TestCase, Client
from django.urls import reverse

class OTPSecurityTests(TestCase):
    def test_otp_brute_force_blocked(self):
        """Verify brute force attempts are throttled"""
        client = Client()
        phone = '+254712345678'
        
        # Try 11 OTP verifications (limit is 10/hour)
        for i in range(11):
            response = client.post(reverse('verify_phone'), {
                'phone_number': phone,
                'otp': '000000'
            })
            
            if i < 10:
                # First 10 should be allowed (with failure response)
                self.assertIn(response.status_code, [400, 429])
            else:
                # 11th should be throttled
                self.assertEqual(response.status_code, 429)
                self.assertIn('too many', response.json()['error'].lower())
```

### Test 2: Verify Callback Signature Validation
```python
# tests/test_payment_security.py
import hmac
import hashlib
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

class PaymentCallbackSecurityTests(TestCase):
    def test_callback_requires_valid_signature(self):
        """Verify NCBA callback requires HMAC signature"""
        client = Client()
        secret = 'test-secret-key'
        payload = b'{"TransactionID": "123", "StatusCode": "SUCCESS"}'
        
        # Compute valid signature
        signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Test 1: Missing signature
        response = client.post(
            reverse('ncba-callback'),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        
        # Test 2: Invalid signature
        response = client.post(
            reverse('ncba-callback'),
            data=payload,
            content_type='application/json',
            HTTP_X_SIGNATURE='invalid-sig'
        )
        self.assertEqual(response.status_code, 403)
        
        # Test 3: Valid signature
        response = client.post(
            reverse('ncba-callback'),
            data=payload,
            content_type='application/json',
            HTTP_X_SIGNATURE=signature,
            HTTP_X_TIMESTAMP=str(int(timezone.now().timestamp()))
        )
        self.assertEqual(response.status_code, 200)
```

---

## COMPLIANCE & STANDARDS

**Standards This System Should Meet:**
- ✅ OWASP Top 10 2021
- ❌ PCI DSS (for payment processing) — **NOT CURRENTLY COMPLIANT**
- ❌ GDPR (for user data) — **NEEDS WORK**
- ❌ ISO 27001 (information security) — **NOT AUDITED**

**Quick Compliance Gaps:**
- No data processing agreements with third parties (Supabase, TextPie, NCBA, Cloudinary)
- No privacy policy enforcing consent for phone data collection
- No data retention schedule documented
- No incident response plan

---

## QUICK REFERENCE: PRIORITY CHECKLIST

```
CRITICAL (Fix This Week)
[ ] Implement HMAC verification for payment callbacks
[ ] Add rate limiting to /api/accounts/register/ and /verify-phone/
[ ] Remove .env files from git history
[ ] Rotate all database and API credentials
[ ] Configure NCBA_CALLBACK_SECRET and enforce it

HIGH (Week 2)
[ ] Add OTP attempt lockout (5 failures = 15 min lockout)
[ ] Enable database SSL requirement
[ ] Restrict Swagger/ReDoc to authenticated users
[ ] Add audit logging for sensitive operations
[ ] Implement IDOR tests for order endpoints

MEDIUM (Month 1)
[ ] Add CSP and security headers
[ ] Implement file upload validation
[ ] Set up centralized logging
[ ] Add penetration testing contract
[ ] GDPR/data protection audit

ONGOING
[ ] Monthly security updates (Django, DRF, dependencies)
[ ] Quarterly secrets rotation
[ ] Continuous monitoring for threats
```

---

## CONCLUSION

The FagiErrands backend has a **solid foundation** with Django, DRF, JWT authentication, and HTTPS configured. However, **critical vulnerabilities in payment processing, secrets management, and rate limiting create immediate risk**.

**The top 3 issues to fix urgently:**
1. **Unauthenticated payment callbacks** — Enables arbitrary payment fraud
2. **Hardcoded secrets in files** — Exposes entire system to compromise
3. **No rate limiting** — Enables account takeover via OTP brute force

Estimated time to address critical issues: **2-3 days**  
Estimated time to full remediation: **4-6 weeks**

After fixes, recommend independent security audit and penetration testing to verify all issues resolved.

---

**Assessment prepared by:** Security Analysis System  
**Confidence Level:** High (based on code review, not runtime testing)  
**Last Updated:** August 12, 2026
