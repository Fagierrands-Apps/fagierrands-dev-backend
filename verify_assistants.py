#!/usr/bin/env python
"""Verify all assistant/riders"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import AssistantVerification

User = get_user_model()

# Get all assistants
assistants = User.objects.filter(user_type='assistant')

if not assistants.exists():
    print("❌ No assistants found! Run load_assistants.py first")
    exit(1)

verified = 0
for assistant in assistants:
    # Create or update verification
    verification, created = AssistantVerification.objects.get_or_create(
        user=assistant,
        defaults={
            'vehicle_type': 'motorcycle',
            'vehicle_registration': f'KAA-{assistant.id:03d}X',
            'drivers_license': f'DL{assistant.id:05d}',
            'id_number': f'{30000000 + assistant.id}',
            'status': 'approved',
            'verified_at': datetime.now()
        }
    )
    
    if not created:
        # Update existing to approved
        verification.status = 'approved'
        verification.verified_at = datetime.now()
        verification.save()
    
    verified += 1
    print(f"✅ Verified: {assistant.username}")

print(f"\n✅ Verified {verified} assistants/riders")
print("They will now appear in Assistants tab!")
