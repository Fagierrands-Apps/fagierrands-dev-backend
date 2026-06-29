# FagiErrands Production Backend

Live production server for FagiErrands application.

## 🚀 Auto-Deployment Setup

This repository deploys automatically to cPanel when you push to `main` branch.

### Deployment Flow
```
Push to main → GitHub Actions → FTP to cPanel → App Restarts
```

### Server Details
- **Path**: `/home3/distinc3/fagierrandsbackendapi`
- **Protocol**: FTPS
- **Trigger**: Push to `main` branch

## 📁 Project Structure

```
FagiErrands-Prod-server/
├── accounts/          # User authentication & management
├── admin_dashboard/   # Admin panel
├── app/              # Main app configuration
├── core/             # Core utilities (SMS, payments, etc.)
├── fagierrands/      # Django project settings
├── locations/        # Location management
├── marketplace/      # Marketplace features
├── notifications/    # Notification system
├── orders/           # Order management & payments
├── static/           # Static files
├── templates/        # HTML templates
├── passenger_wsgi.py # cPanel WSGI entry point
├── manage.py         # Django management
└── requirements.txt  # Python dependencies
```

## 🔒 Protected Files

These files are NEVER overwritten during deployment:
- `.env` - Environment configuration
- `db.sqlite3` - Production database
- `logs/` - Server logs
- `media/` - User uploads

## 💻 Quick Start for Developers

### Making Changes

```bash
# 1. Work in your local directory
cd /home/fagitone/Documents/new-backend
# Make your changes...

# 2. Use sync helper to deploy
cd /home/fagitone/Documents/GitHub/FagiErrands-Prod-server
./sync_and_deploy.sh
```

### Manual Workflow

```bash
# Sync changes
rsync -av /home/fagitone/Documents/new-backend/ \
  /home/fagitone/Documents/GitHub/FagiErrands-Prod-server/ \
  --exclude='.env' --exclude='*.sqlite3' --exclude='logs/' \
  --exclude='__pycache__' --exclude='*.pyc'

# Commit and deploy
cd /home/fagitone/Documents/GitHub/FagiErrands-Prod-server
git add .
git commit -m "Your changes"
git push origin main
```

## 📊 Monitoring Deployments

Watch deployment progress:
https://github.com/Fagierrands-Apps/FagiErrands-Prod-server/actions

## 🆘 Emergency Rollback

```bash
# Revert last commit
git revert HEAD
git push origin main
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Full deployment instructions
- [GitHub Secrets](GITHUB_SECRETS.md) - Secrets configuration

## ⚠️ Important Notes

1. **Test locally before pushing**
2. **Use descriptive commit messages**
3. **Monitor first deployment closely**
4. **Deploy during low-traffic times for major changes**
5. **Never commit .env or database files**

## 🔧 Technical Stack

- **Framework**: Django
- **Python**: 3.x
- **Server**: cPanel with Passenger
- **Database**: SQLite (production)
- **Deployment**: GitHub Actions + FTP

## 📞 Support

- Check GitHub Actions logs for deployment issues
- Check cPanel logs: `/home3/distinc3/fagierrandsbackendapi/logs/`
- Contact: System Administrator

