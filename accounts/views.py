
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Sum, Count
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, OTPVerification, Profile, AssistantVerification
from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer
from .login_security import LoginSecurityManager, get_client_ip
from uuid import uuid4
from core.utils import generate_otp, normalize_phone_number
from core.sms_service import send_otp, send_password_reset_otp
from fagierrands.throttles import (
    RegisterThrottle, OTPVerificationThrottle, ResendOTPThrottle,
    PasswordResetThrottle, LoginThrottle, TokenRefreshThrottle
)

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
@throttle_classes([RegisterThrottle])
def register(request):
    import logging
    logger = logging.getLogger(__name__)
    
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        otp_plain, otp_hash = generate_otp(length=4)  # ← 4-digit OTP for app compatibility
        expires = timezone.now() + timedelta(minutes=10)
        
        # Clean up expired OTPs to prevent DB bloat
        OTPVerification.objects.filter(expires_at__lt=timezone.now()).delete()
        
        OTPVerification.objects.create(
            phone_number=user.phone_number,
            otp_hash=otp_hash,  # Store hash, not plaintext
            purpose='registration',
            expires_at=expires
        )
        send_otp(user.phone_number, otp_plain)  # Send plaintext to user
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
@throttle_classes([OTPVerificationThrottle])
def verify_phone(request):
    phone = normalize_phone_number(request.data.get('phone_number'))
    otp = request.data.get('otp', '').strip()
    
    # Check if account is locked out
    lockout_key = f"otp_lockout_{phone}"
    if cache.get(lockout_key):
        return Response({
            'error': 'Too many failed attempts. Please try again after 15 minutes.'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # NEW: Use verify_otp method with timing attack protection
    otp_obj = OTPVerification.objects.filter(
        phone_number=phone, 
        is_used=False,
        purpose='registration'
    ).latest('created_at')
    
    if not otp_obj or not otp_obj.verify_otp(otp):
        # Track failed attempt
        failure_key = f"otp_failures_{phone}"
        failures = cache.get(failure_key, 0) + 1
        cache.set(failure_key, failures, 3600)  # 1 hour window
        
        # Update attempt count in DB
        if otp_obj:
            otp_obj.attempt_count += 1
            otp_obj.last_attempt_at = timezone.now()
            otp_obj.save(update_fields=['attempt_count', 'last_attempt_at'])
        
        # Generic error message (no enumeration)
        if failures >= 5:
            # Lockout for 15 minutes
            cache.set(lockout_key, True, 900)
            return Response({
                'error': 'Too many failed attempts. Please try again after 15 minutes.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        return Response({
            'error': 'Invalid verification code. Please try again.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(phone_number=phone).first()
    if user:
        user.is_verified = True
        user.save()
        otp_obj.is_used = True
        otp_obj.save(update_fields=['is_used'])
        
        # Clear failure tracking on success
        cache.delete(f"otp_failures_{phone}")
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Phone verified successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })
    
    # Don't reveal if user exists - return generic error
    return Response({
        'error': 'Invalid verification code. Please try again.'
    }, status=status.HTTP_400_BAD_REQUEST)

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
@throttle_classes([ResendOTPThrottle])
def resend_otp(request):
    phone = normalize_phone_number(request.data.get('phone_number'))
    
    # SECURITY: Only allow resend for registered but unverified users
    user = User.objects.filter(phone_number=phone, is_verified=False).first()
    
    if not user:
        # Don't reveal if phone exists or is already verified
        return Response({
            'message': 'If this number is registered and unverified, OTP will be resent.'
        }, status=status.HTTP_200_OK)
    
    # Generate new OTP
    otp_plain, otp_hash = generate_otp(length=4)  # ← 4-digit OTP for app compatibility
    expires = timezone.now() + timedelta(minutes=10)
    
    # Invalidate old OTPs for this phone
    OTPVerification.objects.filter(phone_number=phone, purpose='registration').update(is_used=True)
    
    # Create new OTP
    OTPVerification.objects.create(
        phone_number=phone, 
        otp_hash=otp_hash,  # ← NEW: Store hash
        purpose='registration', 
        expires_at=expires
    )
    
    # Send OTP
    send_otp(phone, otp_plain)
    
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
@throttle_classes([LoginThrottle])
def login(request):
    """
    User login with password.
    Now includes:
    - Failed attempt tracking and lockout
    - Suspicious login detection
    - Concurrent session limiting
    - Phone verification requirement
    """
    import logging
    logger = logging.getLogger(__name__)
    
    phone = normalize_phone_number(request.data.get('phone_number'))
    password = request.data.get('password')
    
    # Get client IP for security tracking
    client_ip = get_client_ip(request)
    
    user = User.objects.filter(phone_number=phone).first()
    
    # Check if login is allowed (not locked out)
    allowed, reason = LoginSecurityManager.check_login_allowed(user, client_ip)
    if not allowed:
        return Response({'error': reason}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # Verify password
    if user and user.check_password(password):
        # Check phone verification
        if not user.is_verified:
            return Response(
                {'error': 'Phone not verified. Please verify your phone number first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Record successful login
        session_id = str(uuid4())
        LoginSecurityManager.record_successful_login(user, session_id, client_ip)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"Successful login for user {user.id} ({user.phone_number}) from IP {client_ip}")
        
        return Response({
            'message': 'Login successful',
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'email': user.email,
            'user_type': user.user_type,
            'is_verified': user.is_verified,
            'email_verified': user.email_verified,
            'session_id': session_id
        })
    else:
        # Record failed login attempt
        if user:
            error_msg = LoginSecurityManager.record_failed_login(user, client_ip, "Invalid password")
            logger.warning(f"Failed login attempt for user {user.id if user else 'unknown'} from IP {client_ip}")
        
        # Return generic error (don't distinguish between invalid user vs password)
        return Response(
            {'error': 'Invalid credentials. Please check phone number and password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

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
    """
    Logout user and cleanup session/token tracking.
    """
    try:
        refresh_token = request.data.get('refresh')
        session_id = request.data.get('session_id')
        
        # Blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        # Clean up session tracking if session_id provided
        if session_id:
            LoginSecurityManager.logout(request.user.id, session_id)
        
        return Response({'message': 'Successfully logged out.'})
    except Exception as e:
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
@throttle_classes([PasswordResetThrottle])
def password_reset_request(request):
    phone = normalize_phone_number(request.data.get('phone_number'))
    user = User.objects.filter(phone_number=phone).first()
    if not user:
        # Don't reveal if phone exists or not
        return Response({'message': 'If this number is registered, an OTP will be sent.'})
    
    otp_plain, otp_hash = generate_otp(length=4)  # ← 4-digit OTP for app compatibility
    expires = timezone.now() + timedelta(minutes=10)
    OTPVerification.objects.create(
        phone_number=phone, 
        otp_hash=otp_hash,  # Store hash
        purpose='password_reset', 
        expires_at=expires
    )
    send_password_reset_otp(phone, otp_plain)
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
@throttle_classes([OTPVerificationThrottle])
def password_reset(request):
    phone = normalize_phone_number(request.data.get('phone_number'))
    otp = request.data.get('otp', '').strip()
    new_password = request.data.get('new_password')
    
    # Check lockout
    lockout_key = f"otp_lockout_{phone}"
    if cache.get(lockout_key):
        return Response({
            'error': 'Too many failed attempts. Please try again after 15 minutes.'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # NEW: Use verify_otp method with timing attack protection
    otp_obj = OTPVerification.objects.filter(
        phone_number=phone, 
        is_used=False,
        purpose='password_reset'
    ).latest('created_at')
    
    if not otp_obj or not otp_obj.verify_otp(otp):
        # Track failure
        failure_key = f"otp_failures_{phone}"
        failures = cache.get(failure_key, 0) + 1
        cache.set(failure_key, failures, 3600)
        
        # Update attempt count in DB
        if otp_obj:
            otp_obj.attempt_count += 1
            otp_obj.last_attempt_at = timezone.now()
            otp_obj.save(update_fields=['attempt_count', 'last_attempt_at'])
        
        if failures >= 5:
            cache.set(lockout_key, True, 900)
            return Response({
                'error': 'Too many failed attempts. Please try again after 15 minutes.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.filter(phone_number=phone).first()
    if user:
        user.set_password(new_password)
        user.save()
        otp_obj.is_used = True
        otp_obj.save(update_fields=['is_used'])
        cache.delete(f"otp_failures_{phone}")
        return Response({'message': 'Password reset successful. Please login with your new password.'})
    
    # Don't reveal if user exists - return generic success message
    return Response({
        'message': 'If this number is registered, password has been reset. Please login with your new password.'
    }, status=status.HTTP_200_OK)

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
@permission_classes([IsAuthenticated, IsPhoneVerified])
def user_detail(request):
    """Get current user details - requires phone verification"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@swagger_auto_schema(method='get', tags=['accounts'])
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPhoneVerified])
def assistant_verification_status(request):
    """Check rider verification status - requires phone verification"""
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
@permission_classes([IsAuthenticated, IsPhoneVerified])
def submit_verification(request):
    """Submit rider verification - requires phone verification"""
    from accounts.models import AssistantVerification
    
    if request.user.user_type != 'assistant':
        return Response({'error': 'Only riders can submit verification'}, status=status.HTTP_403_FORBIDDEN)
    
    # Check if already verified or pending
    existing = AssistantVerification.objects.filter(user=request.user).first()
    if existing and existing.status in ['approved', 'pending']:
        return Response({'error': f'Verification already {existing.status}'}, status=status.HTTP_400_BAD_REQUEST)
    
    verification = AssistantVerification.objects.create(
        user=request.user,
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
@permission_classes([IsAuthenticated, IsPhoneVerified])
def assistant_dashboard_stats(request):
    """Get rider dashboard stats - requires phone verification"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Not a rider'}, status=status.HTTP_403_FORBIDDEN)
    
    from orders.models import Order
    from django.db.models import Sum, Count
    
    stats = {
        'total_deliveries': Order.objects.filter(assistant=request.user).count(),
        'completed': Order.objects.filter(assistant=request.user, status='Completed').count(),
        'active': Order.objects.filter(assistant=request.user, status__in=['Assigned', 'InTransit']).count(),
        'total_earnings': Order.objects.filter(assistant=request.user, status='Completed').aggregate(
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
@permission_classes([IsAuthenticated, IsPhoneVerified])
def assistant_availability(request):
    """Get/Set rider availability (online/offline) - requires phone verification"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Not a rider'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        return Response({
            'is_available': request.user.is_available,
            'user_id': request.user.id
        })
    
    elif request.method == 'PATCH':
        is_available = request.data.get('is_available')
        request.user.is_available = is_available
        request.user.save(update_fields=['is_available'])
        return Response({
            'message': 'Availability updated',
            'is_available': is_available
        })

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile endpoint.
    Requires phone verification for access.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsPhoneVerified]
    
    @swagger_auto_schema(tags=['accounts'])
    def get(self, request, *args, **kwargs):
        """Get authenticated user's profile - requires phone verification"""
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['accounts'])
    def put(self, request, *args, **kwargs):
        """Update authenticated user's profile - requires phone verification"""
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['accounts'])
    def patch(self, request, *args, **kwargs):
        """Partially update authenticated user's profile - requires phone verification"""
        return super().patch(request, *args, **kwargs)
    
    def get_object(self):
        """Get the profile of the authenticated verified user"""
        return self.request.user.profile



# JWT Token Views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

class CustomTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginThrottle]
    
    @swagger_auto_schema(tags=['accounts'], operation_id='accounts_token_create')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CustomTokenRefreshView(TokenRefreshView):
    throttle_classes = [TokenRefreshThrottle]
    
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
    verifications = AssistantVerification.objects.all().select_related('user')
    
    data = [{
        'id': v.id,
        'assistant_id': v.user.id,
        'assistant_name': f"{v.user.first_name} {v.user.last_name}",
        'assistant_phone': v.user.phone_number,
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
        v = AssistantVerification.objects.select_related('user').get(id=id)
    except AssistantVerification.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'id': v.id,
        'assistant': {
            'id': v.user.id,
            'name': f"{v.user.first_name} {v.user.last_name}",
            'phone': v.user.phone_number,
            'email': v.user.email,
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
        'available_assistants': User.objects.filter(user_type='assistant', is_available=True).count(),
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
    
    users = User.objects.all().order_by('-date_joined')
    user_type = request.query_params.get('user_type')
    if user_type:
        users = users.filter(user_type=user_type)
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    total = users.count()
    
    data = [{
        'id': u.id,
        'phone_number': u.phone_number,
        'email': u.email,
        'first_name': u.first_name,
        'last_name': u.last_name,
        'user_type': u.user_type,
        'is_verified': u.is_verified,
        'is_active': u.is_active,
    } for u in users[start:end]]
    
    return Response({
        'results': data,
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size
    })

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
    """List all verified assistants/riders with availability status"""
    from orders.models import Order
    
    assistants = User.objects.filter(
        user_type='assistant',
        assistant_verification__status='approved'
    ).select_related('assistant_verification')
    
    data = []
    for assistant in assistants:
        # Check if rider has active orders
        active_orders = Order.objects.filter(
            assistant=assistant,
            status__in=['Pending', 'Assigned', 'InTransit']
        ).count()
        
        # Check current order
        current_order = Order.objects.filter(
            assistant=assistant,
            status='InTransit'
        ).first()
        
        is_available = active_orders == 0
        
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
            'is_available': is_available,
            'active_orders_count': active_orders,
            'current_order_number': current_order.order_number if current_order else None,
            'status': 'Available' if is_available else 'On Delivery',
        })
    
    return Response(data)
