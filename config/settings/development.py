"""
Development settings
"""
from .base import *

DEBUG = True

# Development-specific apps
# django_extensions is already included in base settings

# Use SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable password validators in development
AUTH_PASSWORD_VALIDATORS = []

# Debug toolbar (optional - uncomment if needed)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ['127.0.0.1']

