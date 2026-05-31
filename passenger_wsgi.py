import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# Load all environment variables
env_vars = {
    'DB_NAME': 'distinc3_FagierrandsNew',
    'DB_USER': 'distinc3_FagierrandsNew',
    'DB_PASSWORD': 'Pa7swrd1990@',
    'DB_HOST': 'localhost',
    'DB_PORT': '5432',
    'DB_ENGINE': 'django.db.backends.postgresql',
    'SECRET_KEY': '9r1%hz2tdkhu39#6f^^_z(&0u&1g8=^cy_$(907_fs#tni-1r7',
    'DEBUG': 'False',
    'ALLOWED_HOSTS': 'api.errandserver.fagitone.com',
    'DJANGO_SETTINGS_MODULE': 'fagierrandsbackup.settings',
    'GOOGLE_MAPS_API_KEY': '',
    'TEXTPIE_API_KEY': 'M176esJGFImYzBlqk9dgKfjuRXE2U3nyHZQvL4hiAWp08rTxwSNDVabtPO5oCc',
    'TEXTPIE_SERVICE_ID': '77',
    'TEXTPIE_SHORTCODE': 'FagiErrands',
    'SUPABASE_URL': 'https://lmwloxheulmybtrnfobz.supabase.co',
    'SUPABASE_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxtd2xveGhldWxteWJ0cm5mb2J6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5NzcxMjMsImV4cCI6MjA5NDU1MzEyM30.O8ScKmH9pIrejFClsOWDvyhFvBXIsPeHE95dSQ4VlN0',
    'SUPABASE_SERVICE_ROLE_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxtd2xveGhldWxteWJ0cm5mb2J6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODk3NzEyMywiZXhwIjoyMDk0NTUzMTIzfQ.OTHbQrAj1mwRNsEjT3Mgj41rqFaJDp56lsEKoUAqcp0',
}

for key, value in env_vars.items():
    os.environ.setdefault(key, value)

from fagierrandsbackup.wsgi import application
