
from .base import *


DEBUG = False


# Static files

STATIC_ROOT = BASE_DIR / 'assets'


# Secure cookies (https:// only)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# Security middleware

SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000

SECURE_SSL_REDIRECT = True


# Load the private settings if a private.py file exists.
try:
    from .private import *
except ImportError:
    pass
