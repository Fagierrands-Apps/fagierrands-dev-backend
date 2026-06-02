# cPanel Folder Separation Setup (Like Existing Backend)

## Current Working Setup:
- **Public Domain:** errandserver.fagitone.com
- **Files Location:** fagiserver.fagtone.com
- **Works via:** .htaccess redirect

## New Setup (Same Pattern):
- **Public Domain:** api.errandserver.fagierrands.com
- **Files Location:** api.fagierrands.backend (or similar - you choose)
- **Works via:** .htaccess redirect

---

## Implementation Steps

### Step 1: Choose File Location Folder Name
Options:
1. `fagierrands.backend`
2. `fagierrands.api`
3. `api.backend.fagierrands`

**Recommendation:** Use `fagierrands.backend` (mirrors your existing pattern)

### Step 2: Update GitHub Deployment
Change deployment path to the FILES folder, not the public domain folder.

**Update:** `.github/workflows/deploy.yml`
```yaml
server-dir: fagierrands.backend/  # Changed from api.errandserver.fagierrands.com/
```

### Step 3: Create Python App on FILES Folder
In cPanel → Setup Python App:
- Application Root: `fagierrands.backend` (not api.errandserver.fagierrands.com)
- Python Version: 3.11
- Create app here

### Step 4: Create .htaccess in Public Domain Folder
In `/home3/distinc3/api.errandserver.fagierrands.com/.htaccess`:

```apache
# Redirect to actual backend location
PassengerAppRoot "/home3/distinc3/fagierrands.backend"
PassengerBaseURI "/"
PassengerPython "/home3/distinc3/virtualenv/fagierrands.backend/3.11/bin/python3.11"
PassengerAppLogFile "/home3/distinc3/logs/api.errandserver.fagierrands.com.error.log"
PassengerEnabled On
```

---

## Why This is Better:

✅ **Separates concerns:** Public URL vs actual files  
✅ **Easier updates:** Change files without touching public folder  
✅ **Mirrors working setup:** Same pattern as existing backend  
✅ **Cleaner:** Public folder only has .htaccess  

---

## Quick Setup Process:

1. **Delete current mess:**
   - Delete Python app
   - Delete `api.errandserver.fagierrands.com` folder content (keep the folder)

2. **Create new backend folder:**
   - In File Manager: Create folder `fagierrands.backend`

3. **Update Git deployment path:**
   ```yaml
   server-dir: fagierrands.backend/
   ```

4. **Push to GitHub** (auto-deploys to `fagierrands.backend`)

5. **Create Python app** on `fagierrands.backend` folder

6. **Fix passenger_wsgi.py** in `fagierrands.backend` (as before)

7. **Create .htaccess** in `api.errandserver.fagierrands.com` pointing to `fagierrands.backend`

8. **Done!**

---

## URLs:
- Public: `http://api.errandserver.fagierrands.com/admin/`
- Backend files: `/home3/distinc3/fagierrands.backend/`

---

Ready to implement this better approach?
