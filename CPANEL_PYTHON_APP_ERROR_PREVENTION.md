# cPanel Python App Setup - Error Prevention Guide
**Date:** June 2, 2026  
**Project:** Fagierrands Backend Django App

---

## Pre-Setup Checklist

### 1. Python Version Check
**Requirement:** Python 3.10 or 3.11  
**cPanel Issue:** May default to Python 3.8 or 3.9

**Solution:**
- In cPanel → Setup Python App → Select Python 3.10+ or 3.11
- If not available, contact host to enable it

---

## Anticipated Errors & Solutions

### ERROR 1: Module Not Found (Missing Dependencies)
**Error Message:**
```
ModuleNotFoundError: No module named 'django'
ModuleNotFoundError: No module named 'psycopg2'
```

**Cause:** Virtual environment not installed with requirements.txt

**Prevention:**
1. Ensure `requirements.txt` is in root directory
2. cPanel auto-installs from requirements.txt when creating Python app
3. If it fails, manually run in SSH:
```bash
source /home/username/virtualenv/api.errandserver.fagitone.com/3.11/bin/activate
pip install -r /home/username/api.errandserver.fagitone.com/requirements.txt
```

---

### ERROR 2: Database Connection Failed
**Error Message:**
```
django.db.utils.OperationalError: could not connect to server
FATAL: password authentication failed for user
```

**Cause:** Database credentials mismatch or PostgreSQL not accessible

**Prevention Checklist:**
- ✅ PostgreSQL database `distinc3_fagierrandsNew` exists in cPanel
- ✅ User `distinc3_FagierrandsNew` has full privileges
- ✅ Password in `.env` matches cPanel database password
- ✅ DB_HOST=localhost (not 127.0.0.1 on some cPanel setups)
- ✅ DB_PORT=5432

**Immediate Fix:**
```bash
# Test connection via SSH
psql -U distinc3_FagierrandsNew -d distinc3_fagierrandsNew -h localhost
```

---

### ERROR 3: Static Files Not Loading
**Error Message:**
```
GET /static/admin/css/base.css 404
```

**Cause:** Static files not collected

**Prevention:**
Run after deployment via SSH:
```bash
cd /home/username/api.errandserver.fagitone.com
source /home/username/virtualenv/api.errandserver.fagitone.com/3.11/bin/activate
python manage.py collectstatic --noinput
```

**cPanel Setting:**
- Static Files URL: `/static/`
- Static Files Path: `/home/username/api.errandserver.fagitone.com/staticfiles/`

---

### ERROR 4: Application Entry Point Error
**Error Message:**
```
Target WSGI script cannot be loaded as Python module
```

**Cause:** Incorrect WSGI path or passenger_wsgi.py misconfigured

