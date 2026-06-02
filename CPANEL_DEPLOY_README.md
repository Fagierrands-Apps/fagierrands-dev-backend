# cPanel Deployment - Quick Guide

## ✨ Key Feature: SAME File Structure as Render!

Both Render and cPanel use:
- ✅ Same `settings.py` (auto-detects environment)
- ✅ Same `passenger_wsgi.py` 
- ✅ Same folder structure
- ✅ Same `manage.py` commands

**Only Difference:** `.env` file contents (Render uses DATABASE_URL, cPanel uses DB_NAME, DB_USER, etc.)

## The Problem We Solved
- No more adding 21 environment variables manually
- No more separate settings files
- No more different code structures
- No more app crashes during creation

## 🚀 Deploy in 3 Steps

### Step 1: Create Production Branch
```bash
./deploy_to_cpanel.sh
```
This creates a `production-cpanel` branch with `.env` file containing cPanel credentials.

### Step 2: Push to GitHub
```bash
git push origin production-cpanel
```

### Step 3: On cPanel
```bash
# Clone production branch
git clone -b production-cpanel https://github.com/YOUR_USERNAME/fagierrands-dev-backend.git

# Create Python App in cPanel
# - Point to the directory
# - Python will automatically load .env file

# Install dependencies (same as Render)
source /path/to/virtualenv/bin/activate
pip install -r requirements.txt

# Run migrations (same as Render)
python manage.py migrate

# Collect static files (same as Render)
python manage.py collectstatic --noinput

# Done! App starts automatically
```

## 🔄 How Settings Auto-Detection Works

The `settings.py` checks for `DATABASE_URL` environment variable:

```python
database_url = os.getenv('DATABASE_URL')

if not database_url:
    # cPanel: use DB_NAME, DB_USER, DB_PASSWORD from .env
    DATABASES = { ... }
elif database_url.startswith('postgresql'):
    # Render: use DATABASE_URL from .env
    DATABASES = dj_database_url.config(...)
```

**Render `.env`:**
```bash
DATABASE_URL=postgresql://user:pass@host/db
```

**cPanel `.env`:**
```bash
DB_NAME=distinc3_fagierrandsNew
DB_USER=distinc3_FagierrandsNew
DB_PASSWORD=Pa7swrd1990@
```

## 📁 File Structure (Identical on Both)

```
fagierrands-dev-backend/
├── .env                      (Different content, same location)
├── manage.py                 (Identical)
├── passenger_wsgi.py         (Identical)
├── requirements.txt          (Identical)
├── fagierrandsbackup/
│   ├── settings.py          (Identical - auto-detects!)
│   ├── wsgi.py              (Identical)
│   └── urls.py              (Identical)
├── accounts/                 (Identical)
├── orders/                   (Identical)
└── [all other apps]          (Identical)
```

## 🔄 Updating Code (Same Process)

```bash
# Make changes on main branch
git checkout main
# ... your changes ...
git commit -m "New feature"
git push origin main

# Merge to production
git checkout production-cpanel
git merge main
git push origin production-cpanel

# On both Render and cPanel: just git pull
cd ~/your-app-directory
git pull
touch tmp/restart.txt  # cPanel restart
# Render restarts automatically
```

## 📝 Important Notes

1. **Same commands everywhere**: `python manage.py migrate` works on both
2. **Same imports**: No need to change `DJANGO_SETTINGS_MODULE`
3. **One codebase**: Only branch difference is `.env` file
4. **Easy testing**: Test on Render, deploy same code to cPanel

## 🔐 Security

- `.env` committed ONLY to `production-cpanel` branch
- Never committed to `main` branch
- Same security practices on both platforms
