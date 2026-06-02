#!/bin/bash
# Simple script to create production-cpanel branch

echo "=== Creating cPanel Production Branch ==="
echo ""
echo "✨ Key Feature: SAME file structure as Render!"
echo "   - Same settings.py (auto-detects environment)"
echo "   - Only difference: .env file with cPanel credentials"
echo ""

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Create/switch to production branch
if git show-ref --verify --quiet refs/heads/production-cpanel; then
    echo "Switching to existing production-cpanel branch..."
    git checkout production-cpanel
else
    echo "Creating new production-cpanel branch from main..."
    git checkout -b production-cpanel
fi

# Copy .env.cpanel to .env (this will be committed ONLY to production branch)
cp .env.cpanel .env

# Add files
git add .env
git add passenger_wsgi.py
git add fagierrandsbackup/settings.py

# Commit
git commit -m "Production branch with cPanel .env file (same structure as Render)"

echo ""
echo "✅ Production branch ready!"
echo ""
echo "📋 What's included:"
echo "  - Same settings.py as Render (auto-detects DB config)"
echo "  - .env file with cPanel credentials"
echo "  - Same passenger_wsgi.py"
echo "  - NO separate settings_production.py"
echo ""
echo "🚀 Next steps:"
echo "  1. Push to GitHub:"
echo "     git push origin production-cpanel"
echo ""
echo "  2. On cPanel, clone this branch:"
echo "     git clone -b production-cpanel https://github.com/USERNAME/fagierrands-dev-backend.git"
echo ""
echo "  3. Install & Run (same as Render):"
echo "     pip install -r requirements.txt"
echo "     python manage.py migrate"
echo "     python manage.py collectstatic --noinput"
echo ""
echo "💡 To return to main: git checkout main"
echo ""
