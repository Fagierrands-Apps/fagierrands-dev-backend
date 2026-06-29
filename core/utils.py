"""
Core utilities - Shared across all apps
"""

import os
import random
import string
import re
from django.conf import settings


def normalize_phone_number(phone):
    """
    Normalize Kenyan phone numbers to +254 format
    Accepts: 0796605409, +254796605409, 254796605409, 796605409
    Returns: 254796605409 (standard format for DB storage)
    """
    if not phone:
        return None
    
    # Remove all non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    # Handle different formats
    if phone.startswith('254'):
        # Already in 254 format
        return phone
    elif phone.startswith('0'):
        # 0796605409 -> 254796605409
        return '254' + phone[1:]
    elif len(phone) == 9:
        # 796605409 -> 254796605409
        return '254' + phone
    
    return phone


def format_phone_number(phone):
    """
    Format phone number for display and SMS sending
    Returns: 254796605409
    """
    return normalize_phone_number(phone)


def generate_otp(length=4):
    """Generate 4-digit numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))


def generate_order_number(prefix='ORD'):
    """Generate unique order number"""
    import time
    timestamp = int(time.time())
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}-{timestamp}{random_suffix}"


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers"""
    from geopy.distance import geodesic
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).kilometers


def calculate_price(distance_km, base_price_per_km=None):
    """Calculate order price based on distance - DEPRECATED, use calculate_parcel_price or calculate_cargo_price"""
    if base_price_per_km is None:
        base_price_per_km = settings.BASE_PRICE_PER_KM
    
    price = distance_km * base_price_per_km
    minimum = settings.MINIMUM_ORDER_AMOUNT
    
    return max(price, minimum)


def calculate_parcel_price(distance_km):
    """
    Calculate parcel delivery price
    First 7.5 km: 200 KES
    Additional km: 23 KES per km
    """
    base_distance = 7.5
    base_price = 200
    additional_rate = 23
    
    if distance_km <= base_distance:
        return {
            'base_fee': base_price,
            'distance_fee': 0,
            'total': base_price,
            'distance_km': distance_km
        }
    
    additional_km = distance_km - base_distance
    distance_fee = additional_km * additional_rate
    total = base_price + distance_fee
    
    return {
        'base_fee': base_price,
        'distance_fee': round(distance_fee, 2),
        'total': round(total, 2),
        'distance_km': distance_km
    }


def calculate_cargo_price(distance_km):
    """
    Calculate cargo delivery price
    First 7.5 km: 500 KES
    Additional km: 28 KES per km
    """
    base_distance = 7.5
    base_price = 500
    additional_rate = 28
    
    if distance_km <= base_distance:
        return {
            'base_fee': base_price,
            'distance_fee': 0,
            'total': base_price,
            'distance_km': distance_km
        }
    
    additional_km = distance_km - base_distance
    distance_fee = additional_km * additional_rate
    total = base_price + distance_fee
    
    return {
        'base_fee': base_price,
        'distance_fee': round(distance_fee, 2),
        'total': round(total, 2),
        'distance_km': distance_km
    }


def format_phone_number(phone):
    """Format phone number to standard format"""
    # Remove spaces, dashes, and plus
    phone = phone.replace(' ', '').replace('-', '').replace('+', '')
    
    # Handle Kenyan numbers
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    elif phone.startswith('7') or phone.startswith('1'):
        phone = '254' + phone
    
    return phone
