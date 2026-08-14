"""
File upload validation utilities for Supabase-hosted files.

Since we use client-side Supabase uploads (not direct Django uploads),
this validates the metadata of Supabase URLs before storing references.
"""

import requests
from django.conf import settings
from urllib.parse import urlparse

# Allowed file types for different use cases
ALLOWED_TYPES = {
    'image': {'image/jpeg', 'image/png', 'image/webp', 'image/gif'},
    'document': {'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'},
    'video': {'video/mp4', 'video/quicktime'},
}

# Size limits (bytes)
FILE_SIZE_LIMITS = {
    'image': 10 * 1024 * 1024,  # 10 MB
    'document': 50 * 1024 * 1024,  # 50 MB
    'video': 500 * 1024 * 1024,  # 500 MB
    'default': 10 * 1024 * 1024,  # 10 MB
}

SUPABASE_BUCKET_URL = getattr(settings, 'SUPABASE_URL', '').rstrip('/') + '/storage/v1/object/public/'


def is_supabase_url(url: str) -> bool:
    """Verify URL is from our Supabase bucket"""
    if not url:
        return False
    supabase_url = getattr(settings, 'SUPABASE_URL', '')
    if not supabase_url:
        return False
    return url.startswith(supabase_url + '/storage/v1/object/public/')


def validate_file_url(url: str, file_type: str = 'image') -> tuple[bool, str]:
    """
    Validate a Supabase file URL.
    
    Returns: (is_valid: bool, error_message: str)
    """
    if not url:
        return False, 'File URL is required'
    
    # Whitelist Supabase URLs only
    if not is_supabase_url(url):
        return False, 'File must be hosted on authorized storage service (Supabase)'
    
    # Check if URL is a valid URL format
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, 'Invalid URL format'
    except Exception as e:
        return False, f'Invalid URL: {str(e)}'
    
    # Get file metadata via HEAD request (don't download entire file)
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        
        # Check response status
        if response.status_code != 200:
            return False, f'File not found or inaccessible (HTTP {response.status_code})'
        
        # Check content type
        content_type = response.headers.get('content-type', '').split(';')[0].lower()
        allowed_types = ALLOWED_TYPES.get(file_type, ALLOWED_TYPES['image'])
        if content_type not in allowed_types:
            return False, f'File type {content_type} not allowed. Allowed: {", ".join(allowed_types)}'
        
        # Check file size
        content_length = response.headers.get('content-length')
        if content_length:
            size = int(content_length)
            max_size = FILE_SIZE_LIMITS.get(file_type, FILE_SIZE_LIMITS['default'])
            if size > max_size:
                return False, f'File too large ({size / 1024 / 1024:.1f}MB > {max_size / 1024 / 1024:.1f}MB limit)'
        
        return True, ''
        
    except requests.Timeout:
        return False, 'File server timeout — could not verify file'
    except requests.RequestException as e:
        return False, f'Could not reach file server: {str(e)}'
    except Exception as e:
        return False, f'File validation error: {str(e)}'