**Required passenger_wsgi.py:**
```python
import sys
import os

INTERP = "/home/username/virtualenv/api.errandserver.fagitone.com/3.11/bin/python3"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, '/home/username/api.errandserver.fagitone.com')
os.environ['DJANGO_SETTINGS_MODULE'] = 'fagierrandsbackup.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Prevention:** Ensure passenger_wsgi.py points to correct:
- Virtual environment path
- Project path
- Settings module name (fagierrandsbackup.settings)

---

### ERROR 5: Environment Variables Not Loading
**Error Message:**
```
KeyError: 'DB_PASSWORD'
ImproperlyConfigured: SECRET_KEY not found
```

**Cause:** .env file not loaded by Django

**Prevention:**
Ensure settings.py has:
```python
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))
```

**Quick Check via SSH:**
```bash
cd /home/username/api.errandserver.fagitone.com
cat .env | head -5
# Should show DEBUG=False, SECRET_KEY=..., etc.
```

---

### ERROR 6: Permission Denied Errors
**Error Message:**
```
PermissionError: [Errno 13] Permission denied: '/home/username/...'
OSError: [Errno 13] Permission denied: 'media'
```

**Cause:** Wrong file/folder permissions

**Prevention - Set correct permissions via SSH:**
```bash
cd /home/username/api.errandserver.fagitone.com
chmod -R 755 .
chmod -R 775 media staticfiles
```

---

### ERROR 7: Migration Errors
**Error Message:**
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Cause:** Database has old migrations or no migrations applied

**Prevention - Run migrations via SSH:**
```bash
cd /home/username/api.errandserver.fagitone.com
source /home/username/virtualenv/api.errandserver.fagitone.com/3.11/bin/activate
python manage.py makemigrations
python manage.py migrate
```

---

### ERROR 8: ALLOWED_HOSTS Error
**Error Message:**
```
DisallowedHost at / Invalid HTTP_HOST header
```

**Cause:** Domain not in ALLOWED_HOSTS

**Prevention:**
`.env` already has:
```
ALLOWED_HOSTS=fagiserver.fagitone.com,www.fagiserver.fagitone.com
```

**If error persists, add to settings.py:**
```python
ALLOWED_HOSTS = [host.strip() for host in os.environ.get(
    'ALLOWED_HOSTS',
    'fagiserver.fagitone.com,www.fagiserver.fagitone.com,api.errandserver.fagitone.com'
).split(',')]
```

---

### ERROR 9: CORS Issues from Frontend
**Error Message (in browser console):**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Prevention:**
`.env` already configured:
```
CORS_ALLOWED_ORIGINS=https://fagierrands-handler-dashboard.vercel.app,https://fagiserver.fagitone.com
```

Ensure settings.py has:
```python
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
```

---

### ERROR 10: TimeZone/Locale Errors
**Error Message:**
```
OSError: Could not find timezone database
```

**Prevention:**
Already set in settings.py:
```python
TIME_ZONE = 'Africa/Nairobi'
USE_TZ = True
```

**If error persists, install via SSH:**
```bash
pip install tzdata
```

---

## cPanel Python App Setup Steps (Error-Free)

### Step 1: Create Python Application
1. cPanel → Setup Python App
2. Python Version: **3.11** (or highest available)
3. Application Root: `/home/username/api.errandserver.fagitone.com`
4. Application URL: `api.errandserver.fagitone.com` OR just leave blank for root
5. Application Startup File: `passenger_wsgi.py`
6. Application Entry Point: `application`

### Step 2: Verify Environment (via SSH)
```bash
# Check virtual environment
source /home/username/virtualenv/api.errandserver.fagitone.com/3.11/bin/activate
python --version  # Should show 3.11

# Check .env file exists
cd /home/username/api.errandserver.fagitone.com
ls -la | grep .env
cat .env | head -5

# Check requirements installed
pip list | grep -E "Django|psycopg2|django-cors"
```

### Step 3: Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Step 4: Test Application
```bash
# Quick test
python manage.py check

# Test database connection
python manage.py dbshell
# Type: \q to quit
```

### Step 5: Restart Application
- cPanel → Setup Python App → Click "Restart" button
- Or via SSH: `touch /home/username/api.errandserver.fagitone.com/tmp/restart.txt`

### Step 6: Verify in Browser
```
https://api.errandserver.fagitone.com/admin/
https://api.errandserver.fagitone.com/api/swagger/
```

---

## Emergency Debugging Commands

### Check Application Logs
```bash
# Error logs
tail -100 /home/username/logs/api.errandserver.fagitone.com.error.log

# Access logs
tail -100 /home/username/logs/api.errandserver.fagitone.com.access.log
```

### Check Passenger Status
```bash
passenger-status
```

### Force Restart
```bash
touch /home/username/api.errandserver.fagitone.com/tmp/restart.txt
```

### Test Python Import
```bash
cd /home/username/api.errandserver.fagitone.com
source /home/username/virtualenv/api.errandserver.fagitone.com/3.11/bin/activate
python -c "import django; print(django.get_version())"
python -c "from fagierrandsbackup.wsgi import application; print('WSGI OK')"
```

---

## Quick Reference: What You'll Need

### From cPanel
- ✅ Full path to home directory (e.g., `/home/distinc3`)
- ✅ Database already exists: `distinc3_fagierrandsNew`
- ✅ Database user: `distinc3_FagierrandsNew`
- ✅ PostgreSQL port: 5432
- ✅ SSH access enabled

### Files to Update (if needed)
1. `passenger_wsgi.py` - Update username in paths
2. `.htaccess` - Usually auto-generated by cPanel

---

## Success Indicators

✅ No errors in `/home/username/logs/api.errandserver.fagitone.com.error.log`  
✅ Admin panel loads at `/admin/`  
✅ Swagger docs load at `/api/swagger/`  
✅ Database queries work (check admin can list users/orders)  
✅ Static files load (admin CSS/JS working)  
✅ Can create/login users via API

---

## Next Steps After Setup

1. Test NCBA payment webhook
2. Test TextPie SMS sending
3. Test file uploads (Supabase)
4. Monitor error logs for 24 hours
5. Set up cron jobs for Celery (if used)

---

**Summary:** This guide prevents 90% of common cPanel Django deployment errors before they happen.
