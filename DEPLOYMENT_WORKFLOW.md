# Deployment Workflow Documentation

## Successfully Configured - June 2, 2026

### Automatic Deployment Setup

This project uses GitHub Actions for automatic deployment to two environments:

## 1. Production cPanel Deployment
**Branch:** `production-cpanel`  
**Trigger:** Push to production-cpanel branch  
**Destination:** `/api.errandserver.fagitone.com/` on cPanel  
**Method:** FTP Deploy Action

### Required GitHub Secrets (Already Configured):
- `FTP_SERVER` - cPanel FTP server address
- `FTP_USERNAME` - cPanel FTP username
- `FTP_PASSWORD` - cPanel FTP password

**Workflow File:** `.github/workflows/deploy.yml`

## 2. Render Deployment
**Branch:** `main`  
**Trigger:** Push to main branch  
**Destination:** Render hosting service  
**Method:** Deploy Hook

### Required GitHub Secret (Already Configured):
- `RENDER_DEPLOY_HOOK` - Render webhook URL

**Workflow File:** `.github/workflows/deploy-render.yml`

---

## How It Works

### Deploy to cPanel (Production)
```bash
git checkout production-cpanel
git merge main  # or make changes directly
git push origin production-cpanel
```
→ Automatically deploys to cPanel via FTP

### Deploy to Render (Main/Development)
```bash
git checkout main
# make changes
git push origin main
```
→ Automatically triggers Render deployment

---

## Deployment Status
✅ **First successful cPanel deployment:** June 2, 2026 at 11:45 AM EAT  
✅ **Render deployment:** Configured and ready  
✅ **GitHub Actions:** Active and working

---

## Notes
- Both workflows exclude `.git`, `.github`, and `.env` files from deployment
- cPanel deployment uses FTP-Deploy-Action@4.3.3
- Render deployment uses webhook trigger via curl
- No manual deployment needed - just push to the respective branch
