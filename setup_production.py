#!/usr/bin/env python
"""
Production Setup Script for cPanel
Run this after uploading/extracting files to cPanel
"""
import os
import sys
import subprocess

def run_command(cmd, description):
    """Run shell command and report status"""
    print(f"\n⏳ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def main():
    print("🚀 FagiErrands Production Setup\n")
    
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    print(f"📁 Working directory: {base_dir}\n")
    
    # 1. Create missing directories
    print("📁 Creating directories...")
    dirs = ['static', 'staticfiles', 'media', 'logs', 'tmp']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✅ {d}/")
    
    # 2. Collect static files
    run_command('python manage.py collectstatic --noinput', 'Collecting static files')
    
    # 3. Run migrations
    run_command('python manage.py migrate --noinput', 'Running database migrations')
    
    # 4. Check system
    run_command('python manage.py check', 'System check')
    
    # 5. Restart app
    restart_file = os.path.join(base_dir, 'tmp', 'restart.txt')
    try:
        open(restart_file, 'a').close()
        os.utime(restart_file, None)
        print("\n✅ App restart triggered")
    except:
        print("\n⚠️  Manually restart app in cPanel")
    
    print("\n" + "="*50)
    print("✅ Production setup complete!")
    print("="*50)
    print("\n📝 Next steps:")
    print("1. Check /admin/ page")
    print("2. Check /swagger/ docs")
    print("3. Test API endpoints\n")

if __name__ == '__main__':
    main()
