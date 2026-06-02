#!/bin/bash
# Clean up old deployment files and unused documentation

echo "🧹 Cleaning up old deployment files..."
echo ""

# Root level old deployment files
echo "Removing old deployment configs..."
rm -f build.sh
rm -f build_file.sh
rm -f Procfile
rm -f render.yaml
rm -f render_env
rm -f render-start.sh
rm -f start.sh
rm -f setup_local.sh

# Old deployment guides (keeping only the new cPanel ones)
echo "Removing old deployment documentation..."
rm -f DEPLOYMENT_CHECKLIST.md
rm -f CPANEL_DEPLOYMENT_GUIDE.md  # Replaced by CPANEL_DEPLOY_README.md

# scripts_and_docs cleanup
echo "Cleaning scripts_and_docs folder..."
cd scripts_and_docs

# Remove Render-specific files
rm -f RENDER_DEPLOYMENT.md
rm -f RENDER_DEPLOYMENT_CHECKLIST.md
rm -f RENDER_DEPLOYMENT_FIX.md
rm -f RENDER_ENV_CHECKLIST.sh
rm -f RENDER_ENV_SETUP.txt

# Remove Vercel files
rm -f vercel*.json
rm -f build_vercel.sh

# Remove old deployment docs
rm -f deploy_fix.md
rm -f DEPLOYMENT_CHECKLIST.md
rm -f MIGRATION_FIX_GUIDE.md

# Remove old payment/webhook guides (IntaSend not used)
rm -f OFFICIAL_INTASEND_WEBHOOK_GUIDE.md
rm -f WEBHOOK_CONFIGURATION_GUIDE.md
rm -f WEBHOOK_TESTING_GUIDE.md
rm -f POSTMAN_WEBHOOK_TESTS.md
rm -f FINAL_INTASEND_INTEGRATION_SUMMARY.md
rm -f INTASEND_INTEGRATION_AUDIT.md
rm -f INTASEND_INTEGRATION_AUDIT_REPORT.md

# Remove old payment fix docs
rm -f PAYMENT_FIX_README.md
rm -f PAYMENT_ISSUE_SOLUTION.md
rm -f PAYMENT_ISSUE_SOLUTION_SUMMARY.md
rm -f PAYMENT_STATUS_CLEANUP_REPORT.md
rm -f REAL_PAYMENT_TEST_GUIDE.md

# Remove M-Pesa files (using NCBA now)
rm -f MPESA_*.md
rm -f mpesa_*.md

# Remove MediaFire docs (not used)
rm -f MEDIAFIRE_*.md

# Remove old Swagger/testing docs
rm -f SWAGGER_FIX_REPORT.md
rm -f TESTING_SETUP_COMPLETE.md
rm -f VERIFICATION_RESULTS.md

cd ..

# reports folder cleanup
echo "Cleaning reports folder..."
cd reports

rm -f deploy_fix.md
rm -f DEPLOYMENT_CHECKLIST.md
rm -f OFFICIAL_INTASEND_WEBHOOK_GUIDE.md
rm -f PAYMENT_FIX_README.md
rm -f PAYMENT_ISSUE_SOLUTION.md
rm -f PAYMENT_ISSUE_SOLUTION_SUMMARY.md
rm -f PAYMENT_STATUS_CLEANUP_REPORT.md
rm -f POSTMAN_WEBHOOK_TESTS.md
rm -f REAL_PAYMENT_TEST_GUIDE.md
rm -f WEBHOOK_CONFIGURATION_GUIDE.md
rm -f WEBHOOK_TESTING_GUIDE.md
rm -f FINAL_INTASEND_INTEGRATION_SUMMARY.md
rm -f INTASEND_INTEGRATION_AUDIT_REPORT.md
rm -f INTASEND_INTEGRATION_AUDIT.md

cd ..

# jsons folder cleanup
echo "Cleaning jsons folder..."
cd jsons
rm -f vercel*.json
rm -f IntaSend*.json
cd ..

# Remove old setup scripts
echo "Removing old test/setup scripts..."
rm -f setup_cpanel_production.sh  # Replaced by deploy_to_cpanel.sh
rm -f test_*.py 2>/dev/null || true

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📦 Kept essential files:"
echo "  - deploy_to_cpanel.sh (NEW deployment script)"
echo "  - CPANEL_DEPLOY_README.md (NEW guide)"
echo "  - passenger_wsgi.py"
echo "  - settings_production.py"
echo ""
echo "🗑️ Removed:"
echo "  - Old Render deployment files"
echo "  - Old Vercel configs"
echo "  - IntaSend/M-Pesa old docs"
echo "  - Old payment fix guides"
echo "  - Duplicate deployment checklists"
echo ""
