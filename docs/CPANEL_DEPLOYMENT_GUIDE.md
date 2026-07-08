# cPanel Python Backend Migration Guide
## Zero-Downtime Deployment Strategy with GitHub Auto-Sync

---

## 📋 EXECUTIVE SUMMARY

**Objective:** Deploy a new Python backend alongside the existing production system with complete isolation and automatic GitHub synchronization.

**Key Principles:**
- ✅ New database (zero connection to production DB)
- ✅ New application folder (separate from existing app)
- ✅ New environment variables (isolated configuration)
- ✅ **GitHub auto-sync via FTP deployment** (push to GitHub = auto-deploy)
- ✅ Production remains untouched until cutover

**Timeline:** ~2-3 hours for complete setup and verification

---

## 🗄️ PHASE 1: DATABASE ISOLATION

### Why Separate Database?
- **Safety:** No risk of schema conflicts or data corruption
- **Testing:** Can test migrations without affecting production
- **Rollback:** Easy to revert by switching connection strings
- **Performance:** No query contention with production

### Step-by-Step Database Creation

#### 1.1 Create New Database
```
cPanel → MySQL® Databases → Create New Database

Database Name: fagierrands_new
(cPanel will prefix with your username: username_fagierrands_new)

✅ Click "Create Database"
```

**Record:** `username_fagierrands_new` (full database name)

#### 1.2 Create Dedicated Database User
```
cPanel → MySQL® Databases → MySQL Users → Add New User

Username: fagierrands_new_user
Password: [Generate strong password - 32+ characters]
✅ Use Password Generator
✅ Copy password to secure location (password manager)

Click "Create User"
```

**Record:** 
- Username: `username_fagierrands_new_user`
- Password: `[saved securely]`

#### 1.3 Grant Privileges
```
cPanel → MySQL® Databases → Add User To Database

User: username_fagierrands_new_user
Database: username_fagierrands_new

✅ Click "Add"

On privileges page:
✅ Check "ALL PRIVILEGES"
✅ Click "Make Changes"
```

#### 1.4 Verify Database Access
```bash
# SSH into cPanel
mysql -u username_fagierrands_new_user -p username_fagierrands_new

# Test commands:
SHOW TABLES;
SELECT DATABASE();
\q
```

**✅ Checkpoint:** Database accessible, no tables yet (clean slate)

---

## 🔗 PHASE 2: GITHUB AUTO-SYNC SETUP (CRITICAL STEP)

### Why GitHub Auto-Sync?
- **Efficiency:** Push to GitHub = Instant deployment
- **No manual FTP:** Eliminates manual file uploads
- **Version control:** Every deployment is tracked
- **Rollback:** Easy to revert to previous commits

### 2.1 Setup GitHub Deploy Key (SSH Authentication)

#### Generate SSH Key on cPanel:
```bash
# SSH into your cPanel server
ssh username@yourdomain.com

# Generate SSH key (no passphrase for automation)
ssh-keygen -t ed25519 -C "cpanel-deploy-fagierrands-new" -f ~/.ssh/cpanel_deploy_new

# Display public key
cat ~/.ssh/cpanel_deploy_new.pub
```

**Copy the entire public key output** (starts with `ssh-ed25519`)

#### Add Deploy Key to GitHub:
```
1. Go to: https://github.com/Fagierrands-Apps/fagierrands-dev-backend
2. Settings → Deploy keys → Add deploy key
3. Title: cPanel Auto-Deploy (New Backend)
4. Key: [paste public key from above]
5. ✅ Allow write access (UNCHECK - read-only is safer)
6. Click "Add key"
```

### 2.2 Setup Git Repository on cPanel

```bash
# Create repositories directory
mkdir -p ~/repositories
cd ~/repositories

# Clone repository using SSH
git clone git@github.com:Fagierrands-Apps/fagierrands-dev-backend.git fagierrands_new_backend

# Configure SSH for this repo
cd fagierrands_new_backend
git config core.sshCommand "ssh -i ~/.ssh/cpanel_deploy_new -o IdentitiesOnly=yes"

# Test connection
git fetch origin
```

**✅ Checkpoint:** Repository cloned successfully

### 2.3 Create Application Directory Structure

