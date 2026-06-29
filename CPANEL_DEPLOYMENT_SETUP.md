# 🚀 cPanel Auto-Deployment Setup Guide

**Created:** 2026-06-07  
**Branch:** production-clean → cPanel

---

## 📋 SETUP STEPS

### 1. GitHub Secrets Configuration

Go to: https://github.com/Fagierrands-Apps/fagierrands-dev-backend/settings/secrets/actions

Add these secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `FTP_SERVER` | `ftp.distinctivecollections.co.ke` | cPanel FTP server |
| `FTP_USERNAME` | Your cPanel FTP username | FTP account user |
| `FTP_PASSWORD` | Your cPanel FTP password | FTP account password |

### 2. cPanel FTP Account Setup

**Option A: Use main cPanel account**
- Username: Your main cPanel username
- Password: Your cPanel password

**Option B: Create dedicated FTP account** (Recommended)
1. Login to cPanel
2. Go to "FTP Accounts"
3. Create new account:
   - Username: `deploy_bot`
   - Directory: `/home3/distinc3/fagierrandsbackendapi`
   - Quota: Unlimited
4. Set strong password
5. Use this in GitHub secrets

### 3. Deployment Directory

**Current Setting (TEST FOLDER):**
```yaml
server-dir: /xxxdx/
```

**Full Path on Server:**
`/home3/distinc3/xxxdx/`

⚠️ **This is a TEST deployment folder. Production folder is `/fagierrandsbackendapi/`**

**Once verified working:**
1. Test all files deployed correctly to `/xxxdx/`
2. Verify workflow runs without errors
3. Change `server-dir: /xxxdx/` to `server-dir: /fagierrandsbackendapi/`
4. Push to deploy to actual production

### 4. Protected Files (Won't be overwritten)

These files are excluded from deployment:
- `.env` - Environment variables
- `db.sqlite3` - Database
- `logs/` - Log files
- `media/` - User uploads
- `__pycache__/` - Python cache
- `.git/` - Git data

---

## 🔄 WORKFLOW DETAILS

### Trigger
```yaml
on:
  push:
    branches: 
      - production-clean
```
Deploys automatically when you push to `production-clean` branch.

### Excluded Files
- Git files (`.git`, `.github`)
- Environment files (`.env`)
- Database (`db.sqlite3`)
- Logs (`logs/`)
- Media (`media/`)
- Python cache (`__pycache__/`, `*.pyc`)

### Deployment Action
Uses: `SamKirkland/FTP-Deploy-Action@v4`
- Syncs files via FTPS
- Only uploads changed files
- Preserves server-only files

---

## ✅ TESTING THE WORKFLOW

### Step 1: Set GitHub Secrets
```bash
# Go to GitHub repo → Settings → Secrets and variables → Actions
# Add the 3 secrets listed above
```

### Step 2: Push test file
```bash
# File already created: test_deployment.txt
git push origin production-clean
```

### Step 3: Monitor Deployment
1. Go to: https://github.com/Fagierrands-Apps/fagierrands-dev-backend/actions
2. Watch the deployment job
3. Check for errors

### Step 4: Verify on cPanel
1. SSH or File Manager in cPanel
2. Check: `/home3/distinc3/fagierrandsbackendapi/`
3. Look for `test_deployment.txt`
4. If present → **Deployment works!** ✅

---

## 🔧 TROUBLESHOOTING

### Error: "Failed to connect to FTP"
- Check FTP credentials in GitHub secrets
- Verify FTP server address
- Check cPanel firewall

### Error: "Permission denied"
- FTP user needs write access to `/fagierrandsbackendapi/`
- Check directory permissions in cPanel

### Error: "Directory not found"
- Verify `server-dir: /fagierrandsbackendapi/` is correct
- Check full path in cPanel File Manager

### Files not updating
- Check exclude patterns
- Clear GitHub Actions cache
- Force push: `git push -f origin production-clean`

---

## 📊 DEPLOYMENT FLOW

```
Local Dev → Git Push → GitHub Actions → FTP Upload → cPanel → LiteSpeed Restart
```

### Timeline
1. Push code: 2 seconds
2. GitHub Actions start: 5-10 seconds
3. FTP upload: 30-60 seconds
4. LiteSpeed detects change: 5-10 seconds
5. **Total: ~1-2 minutes** ⏱️

---

## 🔐 SECURITY NOTES

### DO NOT Commit:
- ❌ `.env` files
- ❌ Database files
- ❌ FTP credentials
- ❌ Secret keys

### Protected on Server:
- `.env` - Never overwritten
- `db.sqlite3` - Never overwritten
- `logs/` - Never overwritten
- `media/` - Never overwritten

---

## 🎯 USAGE

### Normal Development Flow

```bash
# 1. Make changes in main branch (dev)
git checkout main
# ... edit files ...
git add .
git commit -m "Add new feature"
git push origin main

# 2. Test locally

# 3. Merge to production when ready
git checkout production-clean
git merge main
git push origin production-clean  # 🚀 Auto-deploys!
```

### Emergency Hotfix

```bash
# Direct fix on production-clean
git checkout production-clean
# ... fix critical bug ...
git add .
git commit -m "Hotfix: critical payment bug"
git push origin production-clean  # 🚀 Deploys immediately!

# Then backport to main
git checkout main
git cherry-pick <commit-hash>
git push origin main
```

---

## 📝 POST-DEPLOYMENT CHECKLIST

After successful deployment:

- [ ] Check GitHub Actions log - all green
- [ ] Verify file on cPanel File Manager
- [ ] Test API endpoint: `https://fagierrandsbackendapi.distinctivecollections.co.ke/`
- [ ] Check Django logs for errors
- [ ] Test critical endpoints (login, orders, payment)
- [ ] Monitor for 5-10 minutes

---

## 🔄 ROLLBACK PROCEDURE

If deployment breaks production:

```bash
# Option 1: Revert commit
git revert HEAD
git push origin production-clean  # Deploys previous version

# Option 2: Reset to previous commit
git reset --hard HEAD~1
git push -f origin production-clean  # Force deploy old version

# Option 3: Manual FTP upload
# Use FileZilla to upload previous backup
```

---

## 📞 SUPPORT

### Check Deployment Status
https://github.com/Fagierrands-Apps/fagierrands-dev-backend/actions

### Check Server Logs
cPanel → Errors → View last 300 errors

### API Health Check
```bash
curl https://fagierrandsbackendapi.distinctivecollections.co.ke/api/orders/
```

---

## ✅ VERIFICATION CHECKLIST

Before going live:

- [ ] GitHub secrets configured (FTP_SERVER, FTP_USERNAME, FTP_PASSWORD)
- [ ] Test file deployed successfully
- [ ] Protected files NOT overwritten (.env, db.sqlite3)
- [ ] API responds after deployment
- [ ] No errors in GitHub Actions log
- [ ] LiteSpeed restarted automatically
- [ ] Django serving requests

---

## 🎉 SUCCESS CRITERIA

Deployment is successful when:
1. ✅ GitHub Actions shows green checkmark
2. ✅ Files updated on cPanel
3. ✅ API endpoint responds
4. ✅ No errors in Django logs
5. ✅ Protected files untouched

---

**Current Status:** Workflow configured, ready for testing

**Next Step:** Configure GitHub secrets and push to production-clean

---

**END OF SETUP GUIDE**
