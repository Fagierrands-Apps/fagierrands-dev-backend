#!/bin/bash
# Remove old/unused Python files and other cruft

echo "🧹 Removing old Python files and unused code..."
echo ""

# Remove old debug/test scripts from root
echo "Cleaning root directory..."
rm -f debug_phone_number.py
rm -f verify_ncba.py
rm -f test_*.py 2>/dev/null || true

# Remove old/backup files
echo "Removing backup files..."
rm -f admin_dashboard/views_temp.py
rm -f orders/models_updated.py
rm -f orders/views_updated.py
rm -f orders/serializers_updated.py

# Remove old payment files (using NCBA only now)
echo "Removing old payment integrations..."
rm -f orders/intasend_fallback.py
rm -f orders/mpesa_service.py
rm -f orders/views_payment_mpesa.py
rm -f orders/paypal_payment_admin.py

# Remove old settings file
rm -f fagierrandsbackup/settings_cpanel.py  # We're using settings_production.py

# Remove .env.local and other env files
echo "Cleaning environment files..."
rm -f .env.local
rm -f .env.example 2>/dev/null || true

# Clean test files across the project
echo "Cleaning test files..."
find . -path "./.git" -prune -o -name "test_*.py" -type f -delete 2>/dev/null || true
find . -path "./.git" -prune -o -name "*_test.py" -type f -delete 2>/dev/null || true

# Remove old markdown docs that aren't needed
echo "Cleaning old documentation..."
rm -f AUTH_TEST_RESULTS.md
rm -f FILES_CREATED.txt
rm -f PHONE_NUMBER_ISSUE_FIX.md
rm -f READY_FOR_PHONE_TEST.md
rm -f SYNC_COMPLETE.md
rm -f NCBA_*.md 2>/dev/null || true
rm -f PRICE_*.md 2>/dev/null || true
rm -f RIDER_ASSIGNMENT_*.md 2>/dev/null || true
rm -f DEEP_SCAN_CONFIRMATION.md
rm -f COMPLETE_IMPLEMENTATION_SUMMARY.md
rm -f IMPLEMENTATION_SUMMARY.md
rm -f MAP_CONFIGURATION_ANALYSIS.md
rm -f POSTMAN_COLLECTIONS_READY.md
rm -f QUICK_SWAGGER_TEST.md
rm -f TEST_AUTOCOMPLETE_COORDS.md
rm -f LOCATION_TEST_RESULTS.md
rm -f FLOW_DIAGRAM.md
rm -f API_RESPONSE_EXAMPLES.md
rm -f DELIVERY_SUMMARY.md

# Remove old shell scripts
rm -f test_autocomplete_with_coords.sh

# Remove old Excel/CSV data files
rm -f scripts_and_docs/*.xlsx 2>/dev/null || true
rm -f scripts_and_docs/*.csv 2>/dev/null || true
rm -f scripts_and_docs/collections-reports.xlsx 2>/dev/null || true

# Remove exports folder if it exists
rm -rf exports/ 2>/dev/null || true

# Remove old test image
rm -f test_upload_image.jpg

# Clean the fagierrandsbackup old files
rm -f fagierrandsbackup/celery_app.py 2>/dev/null || true
rm -f fagierrandsbackup/celery_local.py 2>/dev/null || true

echo ""
echo "✅ Python cleanup complete!"
echo ""
echo "🗑️ Removed:"
echo "  - Old debug/test scripts"
echo "  - M-Pesa/IntaSend payment files"
echo "  - Backup Python files (*_temp, *_updated)"
echo "  - Old markdown documentation"
echo "  - Test data files"
echo ""