```bash
# Create application directories
mkdir -p ~/fagierrands_new_backend/{public_html,tmp,logs}

# Set permissions
chmod 755 ~/fagierrands_new_backend
chmod 755 ~/fagierrands_new_backend/public_html
```

### 2.4 Setup Automatic Deployment Script

Create: `~/repositories/fagierrands_new_backend/deploy.sh`

```bash
#!/bin/bash

# Configuration
REPO_DIR="$HOME/repositories/fagierrands_new_backend"
APP_DIR="$HOME/fagierrands_new_backend/public_html"
VENV_PATH="$HOME/virtualenv/fagierrands_new_backend/public_html/3.12"
LOG_FILE="$HOME/fagierrands_new_backend/logs/deploy.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Starting Deployment ==="

# Navigate to repository
cd "$REPO_DIR" || exit 1

# Pull latest changes
log "Pulling latest changes from GitHub..."
git pull origin main 2>&1 | tee -a "$LOG_FILE"

if [ $? -ne 0 ]; then
    log "ERROR: Git pull failed"
    exit 1
fi

# Sync to application directory (exclude .git, .env, etc.)
log "Syncing files to application directory..."
rsync -av --delete \
    --exclude='.git' \
    --exclude='.env' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='*.log' \
    --exclude='db.sqlite3' \
    "$REPO_DIR/" "$APP_DIR/" 2>&1 | tee -a "$LOG_FILE"

# Activate virtual environment
log "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Install/update dependencies
log "Installing dependencies..."
cd "$APP_DIR"
pip install -r requirements.txt --upgrade 2>&1 | tee -a "$LOG_FILE"

# Run migrations
log "Running database migrations..."
python manage.py migrate --noinput 2>&1 | tee -a "$LOG_FILE"

# Collect static files
log "Collecting static files..."
python manage.py collectstatic --noinput 2>&1 | tee -a "$LOG_FILE"

# Restart application
log "Restarting application..."
mkdir -p "$APP_DIR/tmp"
touch "$APP_DIR/tmp/restart.txt"

log "=== Deployment Complete ==="
log "Application restarted successfully"
```

**Make executable:**
```bash
chmod +x ~/repositories/fagierrands_new_backend/deploy.sh
```

### 2.5 Setup GitHub Webhook (Auto-Deploy on Push)

#### Option A: Using cPanel Cron Job (Recommended)
```
cPanel → Cron Jobs → Add New Cron Job

Minute: */5 (every 5 minutes)
Hour: *
Day: *
Month: *
Weekday: *

Command:
cd ~/repositories/fagierrands_new_backend && git fetch origin && [ $(git rev-parse HEAD) != $(git rev-parse @{u}) ] && ~/repositories/fagierrands_new_backend/deploy.sh

✅ Add Cron Job
```

**This checks for new commits every 5 minutes and auto-deploys if found.**

#### Option B: Using GitHub Actions (Advanced)
Create: `.github/workflows/deploy-cpanel.yml` in your repo

```yaml
name: Deploy to cPanel

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.CPANEL_HOST }}
          username: ${{ secrets.CPANEL_USER }}
          key: ${{ secrets.CPANEL_SSH_KEY }}
          script: |
            ~/repositories/fagierrands_new_backend/deploy.sh
```

**Add secrets in GitHub:**
```
Repository → Settings → Secrets and variables → Actions
Add:
- CPANEL_HOST: yourdomain.com
- CPANEL_USER: username
- CPANEL_SSH_KEY: [private key content from ~/.ssh/cpanel_deploy_new]
```

### 2.6 Test Auto-Deployment

```bash
# Make a test change
cd ~/repositories/fagierrands_new_backend
echo "# Test deployment" >> README.md
git add README.md
git commit -m "Test auto-deployment"
git push origin main

# Wait 5 minutes (if using cron) or check GitHub Actions

# Verify deployment
tail -f ~/fagierrands_new_backend/logs/deploy.log
```

**✅ Checkpoint:** Changes from GitHub appear in application directory automatically

---

## 🐍 PHASE 3: PYTHON APPLICATION SETUP

### 3.1 Setup Python App in cPanel

