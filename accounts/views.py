
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Sum, Count
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, OTPVerification, Profile, AssistantVerification
from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer
from core.utils import generate_otp
from core.sms_service import send_otp, send_password_reset_otp

@swagger_auto_schema(
    method='post',
    operation_id='accounts_register_create',
    tags=['accounts'],
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response('Registration successful', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                'next_step': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ))
    }
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    import logging
    logger = logging.getLogger(__name__)
    
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        otp = generate_otp()
        expires = timezone.now() + timedelta(minutes=10)
        OTPVerification.objects.create(
            phone_number=user.phone_number,
            otp=otp,
            purpose='registration',
            expires_at=expires
        )
        send_otp(user.phone_number, otp)
        return Response({
            'message': 'Registration successful. OTP sent to your phone number.',
            'phone_number': user.phone_number,
            'next_step': 'verify_phone'
        }, status=status.HTTP_201_CREATED)
    
    logger.error(f"Registration validation errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    tags=['accounts'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone_number', 'otp'],
        properties={
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number'),
            'otp': openapi.Schema(type=openapi.TYPE_STRING, description='6-digit OTP code'),
        }
    ),
    responses={
        200: openapi.Response('Phone verified', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'access': openapi.Schema(type=openapi.TYPE_STRING),
                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                'user': openapi.Schema(type=openapi.TYPE_OBJECT),
            }
        ))
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_phone(request):
    from core.utils import normalize_phone_number
    
    phone = normalize_phone_number(request.data.get('phone_number'))
    otp = request.data.get('otp')
    
    otp_obj = OTPVerification.objects.filter(
        phone_number=phone, otp=otp, is_used=False,
        expires_at__gt=timezone.now()
    ).first()
    
    if not otp_obj:
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(phone_number=phone).first()
    if user:
        user.is_verified = True
        user.save()
        otp_obj.is_used = True
        otp_obj.save()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Phone verified successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })
    
    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='post',
    tags=['accounts'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone_number'],
        properties={
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number'),
        }
    ),
    responses={200: openapi.Response('OTP sent')}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    from core.utils import normalize_phone_number
    
    phone = normalize_phone_number(request.data.get('phone_number'))
    
    # SECURITY: Only allow resend for registered but unverified users
    user = User.objects.filter(phone_number=phone, is_verified=False).first()
    
    if not user:
        return Response({
            'error': 'Phone number not found or already verified. Please register first.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate new OTP
    otp = generate_otp()
    expires = timezone.now() + timedelta(minutes=10)
    
    # Invalidate old OTPs for this phone
    OTPVerification.objects.filter(phone_number=phone, purpose='registration').update(is_used=True)
    
    # Create new OTP
    OTPVerification.objects.create(
        phone_number=phone, 
        otp=otp,
        purpose='registration', 
        expires_at=expires
    )
    
    # Send OTP
    send_otp(phone, otp)
    
    return Response({
        'message': 'OTP sent successfully',
        'phone_number': phone
    })

@swagger_auto_schema(
    method='post',
    tags=['accounts'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone_number', 'password'],
        properties={
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number (0712345678 or 254712345678)'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        }
    ),
    responses={
        200: openapi.Response('Login successful', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'user_type': openapi.Schema(type=openapi.TYPE_STRING),
                'is_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            }
        ))
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    from core.utils import normalize_phone_number
    
    phone = normalize_phone_number(request.data.get('phone_number'))
    password = request.data.get('password')
    
    user = User.objects.filter(phone_number=phone).first()
    if user and user.check_password(password):
        if not user.is_verified:
            return Response({'error': 'Phone not verified'}, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'email': user.email,
            'user_type': user.user_type,
            'is_verified': user.is_verified,
            'email_verified': user.email_verified
        })
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(
    method='post',
    tags=['accounts'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['refresh'],
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
        }
    ),
    responses={200: openapi.Response('Logged out')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Successfully logged out.'})
    except Exception:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    tags=['accounts'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone_number'],
        properties={
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: openapi.Response('OTP sent')}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    from core.utils import normalize_phone_number
    
    phone = normalize_phone_number(request.data.get('phone_number'))
    user = User.objects.filter(phone_number=phone).first()
    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    otp = generate_otp()
    expires = timezone.now() + timedelta(minutes=10)
    OTPVerification.objects.create(
        phone_number=phone, otp=otp,
        purpose='password_reset', expires_at=expires
    )
    send_password_reset_otp(phone, otp)
    return Response({
        'message': 'OTP sent to your phone number',
        'phone_number': phone
    })

@swagger_auto_schema(
    method='post',
    tags=['accounts'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['phone_number', 'otp', 'new_password'],
        properties={
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
            'otp': openapi.Schema(type=openapi.TYPE_STRING),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: openapi.Response('Password reset successful')}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset(request):
    from core.utils import normalize_phone_number
    
    phone = normalize_phone_number(request.data.get('phone_number'))
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')
    
    otp_obj = OTPVerification.objects.filter(
        phone_number=phone, otp=otp, is_used=False,
        purpose='password_reset', expires_at__gt=timezone.now()
    ).first()
    
    if not otp_obj:
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(phone_number=phone).first()
    if user:
        user.set_password(new_password)
        user.save()
        otp_obj.is_used = True
        otp_obj.save()
        return Response({'message': 'Password reset successful. Please login with your new password.'})
    
    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='post',
    tags=['accounts'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['old_password', 'new_password'],
        properties={
            'old_password': openapi.Schema(type=openapi.TYPE_STRING),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: openapi.Response('Password changed')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    user = request.user
    if not user.check_password(old_password):
        return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password changed successfully'})

@swagger_auto_schema(method='get', tags=['accounts'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request):
    """Get current user details"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@swagger_auto_schema(method='get', tags=['accounts'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assistant_verification_status(request):
    """Check rider verification status"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Not a rider'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        verification = request.user.verification
        return Response({
            'status': verification.status,
            'submitted_at': verification.created_at,
            'admin_notes': verification.admin_notes
        })
    except:
        return Response({
            'status': 'not_submitted',
            'message': 'No verification submitted yet'
        })

@swagger_auto_schema(
    method='post',
    tags=['accounts'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id_number', 'id_photo', 'vehicle_type', 'vehicle_registration', 'vehicle_photo', 'drivers_license'],
        properties={
            'id_number': openapi.Schema(type=openapi.TYPE_STRING),
            'id_photo': openapi.Schema(type=openapi.TYPE_STRING, description='URL to ID photo'),
            'vehicle_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['motorcycle', 'bicycle', 'car', 'van']),
            'vehicle_registration': openapi.Schema(type=openapi.TYPE_STRING),
            'vehicle_photo': openapi.Schema(type=openapi.TYPE_STRING, description='URL to vehicle photo'),
            'drivers_license': openapi.Schema(type=openapi.TYPE_STRING, description='URL to license photo'),
        }
    ),
    responses={201: openapi.Response('Verification submitted')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_verification(request):
    """Submit rider verification"""
    from accounts.models import AssistantVerification
    
    if request.user.user_type != 'assistant':
        return Response({'error': 'Only riders can submit verification'}, status=status.HTTP_403_FORBIDDEN)
    
    # Check if already verified or pending
    existing = AssistantVerification.objects.filter(assistant=request.user).first()
    if existing and existing.status in ['approved', 'pending']:
        return Response({'error': f'Verification already {existing.status}'}, status=status.HTTP_400_BAD_REQUEST)
    
    verification = AssistantVerification.objects.create(
        assistant=request.user,
        id_number=request.data.get('id_number'),
        id_photo=request.data.get('id_photo'),
        vehicle_type=request.data.get('vehicle_type'),
        vehicle_registration=request.data.get('vehicle_registration'),
        vehicle_photo=request.data.get('vehicle_photo'),
        drivers_license=request.data.get('drivers_license'),
        status='pending'
    )
    
    return Response({
        'message': 'Verification submitted successfully',
        'verification_id': verification.id,
        'status': 'pending'
    }, status=status.HTTP_201_CREATED)

@swagger_auto_schema(method='get', tags=['accounts'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assistant_dashboard_stats(request):
    """Get rider dashboard stats"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Not a rider'}, status=status.HTTP_403_FORBIDDEN)
    
    from orders.models import Order
    from django.db.models import Sum, Count
    
    stats = {
        'total_deliveries': Order.objects.filter(assistant=request.user).count(),
        'completed': Order.objects.filter(assistant=request.user, status='delivered').count(),
        'active': Order.objects.filter(assistant=request.user, status__in=['assigned', 'picked', 'in_transit']).count(),
        'total_earnings': Order.objects.filter(assistant=request.user, status='delivered').aggregate(
            total=Sum('total_price'))['total'] or 0,
        'rating': float(request.user.profile.rating),
        'total_ratings': request.user.profile.total_ratings,
    }
    
    return Response(stats)

@swagger_auto_schema(
    methods=['get'],
    tags=['accounts'],
    responses={200: openapi.Response('Availability status')}
)
@swagger_auto_schema(
    methods=['patch'],
    tags=['accounts'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'is_available': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Online/Offline status'),
        }
    ),
    responses={200: openapi.Response('Availability updated')}
)
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def assistant_availability(request):
    """Get/Set rider availability (online/offline)"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Not a rider'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        return Response({
            'is_available': request.user.is_active,
            'user_id': request.user.id
        })
    
    elif request.method == 'PATCH':
        is_available = request.data.get('is_available')
        request.user.is_active = is_available
        request.user.save()
        return Response({
            'message': 'Availability updated',
            'is_available': is_available
        })

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(tags=['accounts'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['accounts'])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['accounts'])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    def get_object(self):
        return self.request.user.profile



# JWT Token Views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

class CustomTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(tags=['accounts'], operation_id='accounts_token_create')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(tags=['accounts'], operation_id='accounts_token_refresh_create')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# Admin endpoints
@swagger_auto_schema(
    method='get',
    tags=['accounts'],
    operation_id='accounts_admin_verifications_list',
    responses={200: 'List of verification requests'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_verifications_list(request):
    if request.user.user_type != 'admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    from accounts.models import AssistantVerification
    verifications = AssistantVerification.objects.all().select_related('assistant')
    
    data = [{
        'id': v.id,
        'assistant_id': v.assistant.id,
        'assistant_name': f"{v.assistant.first_name} {v.assistant.last_name}",
        'assistant_phone': v.assistant.phone_number,
        'status': v.status,
        'vehicle_type': v.vehicle_type,
        'submitted_at': v.created_at,
        'updated_at': v.updated_at,
    } for v in verifications]
    
    return Response(data)

@swagger_auto_schema(
    method='get',
    tags=['accounts'],
    operation_id='accounts_admin_verifications_read',
    responses={200: 'Verification detail'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_verification_detail(request, id):
    if request.user.user_type != 'admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    from accounts.models import AssistantVerification
    try:
        v = AssistantVerification.objects.select_related('assistant').get(id=id)
    except AssistantVerification.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'id': v.id,
        'assistant': {
            'id': v.assistant.id,
            'name': f"{v.assistant.first_name} {v.assistant.last_name}",
            'phone': v.assistant.phone_number,
            'email': v.assistant.email,
        },
        'id_number': v.id_number,
        'id_photo': v.id_photo,
        'vehicle_type': v.vehicle_type,
        'vehicle_registration': v.vehicle_registration,
        'vehicle_photo': v.vehicle_photo,
        'drivers_license': v.drivers_license,
        'status': v.status,
        'admin_notes': v.admin_notes,
        'submitted_at': v.created_at,
        'updated_at': v.updated_at,
    })

@swagger_auto_schema(
    method='patch',
    tags=['accounts'],
    operation_id='accounts_admin_verifications_update_partial_update',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['pending', 'approved', 'rejected']),
            'admin_notes': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: 'Verification updated'}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def admin_verification_update(request, id):
    if request.user.user_type != 'admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    from accounts.models import AssistantVerification
    try:
        v = AssistantVerification.objects.get(id=id)
    except AssistantVerification.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    status_val = request.data.get('status')
    if status_val:
        v.status = status_val
    if 'admin_notes' in request.data:
        v.admin_notes = request.data['admin_notes']
    v.save()
    
    return Response({'message': 'Verification updated', 'status': v.status})

@swagger_auto_schema(
    method='get',
    tags=['accounts'],
    operation_id='accounts_assistants_stats_list',
    responses={200: 'Assistant statistics'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assistants_stats(request):
    if request.user.user_type not in ['admin', 'handler']:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    from accounts.models import AssistantVerification
    stats = {
        'total_assistants': User.objects.filter(user_type='assistant').count(),
        'verified_assistants': AssistantVerification.objects.filter(status='approved').count(),
        'pending_verifications': AssistantVerification.objects.filter(status='pending').count(),
        'available_assistants': User.objects.filter(user_type='assistant', is_active=True).count(),
    }
    return Response(stats)

@swagger_auto_schema(
    method='get',
    tags=['accounts'],
    operation_id='accounts_user_list_list',
    manual_parameters=[
        openapi.Parameter('user_type', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Filter by user type'),
    ],
    responses={200: 'List of users'}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    if request.user.user_type not in ['admin', 'handler']:
        return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
    
    users = User.objects.all()
    user_type = request.query_params.get('user_type')
    if user_type:
        users = users.filter(user_type=user_type)
    
    data = [{
        'id': u.id,
        'phone_number': u.phone_number,
        'email': u.email,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'user_type': u.user_type,
        'is_verified': u.is_verified,
        'is_active': u.is_active,
    } for u in users]
    
    return Response(data)

# Admin-only endpoint to change user types
@swagger_auto_schema(
    method='patch',
    tags=['accounts'],
    operation_id='accounts_admin_change_user_type',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_type'],
        properties={
            'user_type': openapi.Schema(
                type=openapi.TYPE_STRING, 
                enum=['user', 'assistant', 'handler', 'admin'],
                description='New user type'
            ),
        }
    ),
    responses={200: openapi.Response('User type updated')}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def admin_change_user_type(request, user_id):
    if request.user.user_type != 'admin':
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    new_type = request.data.get('user_type')
    if new_type not in ['user', 'assistant', 'handler', 'admin', 'vendor']:
        return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
    
    user.user_type = new_type
    user.save()
    
    return Response({
        'message': f'User type changed to {new_type}',
        'user': UserSerializer(user).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_assistants(request):
    """List all verified assistants/riders"""
    assistants = User.objects.filter(
        user_type='assistant',
        assistant_verification__status='approved'
    ).select_related('assistant_verification')
    
    data = []
    for assistant in assistants:
        data.append({
            'id': assistant.id,
            'username': assistant.username,
            'first_name': assistant.first_name,
            'last_name': assistant.last_name,
            'phone_number': assistant.phone_number,
            'email': assistant.email,
            'is_verified': assistant.is_verified,
            'vehicle_type': assistant.assistant_verification.vehicle_type if hasattr(assistant, 'assistant_verification') else None,
            'vehicle_registration': assistant.assistant_verification.vehicle_registration if hasattr(assistant, 'assistant_verification') else None,
        })
    
    return Response(data)
