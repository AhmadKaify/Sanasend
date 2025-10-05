"""
Staging settings for WhatsApp Web API SaaS
"""
from .production import *

# Override production settings for staging
DEBUG = config('DEBUG', default=False, cast=bool)
ENVIRONMENT_LABEL = 'Staging'

# Less strict security for staging
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Staging database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='whatsapp_saas_staging'),
        'USER': config('DB_USER', default='whatsapp_saas'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 300,  # Shorter connection pooling for staging
        'OPTIONS': {
            'sslmode': 'prefer',  # Less strict SSL for staging
        },
    }
}

# Staging-specific CORS
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://staging.yourdomain.com,https://api-staging.yourdomain.com',
    cast=Csv()
)

# Staging hosts
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='staging.yourdomain.com,api-staging.yourdomain.com',
    cast=Csv()
)

# Staging logging
LOGGING['handlers']['file']['filename'] = config(
    'LOG_FILE', 
    default='/var/log/whatsapp_saas_staging/django.log'
)
LOGGING['handlers']['error_file']['filename'] = config(
    'ERROR_LOG_FILE', 
    default='/var/log/whatsapp_saas_staging/error.log'
)

# Staging static/media paths
STATIC_ROOT = config('STATIC_ROOT', default='/var/www/whatsapp_saas_staging/static/')
MEDIA_ROOT = config('MEDIA_ROOT', default='/var/www/whatsapp_saas_staging/media/')

# Staging rate limits (more lenient)
MAX_MESSAGES_PER_MINUTE = config('MAX_MESSAGES_PER_MINUTE', default=10, cast=int)
MAX_MESSAGES_PER_DAY = config('MAX_MESSAGES_PER_DAY', default=1000, cast=int)

# Staging Node.js service
NODE_SERVICE_URL = config('NODE_SERVICE_URL', default='http://localhost:3001')
DJANGO_BASE_URL = config('DJANGO_BASE_URL', default='https://api-staging.yourdomain.com')
