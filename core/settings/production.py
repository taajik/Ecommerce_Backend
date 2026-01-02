
from .development import *


## Necessary settings for a production environment
## An extension of the development settings
## See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/


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
