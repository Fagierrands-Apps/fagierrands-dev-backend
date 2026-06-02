#!/bin/bash
# Three-branch deployment strategy

echo "🌳 Setting up 3-Branch Strategy..."
echo ""
echo "Branch Structure:"
echo "  main         → Development/Testing on Render"
echo "  production   → Stable code (merge from main after testing)"
echo "  production-cpanel → Production with cPanel .env file"
echo ""

# Ensure we're on main
git checkout main

# Check if production branch exists
if git show-ref --verify --quiet refs/heads/production; then
    echo "✓ production branch already exists"
else
    echo "Creating production branch from main..."
    git checkout -b production
    git checkout main
    echo "✓ production branch created"
fi

# Check if production-cpanel exists
if git show-ref --verify --quiet refs/heads/production-cpanel; then
    echo "✓ production-cpanel branch already exists"
else
    echo "Creating production-cpanel branch from production..."
    git checkout production
    git checkout -b production-cpanel
    
    # Copy cPanel .env
    cp .env.cpanel .env
    git add .env
    git commit -m "Add cPanel .env for production deployment"
    
    git checkout main
    echo "✓ production-cpanel branch created"
fi

echo ""
echo "✅ Branch structure ready!"
echo ""
echo "📋 Workflow:"
echo ""
echo "1. Development & Testing (main → Render):"
echo "   git checkout main"
echo "   # Make changes, test on Render"
echo "   git push origin main"
echo ""
echo "2. After Successful Testing (main → production):"
echo "   git checkout production"
echo "   git merge main"
echo "   git push origin production"
echo ""
echo "3. Deploy to cPanel (production → production-cpanel):"
echo "   git checkout production-cpanel"
echo "   git merge production"
echo "   git push origin production-cpanel"
echo "   # On cPanel: git pull"
echo ""
echo "Current branch: $(git branch --show-current)"
echo ""
