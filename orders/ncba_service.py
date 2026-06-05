"""
NCBA Till STK Push & Dynamic QR Code API Integration Service
"""
import requests
import base64
import logging
import json
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class NCBAService:
    """
    Service class for interacting with NCBA Till API
    Supports: STK Push and Dynamic QR Code generation
    """
    
    def __init__(self):
        self.base_url = "https://c2bapis.ncbagroup.com"
        self.username = getattr(settings, 'NCBA_USERNAME', '')
        self.password = getattr(settings, 'NCBA_PASSWORD', '')
        self.paybill_no = getattr(settings, 'NCBA_PAYBILL_NO', '880100')
        self.till_no = getattr(settings, 'NCBA_TILL_NO', '')
        self.default_transaction_type = getattr(settings, 'NCBA_TRANSACTION_TYPE', 'CustomerPayBillOnline')
        self.use_till_as_account = getattr(settings, 'NCBA_USE_TILL_AS_ACCOUNT', False)
        self.callback_url = getattr(settings, 'NCBA_CALLBACK_URL', '')
        self.timeout = 30

    def get_access_token(self):
        """Retrieve authorization token from NCBA API"""
        cache_key = 'ncba_access_token'
        token = cache.get(cache_key)
        
        if token:
            logger.info("Using cached NCBA access token")
            return token
        
        # Validate credentials
        if not self.username or not self.password:
            logger.error("NCBA credentials not configured")
            raise Exception("NCBA credentials missing. Set NCBA_USERNAME and NCBA_PASSWORD in cPanel.")
            
        try:
            url = f"{self.base_url}/payments/api/v1/auth/token"
            logger.info(f"Fetching NCBA token for user: {self.username}")
            
            auth_string = f"{self.username}:{self.password}"
            auth_base64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_base64}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 401:
                logger.error(f"NCBA 401 Unauthorized - Invalid credentials for user: {self.username}")
                logger.error(f"Response: {response.text}")
                raise Exception("Invalid NCBA credentials. Verify NCBA_USERNAME and NCBA_PASSWORD.")
            
            logger.info(f"NCBA token response: {response.status_code}")
            response.raise_for_status()
            
            result = response.json()
            token = result.get('access_token')
            expires_in = result.get('expires_in', 18000)
            
            if token:
                logger.info("NCBA access token obtained")
                cache.set(cache_key, token, expires_in - 900)
                return token
            else:
                raise Exception("No access token in response")
                
        except requests.exceptions.Timeout:
            logger.error("NCBA token request timed out")
            raise Exception("NCBA authentication timed out")
        except Exception as e:
            logger.error(f"NCBA authentication failed: {str(e)}")
            raise

    def initiate_stk_push(self, phone_number, amount, account_no, transaction_type=None, paybill_no=None, network="Safaricom"):
        """Initiate STK push transaction"""
        try:
            access_token = self.get_access_token()
            url = f"{self.base_url}/payments/api/v1/stk-push/initiate"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            tx_type = transaction_type or self.default_transaction_type
            pb_no = paybill_no or self.paybill_no
            
            if tx_type == "CustomerBuyGoodsOnline" and not paybill_no:
                pb_no = self.till_no
            
            acc_no = self.till_no if self.use_till_as_account else account_no
                
            payload = {
                "TelephoneNo": phone_number,
                "Amount": str(amount),
                "PayBillNo": pb_no,
                "AccountNo": acc_no,
                "Network": network,
                "TransactionType": tx_type
            }
            
            if self.callback_url:
                payload["CallBackURL"] = self.callback_url
            
            logger.info(f"NCBA STK Push: {phone_number}, Amount: {amount}, Till: {acc_no}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            logger.info(f"NCBA STK response: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            
            status_code = str(result.get('StatusCode', ''))
            result['success'] = status_code == '0'
            if not result['success']:
                result['error'] = result.get('StatusDescription', f'Error code: {status_code}')
                
            return result
            
        except Exception as e:
            logger.error(f"NCBA STK Push failed: {str(e)}")
            raise Exception(f"Failed to initiate NCBA payment: {str(e)}")

    def stk_query(self, transaction_id):
        """Query STK push transaction status"""
        try:
            access_token = self.get_access_token()
            url = f"{self.base_url}/payments/api/v1/stk-push/query"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {"TransactionID": transaction_id}
            
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"NCBA STK Query failed: {str(e)}")
            raise Exception(f"Failed to query NCBA transaction: {str(e)}")

    def generate_qr(self, amount=None, narration=None):
        """Generate payment QR code"""
        try:
            access_token = self.get_access_token()
            url = f"{self.base_url}/payments/api/v1/qr/generate"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            till_value = f"{self.till_no}#{narration}" if narration else self.till_no
            payload = {"till": till_value}
            
            if amount:
                payload["amount"] = float(amount)
                
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"NCBA QR Generation failed: {str(e)}")
            raise Exception(f"Failed to generate NCBA QR code: {str(e)}")
