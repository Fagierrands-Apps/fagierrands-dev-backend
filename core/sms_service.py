"""
SMS Service - Send OTP via TextPie SMS API
"""

import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_sms(phone_number, message):
    """
    Send SMS using TextPie API (Correct URL from old backend)
    """
    try:
        # Format phone number (254...)
        from core.utils import format_phone_number
        phone = format_phone_number(phone_number)
        
        # Always log the SMS
        logger.info(f"SMS to {phone}: {message}")
        print(f"\n{'='*60}")
        print(f"SENDING SMS VIA TEXTPIE")
        print(f"To: {phone}")
        print(f"Message: {message}")
        print(f"{'='*60}\n")
        
        # TextPie SMS API - CORRECT URL
        url = "https://api.textpie.co.ke/sms/sendsms"
        
        payload = {
            "api_key": settings.TEXTPIE_API_KEY,
            "service_id": int(settings.TEXTPIE_SERVICE_ID),
            "mobile": phone,
            "response_type": "json",
            "shortcode": settings.TEXTPIE_SHORTCODE,
            "message": message
        }
        
        print(f"TextPie API Request:")
        print(f"URL: {url}")
        print(f"Payload: {payload}\n")
        
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"TextPie API Response:")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}\n")
        
        try:
            result = response.json()
            print(f"JSON: {result}\n")
            
            if result.get('status_code') == '1000' or result.get('success'):
                logger.info(f"SMS sent successfully to {phone}")
                print(f"SMS SENT SUCCESSFULLY!\n")
                return True
            else:
                logger.error(f"SMS failed: {result}")
                print(f"SMS FAILED: {result}\n")
                return False
        except:
            # If not JSON, check status code
            if response.status_code == 200:
                logger.info(f"SMS sent (status 200)")
                return True
            else:
                logger.error(f"SMS API error: {response.status_code}")
                return False
            
    except Exception as e:
        logger.error(f"SMS exception: {str(e)}")
        print(f"SMS ERROR: {str(e)}\n")
        return False


def send_otp(phone_number, otp):
    """Send OTP via SMS"""
    message = f"Your FagiErrands verification code is: {otp}. Valid for 10 minutes. Do not share this code."
    return send_sms(phone_number, message)


def send_password_reset_otp(phone_number, otp):
    """Send password reset OTP"""
    message = f"Your FagiErrands password reset code is: {otp}. Valid for 10 minutes."
    return send_sms(phone_number, message)