```
cPanel → Setup Python App → Create Application

Python Version: 3.12.x (or latest available)
Application Root: fagierrands_new_backend/public_html
Application URL: new-api.yourdomain.com (or subdomain)
Application Startup File: passenger_wsgi.py
Application Entry Point: application

✅ Click "Create"
```

**Important:** cPanel creates a virtual environment at:
`/home/username/virtualenv/fagierrands_new_backend/public_html/3.12/`

**Record:**
- Virtual env path: `[shown in cPanel after creation]`
- Python version: `3.12.x`
- Command to enter venv: `source /home/username/virtualenv/[path]/bin/activate`

### 3.2 Configure Environment Variables (SECURE METHOD)

**❌ NEVER:** Put credentials in code or commit to Git

**✅ CORRECT:** Use cPanel Python App environment variables

```
cPanel → Setup Python App → [Your New App] → Edit

Scroll to "Environment Variables" section:

Add each variable:

Variable Name: DEBUG
Value: False

Variable Name: SECRET_KEY
Value: [generate: python -c "import secrets; print(secrets.token_urlsafe(50))"]

Variable Name: DATABASE_NAME
Value: username_fagierrands_new

Variable Name: DATABASE_USER
Value: username_fagierrands_new_user

Variable Name: DATABASE_PASSWORD
Value: [password from Phase 1]

Variable Name: DATABASE_HOST
Value: localhost

Variable Name: DATABASE_PORT
Value: 3306

Variable Name: ALLOWED_HOSTS
Value: new-api.yourdomain.com,yourdomain.com

Variable Name: GOOGLE_MAPS_API_KEY
Value: [your API key]

Variable Name: CORS_ALLOWED_ORIGINS
Value: https://yourdomain.com,https://new-api.yourdomain.com

[Add all other required environment variables]

✅ Click "Save"
```

**Security Note:** These variables are only accessible to your application, not visible in code or Git.

---

## 🚀 PHASE 4: INITIALIZATION & HEALTH CHECK

### 4.1 Install Dependencies

```bash
# Activate virtual environment
source ~/virtualenv/fagierrands_new_backend/public_html/3.12/bin/activate

# Navigate to app directory
cd ~/fagierrands_new_backend/public_html

# Verify Python version
python --version  # Should show 3.12.x

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installations
pip list | grep -i django
pip list | grep -i rest
```

### 4.2 Run Django Migrations

```bash
# Still in activated venv
cd ~/fagierrands_new_backend/public_html

# Check migration status
python manage.py showmigrations

# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser
# Username: admin
# Email: admin@yourdomain.com
# Password: [secure password]

# Collect static files
python manage.py collectstatic --noinput
```

### 4.3 Create passenger_wsgi.py

Create: `~/fagierrands_new_backend/public_html/passenger_wsgi.py`

```python
import sys
import os

# Add application directory to path
INTERP = "/home/username/virtualenv/fagierrands_new_backend/public_html/3.12/bin/python"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'fagierrandsbackup.settings'

# Add project directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Set permissions:**
```bash
chmod 644 ~/fagierrands_new_backend/public_html/passenger_wsgi.py
```

### 4.4 Restart Application

```bash
# Create restart trigger
mkdir -p ~/fagierrands_new_backend/public_html/tmp
touch ~/fagierrands_new_backend/public_html/tmp/restart.txt
```

**Or via cPanel:**
```
cPanel → Setup Python App → [Your App] → Restart
```

### 4.5 Health Check & Verification

#### Check Deployment Logs:
```bash
# Deployment log
tail -f ~/fagierrands_new_backend/logs/deploy.log

# Application error log
tail -f ~/fagierrands_new_backend/logs/error.log

# Passenger log
tail -f ~/logs/passenger.log
```

#### Test Endpoints:
```bash
# Health check
curl https://new-api.yourdomain.com/

# Admin panel
curl https://new-api.yourdomain.com/admin/

# API endpoint
curl https://new-api.yourdomain.com/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"test","password":"test"}'
```

#### Verify Database Connection:
```bash
cd ~/fagierrands_new_backend/public_html
source ~/virtualenv/fagierrands_new_backend/public_html/3.12/bin/activate

python manage.py shell

