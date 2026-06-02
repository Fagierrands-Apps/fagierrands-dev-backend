# cPanel Clean Deployment - Step by Step

## What We Learned:
1. cPanel overwrites `passenger_wsgi.py` - we need to edit it after creation
2. Celery doesn't work without Redis - must be disabled
3. Need proper logging to debug issues
4. FTP deployment path must be correct
5. `.htaccess` needed for routing

## Pre-Deployment Fixes (Done in Git)

### 1. Fix Celery Issue
**File:** `fagierrandsbackup/__init__.py`
**Make it empty or just comments:**
```python
# Django app initialization
# Celery disabled for cPanel (no Redis available)
```

### 2. Create cPanel-Ready passenger_wsgi.py Template
**File:** `passenger_wsgi_INSTRUCTIONS.txt`
```
After cPanel creates the Python app, replace passenger_wsgi.py with:

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from wsgi_app import application
```

### 3. Ensure wsgi_app.py is Ready
**File:** `wsgi_app.py` (already exists with logging)

### 4. Verify .env.cpanel is Correct
**File:** `.env.cpanel` (already correct)

### 5. Create .htaccess Template
**File:** `.htaccess_TEMPLATE`
```apache
PassengerAppRoot "/home3/distinc3/api.errandserver.fagierrands.com"
PassengerBaseURI "/"
PassengerPython "/home3/distinc3/virtualenv/api.errandserver.fagierrands.com/3.11/bin/python3.11"
PassengerAppLogFile "/home3/distinc3/logs/api.errandserver.fagierrands.com.error.log"
PassengerEnabled On
```

---

## Clean Deployment Process

### Step 1: Clean Up cPanel
1. **Delete existing Python app** in Setup Python App
2. **Delete folder** `/home3/distinc3/api.errandserver.fagierrands.com/` in File Manager
3. **Create fresh subdomain** (if needed): `api.errandserver.fagierrands.com`

### Step 2: Push Fixed Code to GitHub
```bash
git checkout production-cpanel
# Make sure all fixes are committed
git push origin production-cpanel
```

**This will auto-deploy via GitHub Actions**

### Step 3: Create Python App in cPanel
1. cPanel → **Setup Python App** → **Create Application**
2. Settings:
   - Python Version: **3.11**
   - Application Root: `api.errandserver.fagierrands.com`
   - Application URL: Select domain from dropdown
   - Application Startup File: `passenger_wsgi.py`
   - Application Entry Point: `application`
3. Click **CREATE**
4. **Wait 3-5 minutes** for requirements.txt installation

### Step 4: Fix passenger_wsgi.py (cPanel Always Overwrites This)
1. File Manager → `api.errandserver.fagierrands.com/passenger_wsgi.py`
2. **Edit and replace ALL content** with:
```python
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from wsgi_app import application
```
3. **Save**

### Step 5: Create .htaccess
1. File Manager → `api.errandserver.fagierrands.com/`
2. **Create new file:** `.htaccess`
3. Content:
```apache
PassengerAppRoot "/home3/distinc3/api.errandserver.fagierrands.com"
PassengerBaseURI "/"
PassengerPython "/home3/distinc3/virtualenv/api.errandserver.fagierrands.com/3.11/bin/python3.11"
PassengerAppLogFile "/home3/distinc3/logs/api.errandserver.fagierrands.com.error.log"
PassengerEnabled On
```
4. **Save**

### Step 6: Restart and Test
1. Setup Python App → **Restart**
2. Test URLs:
   - `http://api.errandserver.fagierrands.com/admin/`
   - `http://api.errandserver.fagierrands.com/api/swagger/`

### Step 7: Check Logs (If Issues)
**File Manager:**
- `/home3/distinc3/api.errandserver.fagierrands.com/wsgi_startup.log`
- `/home3/distinc3/logs/api.errandserver.fagierrands.com.error.log`

---

## Expected Result
✅ Django admin accessible  
✅ Swagger API docs working  
✅ No 404 or 503 errors  
✅ Database connected  

---

## If Still Issues - Quick Fixes

### Issue: ModuleNotFoundError
**Fix:** Check requirements.txt installed
```bash
# In Setup Python App → Run pip install
```

### Issue: Database Connection Failed
**Fix:** Verify .env file exists and has correct DB credentials

### Issue: 503 Error
**Fix:** Check `wsgi_startup.log` for exact error

---

## Time Estimate
- Delete old setup: 2 minutes
- Push code: 1 minute
- Auto-deploy: 2 minutes
- Create Python app: 5 minutes (requirements install)
- Edit passenger_wsgi.py: 1 minute
- Create .htaccess: 1 minute
- Test: 1 minute

**Total: ~13 minutes**

---

## Files to Prepare Now (Before Starting)

1. ✅ Fix `fagierrandsbackup/__init__.py` - Remove Celery
2. ✅ Ensure `wsgi_app.py` has logging
3. ✅ Create `.htaccess` template file
4. ✅ Create `passenger_wsgi_CORRECT.py` template file
5. ✅ Verify `.env.cpanel` is correct
6. ✅ Commit and push all fixes

Ready to start?
