import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '..' / '.env')

# Avoid AutoField warnings
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Debug and allowed hosts
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# load env vars from .env if you use python-dotenv (optional)
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '..' / '.env')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'msdc'),
        'USER': os.getenv('POSTGRES_USER', 'msdc_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'msdc_pass'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}
