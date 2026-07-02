
from .development import *      # noqa


## Necessary settings for a production environment
## An extension of the development settings
## See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/


DEBUG = False


# Static files

STATIC_ROOT = BASE_DIR / 'assets'


# https

# SECURE_SSL_REDIRECT = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Secure cookies

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# HTTP Strict Transport Security

# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
