#!/bin/bash
# Final verification before deploying

echo "🔍 Verifying Same File Structure Setup..."
echo ""

echo "✅ Checking key files..."
echo ""

# Check settings.py has auto-detection
if grep -q "if not database_url:" fagierrandsbackup/settings.py; then
    echo "✓ settings.py has auto-detection logic"
else
    echo "✗ settings.py missing auto-detection"
    exit 1
fi

# Check passenger_wsgi uses same settings
if grep -q "fagierrandsbackup.settings" passenger_wsgi.py && ! grep -q "settings_production" passenger_wsgi.py; then
    echo "✓ passenger_wsgi.py uses same settings as Render"
else
    echo "✗ passenger_wsgi.py has wrong settings module"
    exit 1
fi

# Check .env.cpanel exists
if [ -f .env.cpanel ]; then
    echo "✓ .env.cpanel exists for production branch"
else
    echo "✗ .env.cpanel missing"
    exit 1
fi

# Check no separate settings files
if [ ! -f fagierrandsbackup/settings_production.py ] && [ ! -f fagierrandsbackup/settings_cpanel.py ]; then
    echo "✓ No separate settings files (good!)"
else
    echo "✗ Found separate settings files (should be deleted)"
    exit 1
fi

echo ""
echo "📊 File Structure Comparison:"
echo ""
echo "Render (main branch):"
echo "  └── .env (DATABASE_URL=postgresql://...)"
echo "      └── settings.py detects and uses DATABASE_URL"
echo ""
echo "cPanel (production-cpanel branch):"
echo "  └── .env (DB_NAME, DB_USER, DB_PASSWORD)"
echo "      └── same settings.py detects and uses individual credentials"
echo ""

echo "✅ All checks passed!"
echo ""
echo "🎯 Ready to deploy!"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Commit: ./commit_cleanup.sh"
echo "  3. Push main: git push origin main"
echo "  4. Create production: ./deploy_to_cpanel.sh"
echo "  5. Push production: git push origin production-cpanel"
echo ""