# In Python shell:
from django.db import connection
connection.ensure_connection()
print("✅ Database connected!")
exit()
```

---

## 🔧 PHASE 5: TROUBLESHOOTING COMMON ISSUES

### Issue 1: "Application failed to start"

**Check:**
```bash
# View full error
cat ~/fagierrands_new_backend/logs/error.log

# Common causes:
# 1. Wrong Python path in passenger_wsgi.py
# 2. Missing dependencies
# 3. Database connection failure
```

**Fix:**
```bash
# Verify virtual env path
ls -la ~/virtualenv/fagierrands_new_backend/public_html/

# Reinstall dependencies
source [venv_path]/bin/activate
pip install -r requirements.txt --force-reinstall

# Test Django directly
python manage.py runserver 0.0.0.0:8000
# If this works, issue is with passenger_wsgi.py
```

### Issue 2: "Git pull fails / Auto-sync not working"

**Check:**
```bash
# Test SSH connection to GitHub
ssh -T git@github.com -i ~/.ssh/cpanel_deploy_new

# Should see: "Hi Fagierrands-Apps! You've successfully authenticated"

# Check cron job
crontab -l | grep deploy

# Manual test
cd ~/repositories/fagierrands_new_backend
git pull origin main
```

**Fix:**
```bash
# Re-add SSH key to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/cpanel_deploy_new

# Update git remote to use SSH
cd ~/repositories/fagierrands_new_backend
git remote set-url origin git@github.com:Fagierrands-Apps/fagierrands-dev-backend.git

# Test again
git pull origin main
```

### Issue 3: "ModuleNotFoundError"

**Fix:**
```bash
# Activate venv
source ~/virtualenv/fagierrands_new_backend/public_html/3.12/bin/activate

# Install missing module
pip install [module_name]

# Update requirements.txt
pip freeze > requirements.txt

# Commit and push (will auto-deploy)
git add requirements.txt
git commit -m "Add missing dependency"
git push origin main

# Restart
touch ~/fagierrands_new_backend/public_html/tmp/restart.txt
```

### Issue 4: "Database connection refused"

**Check:**
```bash
# Test MySQL connection
mysql -u username_fagierrands_new_user -p username_fagierrands_new

# Verify environment variables
cPanel → Setup Python App → [Your App] → Edit
# Check DATABASE_* variables match database credentials
```

### Issue 5: "502 Bad Gateway"

**Causes:**
- Application crashed
- Passenger not starting
- Wrong application entry point

**Fix:**
```bash
# Check passenger status
passenger-status

# Verify passenger_wsgi.py exists and is readable
ls -la ~/fagierrands_new_backend/public_html/passenger_wsgi.py

# Check for syntax errors
python ~/fagierrands_new_backend/public_html/passenger_wsgi.py
# Should not output errors

# Force restart
touch ~/fagierrands_new_backend/public_html/tmp/restart.txt
```

---

## ✅ SAFETY CHECKLIST (Pre-Cutover)

### Database Verification
- [ ] New database created and accessible
- [ ] Dedicated user with correct privileges
- [ ] No connection to production database
- [ ] Migrations completed successfully
- [ ] Test data inserted and retrievable

### GitHub Auto-Sync Verification
- [ ] SSH key added to GitHub
- [ ] Repository clones successfully
- [ ] Deploy script executes without errors
- [ ] Cron job or GitHub Actions configured
- [ ] Test push triggers auto-deployment
- [ ] Deployment logs show success

### Application Verification
- [ ] Application starts without errors
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] passenger_wsgi.py correct and executable
- [ ] Static files collected and accessible

### Endpoint Testing
- [ ] Admin panel accessible (`/admin/`)
- [ ] API endpoints responding
- [ ] Authentication working
- [ ] Database queries executing
- [ ] CORS configured correctly

### Performance Check
- [ ] Response times acceptable (<500ms)
- [ ] No memory leaks (monitor for 1 hour)
- [ ] Passenger processes stable
- [ ] Database connections pooling correctly

### Security Audit
- [ ] DEBUG = False in production
- [ ] SECRET_KEY is strong and unique
- [ ] ALLOWED_HOSTS configured
- [ ] Database credentials not in code
- [ ] HTTPS enforced
- [ ] CORS origins whitelisted
- [ ] SSH keys secured (not in repo)

### Rollback Plan
- [ ] Production app still running
- [ ] Production database untouched
- [ ] Can revert DNS/URL changes instantly
- [ ] Backup of new database before cutover
- [ ] Documentation of all changes

---

## 🔄 CUTOVER STRATEGY

### Option 1: DNS Switch (Recommended)
```
1. Test new backend: https://new-api.yourdomain.com
2. Update frontend configs to point to new URL
3. Deploy frontend changes
4. Monitor for 24 hours
5. If stable, deprecate old backend
```

### Option 2: Gradual Migration
```
1. Route 10% of traffic to new backend
2. Monitor error rates
3. Increase to 50% if stable
4. Full cutover after 48 hours
5. Keep old backend as fallback for 1 week
```

### Option 3: Feature Flag
```
1. Add feature flag in frontend
2. Enable new backend for internal users
3. Test thoroughly
4. Enable for all users
5. Remove old backend after 2 weeks
```

---

## 📊 MONITORING POST-DEPLOYMENT

### Key Metrics to Watch:
```bash
# Deployment logs
tail -f ~/fagierrands_new_backend/logs/deploy.log

