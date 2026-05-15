from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_admin_user(request):
    """Emergency endpoint to create admin user - REMOVE AFTER USE"""
    User = get_user_model()
    
    try:
        if User.objects.filter(username='admin').exists():
            user = User.objects.get(username='admin')
            user.set_password('FagiAdmin2026!')
            user.is_superuser = True
            user.is_staff = True
            user.phone_verified = True
            user.is_verified = True
            user.save()
            return JsonResponse({'status': 'success', 'message': 'Admin password updated'})
        else:
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@fagierrands.com',
                password='FagiAdmin2026!',
                phone_number='+254700000000',
                user_type='ADMIN',
                first_name='Admin',
                last_name='User'
            )
            admin.phone_verified = True
            admin.is_verified = True
            admin.save()
            return JsonResponse({'status': 'success', 'message': 'Admin user created'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
