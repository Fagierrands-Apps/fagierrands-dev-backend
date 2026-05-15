from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates an admin superuser'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        
        username = 'admin'
        email = 'admin@fagierrands.com'
        password = 'FagiAdmin2026!'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Admin user "{username}" already exists'))
            # Update password for existing user
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.phone_verified = True
            user.is_verified = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" password updated'))
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                phone_number='+254700000000',
                user_type='ADMIN',
                first_name='Admin',
                last_name='User',
                phone_verified=True,
                is_verified=True
            )
            self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" created successfully'))
