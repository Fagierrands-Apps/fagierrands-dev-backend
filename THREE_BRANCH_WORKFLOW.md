# 🌳 Three-Branch Deployment Strategy

## Branch Structure

```
main               → Development/Testing (Render)
  ↓ (after testing)
production         → Stable code
  ↓ (after approval)
production-cpanel  → Live Production (cPanel)
```

## ✅ Setup Complete

All three branches are ready:
- ✓ `main` - Development branch (connected to Render)
- ✓ `production` - Staging/stable branch
- ✓ `production-cpanel` - Production branch (with cPanel .env)

## 📋 Daily Workflow

### 1. Development & Testing (main → Render)

```bash
# Work on main branch
git checkout main

# Make your changes
# ... edit code ...

# Commit and push
git add .
git commit -m "Add new feature"
git push origin main

# Render automatically deploys and tests
# Wait for tests to pass ✓
```

### 2. After Successful Testing (main → production)

```bash
# Switch to production
git checkout production

# Merge tested code from main
git merge main

# Push to GitHub
git push origin production

# Review one more time if needed
# This is your "staging" branch
```

### 3. Deploy to cPanel (production → production-cpanel)

```bash
# Switch to production-cpanel
git checkout production-cpanel

# Merge stable code from production
git merge production

# Push to GitHub
git push origin production-cpanel

# On cPanel server (SSH):
cd ~/your-app-directory
git pull origin production-cpanel
touch tmp/restart.txt  # Restart app
```

## 🎯 Quick Commands

### See all branches
```bash
git branch -a
```

### Check current branch
```bash
git branch --show-current
```

### Switch branch
```bash
git checkout main           # Development
git checkout production     # Stable
git checkout production-cpanel  # Production
```

## 🔍 Branch Differences

| Branch | Purpose | Environment | .env Content | Auto-Deploy |
|--------|---------|-------------|--------------|-------------|
| `main` | Development | Render | DATABASE_URL | Yes (Render) |
| `production` | Stable/Staging | Render | DATABASE_URL | Yes (Render) |
| `production-cpanel` | Production | cPanel | DB_NAME, DB_USER | Manual git pull |

## 🚀 Example: Adding a New Feature

```bash
# Day 1: Development
git checkout main
# ... add feature ...
git commit -m "Add user profile feature"
git push origin main
# Test on Render dev environment

# Day 2: Testing passed, move to staging
git checkout production
git merge main
git push origin production
# Test on Render production environment

# Day 3: All good, deploy to cPanel
git checkout production-cpanel
git merge production
git push origin production-cpanel
# SSH to cPanel and git pull
```

## 🛡️ Safety Features

1. **Never push directly to production-cpanel**
   - Always merge from `production` first
   
2. **Test on Render before cPanel**
   - Render = your testing ground
   - cPanel = real users
   
3. **Quick rollback**
   ```bash
   git checkout production-cpanel
   git reset --hard HEAD~1  # Go back one commit
   git push origin production-cpanel --force
   ```

## 📊 Branch Status

```bash
# View commit differences
git log main..production           # What's in main but not in production
git log production..production-cpanel  # What's in production but not on cPanel
```

## 🎉 Benefits

- ✅ Test everything on Render first (free testing!)
- ✅ Stable production branch for cPanel
- ✅ Easy rollback if something breaks
- ✅ Clear separation: dev → staging → production
- ✅ Same file structure on all branches
