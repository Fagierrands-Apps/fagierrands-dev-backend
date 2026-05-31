import os
import sys

# Add the fagierrandsbackup directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fagierrandsbackup'))

# Force load environment variables if not already set
if not os.environ.get('DB_NAME'):
    # Set from cPanel environment or use defaults
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
    }
    for key, value in env_vars.items():
        if not os.environ.get(key):
            os.environ[key] = value

from fagierrandsbackup.wsgi import application
