from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model
from .models import EmailOTP
from .serializers import normalize_phone_number
import random
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def generate_otp():
    """Generate a 4-digit OTP for SMS"""
    return str(random.randint(1000, 9999))


def send_otp_sms(phone_number, otp):
    """Send OTP via SMS using the SMS service"""
    from .services.sms_service import SMSService
    try:
        SMSService.send_otp(phone_number, otp, purpose='password_reset')
        logger.info(f"Password reset OTP sent to {phone_number}")
    except Exception as e:
        logger.error(f"Failed to send password reset OTP to {phone_number}: {str(e)}")


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['phone_number'],
            properties={'phone_number': openapi.Schema(type=openapi.TYPE_STRING)}
        ),
        responses={200: 'OTP sent', 404: 'User not found'}
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize phone number
        normalized_phone = normalize_phone_number(phone_number)
        
        try:
            user = User.objects.get(phone_number=normalized_phone)
            otp_code = generate_otp()
            
            EmailOTP.objects.filter(user=user).delete()
            EmailOTP.objects.create(user=user, otp_code=otp_code)
            
            send_otp_sms(normalized_phone, otp_code)
            
            return Response({'message': 'OTP sent to your phone'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class VerifyPasswordResetOTPView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['phone_number', 'otp'],
            properties={
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                'otp': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={200: 'OTP verified', 400: 'Invalid OTP'}
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')
        
        if not phone_number or not otp:
            return Response({'error': 'Phone number and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        normalized_phone = normalize_phone_number(phone_number)
        
        try:
            user = User.objects.get(phone_number=normalized_phone)
            otp_obj = EmailOTP.objects.filter(
                user=user, 
                otp_code=otp, 
                is_used=False
            ).first()
            
            if not otp_obj:
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'message': 'OTP verified successfully',
                'user_id': user.id
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['phone_number', 'otp', 'new_password'],
            properties={
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                'otp': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={200: 'Password reset successful', 400: 'Invalid request'}
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not all([phone_number, otp, new_password]):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        normalized_phone = normalize_phone_number(phone_number)
        
        try:
            user = User.objects.get(phone_number=normalized_phone)
            otp_obj = EmailOTP.objects.filter(
                user=user,
                otp_code=otp,
                is_used=False
            ).first()
            
            if not otp_obj:
                return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            
            otp_obj.is_used = True
            otp_obj.save()
            
            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
