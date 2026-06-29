"""
Django settings for fagierrands project.
Clean build - No dead code.
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

# Load environment variables
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security - Read from .env
SECRET_KEY = os.getenv('SECRET_KEY', '9r1%hz2tdkhu39#6f^^_z(&0u&1g8=^cy_$(907_fs#tni-1r7')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Fix trailing slash issue for mobile app
APPEND_SLASH = False

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    'channels',
    
    # Local apps
    'accounts',
    'orders',
    'locations',
    'notifications',
    'admin_dashboard',
    'marketplace',
]

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fagierrands.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fagierrands.wsgi.application'
ASGI_APPLICATION = 'fagierrands.asgi.application'

# Database
# Use SQLite for testing, PostgreSQL for production
USE_SQLITE = os.getenv('USE_SQLITE', 'False') == 'True'

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# Swagger Settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
        }
    },
    'USE_SESSION_AUTH': False,
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME', 1))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME', 7))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings - HARDCODED
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'https://fagierrands-handler-dashboard.vercel.app',
    'https://fagiserver.fagitone.com',
    'https://api.errandserver.fagierrands.com',  # API domain itself
]
CORS_ALLOW_CREDENTIALS = True

# CSRF Settings - Trust API domain
CSRF_TRUSTED_ORIGINS = [
    'https://api.errandserver.fagierrands.com',
    'https://fagiserver.fagitone.com',
]

# Supabase Configuration - HARDCODED
SUPABASE_URL = 'https://lmwloxheulmybtrnfobz.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxtd2xveGhldWxteWJ0cm5mb2J6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5NzcxMjMsImV4cCI6MjA5NDU1MzEyM30.O8ScKmH9pIrejFClsOWDvyhFvBXIsPeHE95dSQ4VlN0'
SUPABASE_SERVICE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxtd2xveGhldWxteWJ0cm5mb2J6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODk3NzEyMywiZXhwIjoyMDk0NTUzMTIzfQ.OTHbQrAj1mwRNsEjT3Mgj41rqFaJDp56lsEKoUAqcp0'
SUPABASE_STORAGE_URL = 'https://lmwloxheulmybtrnfobz.supabase.co/storage/v1'
SUPABASE_BUCKET_NAME = 'user-uploads'

# Cloudinary Configuration - HARDCODED (if you have values)
CLOUDINARY_CLOUD_NAME = ''
CLOUDINARY_API_KEY = ''
CLOUDINARY_API_SECRET = ''

# SMS Configuration - HARDCODED (TextPie)
SMS_API_KEY = 'M176esJGFImYzBlqk9dgKfjuRXE2U3nyHZQvL4hiAWp08rTxwSNDVabtPO5oCc'
SMS_USERNAME = 'FagiErrands'
SMS_SENDER_ID = 'FagiErrands'
TEXTPIE_API_KEY = 'M176esJGFImYzBlqk9dgKfjuRXE2U3nyHZQvL4hiAWp08rTxwSNDVabtPO5oCc'
TEXTPIE_SERVICE_ID = '77'
TEXTPIE_SHORTCODE = 'FagiErrands'

# Google Maps API - HARDCODED
GOOGLE_MAPS_API_KEY = 'AIzaSyDT22XW8FHw6Pd1lNkh1UxDXSN6HrBUtsQ'

# Payment Configuration - HARDCODED (NCBA)
NCBA_USERNAME = 'Errand@123'
NCBA_PASSWORD = '9Y7a24B5TNxxKimfnGz9MTbdn960JY57ASC/r6KOCQNnR220v52od6a2ajgEaipL'
NCBA_TILL_NO = '852054'
NCBA_PAYBILL_NO = '880100'
NCBA_TRANSACTION_TYPE = 'CustomerPayBillOnline'
NCBA_USE_TILL_AS_ACCOUNT = False
NCBA_CALLBACK_URL = 'http://localhost:8000/api/orders/payments/ncba/callback/'
BASE_URL = 'http://localhost:8000'

# Pricing Configuration - HARDCODED
BASE_PRICE_PER_KM = 50
MINIMUM_ORDER_AMOUNT = 100

# Email Configuration - HARDCODED
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'no-reply@fagitone.com'
EMAIL_HOST_PASSWORD = ''  # Add if you have it
DEFAULT_FROM_EMAIL = 'no-reply@fagitone.com'

# Push Notifications - HARDCODED
FCM_SERVER_KEY = ''  # Add FCM key if available
VAPID_PUBLIC_KEY = ''
VAPID_PRIVATE_KEY = ''
VAPID_ADMIN_EMAIL = ''

# Groq AI - HARDCODED
GROQ_API_KEY = ''

# Redis & Celery - HARDCODED
REDIS_URL = 'redis://localhost:6379/0'
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# Google Maps
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# App Settings
DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'KES')
BASE_PRICE_PER_KM = float(os.getenv('BASE_PRICE_PER_KM', 100))
MINIMUM_ORDER_AMOUNT = float(os.getenv('MINIMUM_ORDER_AMOUNT', 200))

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
(BASE_DIR / 'logs').mkdir(exist_ok=True)
