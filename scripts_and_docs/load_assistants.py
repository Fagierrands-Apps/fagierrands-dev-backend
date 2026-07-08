#!/usr/bin/env python
"""Load verified assistants (riders)"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

assistants = [
    {'username': 'rider1', 'phone': '254720000001', 'name': 'James Mwangi'},
    {'username': 'rider2', 'phone': '254720000002', 'name': 'Peter Kamau'},
    {'username': 'rider3', 'phone': '254720000003', 'name': 'Mary Wanjiru'},
    {'username': 'rider4', 'phone': '254720000004', 'name': 'Kevin Otieno'},
    {'username': 'rider5', 'phone': '254720000005', 'name': 'Grace Akinyi'},
]

created = 0
for a in assistants:
    if not User.objects.filter(phone_number=a['phone']).exists():
        names = a['name'].split()
        User.objects.create_user(
            username=a['username'],
            phone_number=a['phone'],
            email=f"{a['username']}@test.com",
            password='Test@123',
            first_name=names[0],
            last_name=names[-1] if len(names) > 1 else '',
            user_type='assistant',
            is_verified=True
        )
        created += 1
        print(f"✅ Created assistant: {a['username']} ({a['phone']})")
    else:
        print(f"⏭️  Exists: {a['username']}")

print(f"\n✅ Done! Created {created} verified assistants")
