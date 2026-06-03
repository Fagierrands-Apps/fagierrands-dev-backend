#!/bin/bash
echo "========================================"
echo "DEPLOYMENT VERIFICATION"
echo "========================================"
echo ""

echo "Checking critical files..."
echo ""

# Check passenger_wsgi.py
if grep -q "OPENBLAS_NUM_THREADS" passenger_wsgi.py; then
    echo "✅ passenger_wsgi.py - OpenBLAS limit configured"
else
    echo "❌ passenger_wsgi.py - OpenBLAS limit MISSING"
fi

# Check requirements.txt size
REQ_LINES=$(wc -l < requirements.txt)
if [ "$REQ_LINES" -lt 30 ]; then
    echo "✅ requirements.txt - Simplified ($REQ_LINES packages)"
else
    echo "⚠️  requirements.txt - Still large ($REQ_LINES lines)"
fi

# Check .env.cpanel
if [ -f ".env.cpanel" ]; then
    echo "✅ .env.cpanel - Present"
    if grep -q "DB_NAME=distinc3_fagierrandsNew" .env.cpanel; then
        echo "✅ .env.cpanel - Database credentials configured"
    fi
else
    echo "❌ .env.cpanel - MISSING"
fi

# Check runtime.txt
if grep -q "3.12" runtime.txt; then
    echo "✅ runtime.txt - Python 3.12.x"
else
    echo "⚠️  runtime.txt - Old Python version"
fi

# Check restart file
if [ -f "tmp/restart.txt" ]; then
    echo "✅ tmp/restart.txt - Present"
else
    echo "❌ tmp/restart.txt - MISSING"
fi

echo ""
echo "========================================"
echo "DEPLOYMENT FILES READY"
echo "========================================"
echo ""
echo "Upload these files to cPanel:"
echo "  - passenger_wsgi.py"
echo "  - requirements.txt"
echo "  - runtime.txt"
echo "  - .env.cpanel (rename to .env)"
echo "  - All Django app folders"
echo "  - fagierrandsbackup/ folder"
echo "  - tmp/ folder"
echo ""
echo "Then run in cPanel terminal:"
echo "  pip install -r requirements.txt"
echo "  touch tmp/restart.txt"
echo ""
