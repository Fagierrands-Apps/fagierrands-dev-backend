#!/usr/bin/env python
"""Load 10 test users"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagierrands.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

users = [
    {'username': 'customer1', 'phone': '254711111111', 'type': 'customer', 'name': 'John Doe'},
    {'username': 'customer2', 'phone': '254722222222', 'type': 'customer', 'name': 'Jane Smith'},
    {'username': 'customer3', 'phone': '254733333333', 'type': 'customer', 'name': 'Bob Wilson'},
    {'username': 'customer4', 'phone': '254744444444', 'type': 'customer', 'name': 'Alice Brown'},
    {'username': 'customer5', 'phone': '254755555555', 'type': 'customer', 'name': 'Charlie Davis'},
    {'username': 'handler1', 'phone': '254766666666', 'type': 'handler', 'name': 'Mike Handler'},
    {'username': 'handler2', 'phone': '254777777777', 'type': 'handler', 'name': 'Sarah Handler'},
    {'username': 'handler3', 'phone': '254788888888', 'type': 'handler', 'name': 'Tom Handler'},
    {'username': 'handler4', 'phone': '254799999999', 'type': 'handler', 'name': 'Lisa Handler'},
    {'username': 'handler5', 'phone': '254710000000', 'type': 'handler', 'name': 'David Handler'},
]

created = 0
for u in users:
    if not User.objects.filter(phone_number=u['phone']).exists():
        names = u['name'].split()
        User.objects.create_user(
            username=u['username'],
            phone_number=u['phone'],
            email=f"{u['username']}@test.com",
            password='Test@123',
            first_name=names[0],
            last_name=names[-1] if len(names) > 1 else '',
            user_type=u['type'],
            is_verified=True
        )
        created += 1
        print(f"✅ Created {u['type']}: {u['username']} ({u['phone']})")
    else:
        print(f"⏭️  Exists: {u['username']}")

print(f"\n✅ Done! Created {created} new users, {10-created} already existed")
