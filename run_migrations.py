import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrandsbackup.settings')
django.setup()

from django.core.management import call_command

call_command('migrate')
call_command('collectstatic', '--noinput')
print("Migrations completed!")
