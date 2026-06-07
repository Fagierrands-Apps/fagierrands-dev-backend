"""
NCBA Payment Integration - Till API
"""

import requests
import base64
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_ncba_password():
    """Generate NCBA API password (Base64 encoded timestamp)"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    # Format: Shortcode + Password + Timestamp
    password_str = f"{settings.NCBA_TILL_NO}{settings.NCBA_PASSWORD}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode('utf-8')
    return password, timestamp


def initiate_ncba_payment(order, phone_number, amount):
    """
    Initiate NCBA Till payment
    """
    try:
        password, timestamp = generate_ncba_password()
        
        # Format phone number
        from core.utils import format_phone_number
        phone = format_phone_number(phone_number)
        
        # NCBA API endpoint
        url = "https://api.ncba.co.ke/mpesaapi/CustomerPayBillOnline"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            "BusinessShortCode": settings.NCBA_TILL_NO,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": settings.NCBA_TILL_NO,
            "PhoneNumber": phone,
            "CallBackURL": f"{settings.BASE_URL}/api/orders/payments/ncba/callback/",
            "AccountReference": order.order_number,
            "TransactionDesc": f"Payment for order {order.order_number}"
        }
        
        if settings.DEBUG:
            logger.info(f"NCBA Payment Request: {payload}")
            print(f"\n{'='*60}")
            print(f"NCBA PAYMENT DEBUG")
            print(f"Order: {order.order_number}")
            print(f"Phone: {phone}")
            print(f"Amount: {amount}")
            print(f"Till: {settings.NCBA_TILL_NO}")
            print(f"{'='*60}\n")
            return {
                'success': True,
                'message': 'Payment initiated (DEBUG MODE)',
                'checkout_request_id': f'DEBUG_{order.id}'
            }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('ResponseCode') == '0':
            return {
                'success': True,
                'message': 'Payment prompt sent to phone',
                'checkout_request_id': result.get('CheckoutRequestID'),
                'merchant_request_id': result.get('MerchantRequestID')
            }
        else:
            return {
                'success': False,
                'message': result.get('ResponseDescription', 'Payment failed'),
                'error_code': result.get('ResponseCode')
            }
            
    except Exception as e:
        logger.error(f"NCBA payment error: {str(e)}")
        return {
            'success': False,
            'message': f'Payment initiation failed: {str(e)}'
        }


def check_payment_status(checkout_request_id):
    """
    Check NCBA payment status
    """
    try:
        password, timestamp = generate_ncba_password()
        
        url = "https://api.ncba.co.ke/mpesaapi/stkpushquery/v1/query"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            "BusinessShortCode": settings.NCBA_TILL_NO,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        return result
        
    except Exception as e:
        logger.error(f"Payment status check error: {str(e)}")
        return {'ResultCode': '1', 'ResultDesc': str(e)}