# Application logs
tail -f ~/fagierrands_new_backend/logs/error.log

# Passenger status
watch -n 5 'passenger-status'

# Database connections
mysql -u username_fagierrands_new_user -p -e "SHOW PROCESSLIST;"

# Disk usage
df -h ~/fagierrands_new_backend/

# Memory usage
free -h
```

### Alert Thresholds:
- Response time > 1 second
- Error rate > 1%
- Database connections > 80% of max
- Disk usage > 80%
- Memory usage > 90%
- Deployment failures > 0

---

## 🎯 DAILY WORKFLOW (After Setup)

### Making Changes:
```bash
# On your local machine
git add .
git commit -m "Your changes"
git push origin main

# Wait 5 minutes (cron) or instant (GitHub Actions)
# Changes automatically deployed to cPanel!

# Verify deployment
curl https://new-api.yourdomain.com/api/health/
```

### Checking Deployment Status:
```bash
# SSH into cPanel
ssh username@yourdomain.com

# Check last deployment
tail -20 ~/fagierrands_new_backend/logs/deploy.log

# Check application status
passenger-status
```

### Rolling Back:
```bash
# SSH into cPanel
cd ~/repositories/fagierrands_new_backend

# Revert to previous commit
git log --oneline -5  # Find commit hash
git reset --hard [commit_hash]

# Run deployment manually
~/repositories/fagierrands_new_backend/deploy.sh
```

---

## 🎯 FINAL NOTES

**Critical Success Factors:**
1. ✅ Complete isolation from production
2. ✅ GitHub auto-sync working reliably
3. ✅ Thorough testing before cutover
4. ✅ Clear rollback plan
5. ✅ Monitoring in place
6. ✅ Team communication

**Timeline:**
- Database setup: 30 minutes
- GitHub auto-sync: 1 hour
- Application setup: 1 hour
- Testing: 2-4 hours
- Cutover: 15 minutes
- Monitoring: 24-48 hours

**Support:**
- Keep old backend running for 1 week minimum
- Document all configuration changes
- Train team on new deployment process
- Monitor deployment logs daily

---

## 📝 QUICK REFERENCE COMMANDS

### Deploy Manually:
```bash
~/repositories/fagierrands_new_backend/deploy.sh
```

### Restart Application:
```bash
touch ~/fagierrands_new_backend/public_html/tmp/restart.txt
```

### Check Logs:
```bash
tail -f ~/fagierrands_new_backend/logs/deploy.log
tail -f ~/fagierrands_new_backend/logs/error.log
```

### Update Dependencies:
```bash
source ~/virtualenv/fagierrands_new_backend/public_html/3.12/bin/activate
cd ~/fagierrands_new_backend/public_html
pip install -r requirements.txt --upgrade
```

### Run Migrations:
```bash
source ~/virtualenv/fagierrands_new_backend/public_html/3.12/bin/activate
cd ~/fagierrands_new_backend/public_html
python manage.py migrate
```

---

**You are now ready to deploy your new backend with GitHub auto-sync and zero risk to production!** 🚀
