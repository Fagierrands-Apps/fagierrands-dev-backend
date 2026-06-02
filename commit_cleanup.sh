#!/bin/bash
# Commit all cleanup changes

echo "📝 Committing cleanup changes..."
echo ""

# Stage all deletions
git add -A

# Show summary
echo "Changes to be committed:"
git status --short | wc -l
echo "files changed"
echo ""

# Commit
git commit -m "Clean up 114 old/unused files

- Remove old Render/Vercel deployment configs
- Remove M-Pesa/IntaSend payment files (using NCBA only)
- Remove outdated documentation (60+ files)
- Remove backup Python files (_temp, _updated)
- Remove old test scripts and data files
- Add new cPanel deployment setup
- Add settings_production.py with hardcoded credentials
- Total: 114 files deleted, 6 files added"

echo ""
echo "✅ Changes committed!"
echo ""
echo "Next steps:"
echo "  1. Push to main: git push origin main"
echo "  2. Create production branch: ./deploy_to_cpanel.sh"
echo "  3. Push production: git push origin production-cpanel"
echo ""
