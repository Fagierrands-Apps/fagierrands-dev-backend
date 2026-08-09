"""
SMS Service - Send OTP via TextPie SMS API
"""

import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_sms(phone_number, message):
    try:
        from core.utils import format_phone_number
        phone = format_phone_number(phone_number)

        logger.info(f"SMS to {phone}: {message}")

        url = "https://api.textpie.co.ke/sms/sendsms"
        payload = {
            "api_key": settings.TEXTPIE_API_KEY,
            "service_id": int(settings.TEXTPIE_SERVICE_ID),
            "mobile": phone,
            "response_type": "json",
            "shortcode": settings.TEXTPIE_SHORTCODE,
            "message": message
        }

        response = requests.post(url, json=payload, timeout=10)

        try:
            result = response.json()
            if result.get('status_code') == '1000' or result.get('success'):
                logger.info(f"SMS sent successfully to {phone}")
                return True
            else:
                logger.error(f"SMS failed to {phone}: {result.get('status_desc', 'unknown error')}")
                return False
        except Exception:
            if response.status_code == 200:
                logger.info(f"SMS sent to {phone} (status 200)")
                return True
            logger.error(f"SMS API error: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"SMS exception for {phone_number}: {str(e)}")
        return False


def send_otp(phone_number, otp):
    message = f"Your FagiErrands verification code is: {otp}. Valid for 10 minutes. Do not share this code."
    return send_sms(phone_number, message)


def send_password_reset_otp(phone_number, otp):
    message = f"Your FagiErrands password reset code is: {otp}. Valid for 10 minutes."
    return send_sms(phone_number, message)
