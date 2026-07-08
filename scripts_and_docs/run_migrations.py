#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')
django.setup()

from django.core.management import call_command

print("Running migrations...")
call_command('migrate')
print("Migrations completed!")
