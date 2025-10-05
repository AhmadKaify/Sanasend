"""
Base settings for WhatsApp Web API SaaS project.
"""
from pathlib import Path
from decouple import config, Csv
from django.urls import reverse_lazy

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Application definition
INSTALLED_APPS = [
    # Django Unfold must be before django.contrib.admin
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    'django_extensions',
    
    # Local apps
    'users.apps.UsersConfig',
    'sessions.apps.SessionsConfig',
    'messages.apps.MessagesConfig',
    'api_keys.apps.ApiKeysConfig',
    'analytics.apps.AnalyticsConfig',
    'core.apps.CoreConfig',
    'dashboard.apps.DashboardConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'core.security.SecurityHeadersMiddleware',
    'core.security.BruteForceProtectionMiddleware',
    'core.security.RequestValidationMiddleware',
    'core.security.SQLInjectionProtectionMiddleware',
    'core.security.InputSanitizationMiddleware',
    'core.security.IPWhitelistMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.RateLimitMiddleware',
    'core.middleware.UsageTrackingMiddleware',
    'core.middleware.APILoggingMiddleware',
    'core.security.SecurityAuditMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='whatsapp_saas'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Sites Framework
SITE_ID = 1

# Login settings
LOGIN_URL = '/dashboard/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/dashboard/login/'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'api_keys.authentication.APIKeyAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:8000',
    cast=Csv()
)
CORS_ALLOW_CREDENTIALS = True

# Redis Configuration
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)
REDIS_DB = config('REDIS_DB', default=0, cast=int)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'whatsapp_saas',
        'TIMEOUT': 300,
    }
}

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=f'redis://{REDIS_HOST}:{REDIS_PORT}/1')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=f'redis://{REDIS_HOST}:{REDIS_PORT}/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    'aggregate-daily-usage': {
        'task': 'analytics.tasks.aggregate_daily_usage_stats',
        'schedule': 60.0 * 60.0,  # Run every hour
    },
    'cleanup-old-usage-data': {
        'task': 'analytics.tasks.cleanup_old_usage_data',
        'schedule': 60.0 * 60.0 * 24.0,  # Run daily
    },
    'cleanup-inactive-sessions': {
        'task': 'analytics.tasks.cleanup_inactive_sessions',
        'schedule': 60.0 * 30.0,  # Run every 30 minutes
    },
    'cleanup-old-messages': {
        'task': 'analytics.tasks.cleanup_old_messages',
        'schedule': 60.0 * 60.0 * 24.0,  # Run daily
    },
    'health-check': {
        'task': 'analytics.tasks.health_check',
        'schedule': 60.0 * 5.0,  # Run every 5 minutes
    },
}

# Node.js Service Configuration
NODE_SERVICE_URL = config('NODE_SERVICE_URL', default='http://localhost:3000')
NODE_SERVICE_API_KEY = config('NODE_SERVICE_API_KEY', default='change-this-secret-key')

# Django Base URL (for media file access from Node.js)
DJANGO_BASE_URL = config('DJANGO_BASE_URL', default='http://localhost:8000')

# Rate Limiting
MAX_MESSAGES_PER_MINUTE = config('MAX_MESSAGES_PER_MINUTE', default=10, cast=int)
MAX_MESSAGES_PER_DAY = config('MAX_MESSAGES_PER_DAY', default=1000, cast=int)

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'WhatsApp Web API',
    'DESCRIPTION': 'SaaS API for WhatsApp Web messaging',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# Environment label for admin
ENVIRONMENT_LABEL = config('ENVIRONMENT', default='Development')

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# API Security Settings
API_IP_WHITELIST = config('API_IP_WHITELIST', default='', cast=Csv())
MAX_INPUT_LENGTH = config('MAX_INPUT_LENGTH', default=10000, cast=int)

# Brute Force Protection
BRUTE_FORCE_ENABLED = config('BRUTE_FORCE_ENABLED', default=True, cast=bool)
BRUTE_FORCE_MAX_ATTEMPTS = config('BRUTE_FORCE_MAX_ATTEMPTS', default=5, cast=int)
BRUTE_FORCE_LOCKOUT_TIME = config('BRUTE_FORCE_LOCKOUT_TIME', default=900, cast=int)  # 15 minutes

# Django Unfold Configuration
UNFOLD = {
    "SITE_TITLE": "WhatsApp Web API Admin",
    "SITE_HEADER": "WhatsApp Web API SaaS",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "SITE_LOGO": None,
    "SITE_SYMBOL": "messages",  # Icon from Material Design
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "ENVIRONMENT": lambda request: ENVIRONMENT_LABEL,
    "DASHBOARD_CALLBACK": None,
    "LOGIN": {
        "image": None,
    },
    "STYLES": [],
    "COLORS": {
        "primary": {
            "50": "240 253 250",
            "100": "204 251 241",
            "200": "153 246 228",
            "300": "102 240 214",
            "400": "45 212 191",
            "500": "0 201 167",
            "600": "0 180 149",
            "700": "0 159 131",
            "800": "0 138 113",
            "900": "0 117 95",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Navigation",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": lambda request: "/admin/",
                    },
                ],
            },
            {
                "title": "User Management",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": lambda request: "/admin/users/user/",
                    },
                    {
                        "title": "API Keys",
                        "icon": "key",
                        "link": lambda request: "/admin/api_keys/apikey/",
                    },
                ],
            },
            {
                "title": "WhatsApp",
                "separator": True,
                "items": [
                    {
                        "title": "Sessions",
                        "icon": "link",
                        "link": lambda request: "/admin/sessions/whatsappsession/",
                    },
                    {
                        "title": "Messages",
                        "icon": "message",
                        "link": lambda request: "/admin/messages/message/",
                    },
                ],
            },
            {
                "title": "Analytics",
                "separator": True,
                "items": [
                    {
                        "title": "Usage Stats",
                        "icon": "bar_chart",
                        "link": lambda request: "/admin/analytics/usagestats/",
                    },
                    {
                        "title": "API Logs",
                        "icon": "article",
                        "link": lambda request: "/admin/analytics/apilog/",
                    },
                ],
            },
        ],
    },
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
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
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

