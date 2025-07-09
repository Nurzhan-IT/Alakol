"""
Production settings for Alakol HMS project.
Inherits from base settings and overrides for production environment.

python manage.py collectstatic --settings=hms_prj.production_settings
python manage.py makemigrations --settings=hms_prj.production_settings
python manage.py migrate --settings=hms_prj.production_settings
python manage.py createsuperuser --settings=hms_prj.production_settings
python manage.py runserver --settings=hms_prj.production_settings
python manage.py check --deploy --settings=hms_prj.production_settings
"""

import os
import secrets
from pathlib import Path
from django.utils.translation import gettext
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

# ==============================================
# CORE DJANGO SETTINGS
# ==============================================

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Generate a secure SECRET_KEY for production
SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_urlsafe(50))

# Allowed hosts for production
ALLOWED_HOSTS = [
    'ekol.kz',
    'www.ekol.kz',
    os.getenv('DOMAIN_NAME', ''),
    '46.8.43.15',
    'localhost',
]
# Remove empty strings
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]

# ==============================================
# SECURITY SETTINGS
# ==============================================

# HTTPS and Security Settings
SECURE_SSL_REDIRECT = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'same-origin'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS settings for enhanced security
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie security
LANGUAGE_COOKIE_SECURE = True
LANGUAGE_COOKIE_HTTPONLY = True

# ==============================================
# APPLICATION DEFINITION
# ==============================================

INSTALLED_APPS = [
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',  # Добавлено для SEO

    # Custom Apps
    'hotel',
    'booking',
    'addon',
    'userauths',
    'user_dashboard',
    'search',
    'robokassa',
    'legal',

    # Third Party Apps
    'import_export',
    'crispy_forms',
    'mathfilters',
    'taggit',
    "anymail",
    'geoip2',
    'django_user_agents',
    'storages',
    'channels',
    'multiupload',
    'modeltranslation',
    'django.contrib.humanize',
    'django_crontab',
    'clearcache',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For serving static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'hotel.middleware.AdminRussianLanguageMiddleware',  # Принудительно устанавливает русский для админки
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'legal.middleware.AdminLegalConsentMiddleware',  # Проверка согласия с legal agreements для админки
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hms_prj.urls'

# ==============================================
# TEMPLATES
# ==============================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.i18n',
                'hotel.context_processor.default',
                'hotel.context_processor.admin_russian_language',  # Принудительно русский для админки
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'legal.context_processors.legal_documents',
            ],
        },
    },
]

WSGI_APPLICATION = 'hms_prj.wsgi.application'

# ==============================================
# DATABASE
# ==============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'db'),  # Docker service name as default
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # 10 минут connection pooling для production
    }
}

# ==============================================
# PASSWORD VALIDATION
# ==============================================

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

# ==============================================
# INTERNATIONALIZATION
# ==============================================

LANGUAGE_CODE = 'ru'  # Default to Russian for production

TIME_ZONE = 'Asia/Yekaterinburg'  # UTC+5, Алматы не обновленый там +6 до сих пор

USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = False
USE_TZ = True

gettext = lambda s:s
LANGUAGES = (
    ("kk", gettext("Kazakh")),
    ("ru", gettext("Russia")),
    ("en", gettext("English")),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# Настройки для языкового cookie
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = None  # Действует до закрытия браузера
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_PATH = '/'
LANGUAGE_COOKIE_SECURE = True  # Secure for production
LANGUAGE_COOKIE_HTTPONLY = True  # HttpOnly for production
LANGUAGE_COOKIE_SAMESITE = 'Lax'

# ==============================================
# STATIC FILES (CSS, JavaScript, Images)
# ==============================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Static files optimization for production
# Используем CompressedStaticFilesStorage вместо ManifestStaticFilesStorage
# чтобы избежать проблем с отсутствующими source map файлами
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# WhiteNoise settings for better performance
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_AUTOREFRESH = False  # Disable in production
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'tgz', 'bz2', 'tbz', 'xz', 'br']

# ==============================================
# MEDIA FILES
# ==============================================

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ==============================================
# AUTHENTICATION
# ==============================================

LOGIN_URL = "userauths:sign-in"
LOGIN_REDIRECT_URL = ""
LOGOUT_REDIRECT_URL = "userauths:sign-in"

AUTH_USER_MODEL = 'userauths.User'

AUTHENTICATION_BACKENDS = [
    'userauths.backends.CaseInsensitiveEmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ==============================================
# EMAIL SETTINGS
# ==============================================

# Website Address
WEBSITE_ADDRESS = os.getenv("WEBSITE_ADDRESS", "https://ekol.kz")

# Email backend configuration
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "anymail.backends.amazon_ses.EmailBackend")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@ekol.kz")

# Anymail configuration
ANYMAIL = {
    "MAILGUN_API_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": os.getenv("MAILGUN_SENDER_DOMAIN"),  
}

# AWS SES Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_SES_REGION_NAME = AWS_REGION
AWS_SES_REGION_ENDPOINT = f'email.{AWS_REGION}.amazonaws.com'

# ==============================================
# CACHING CONFIGURATION
# ==============================================

# Redis Configuration for Docker Production Caching
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/1"),  # Docker service name
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 20,  # Оптимизировано для VPS 8GB RAM
                "retry_on_timeout": True,
                "health_check_interval": 30,
            },
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "SERIALIZER": "django_redis.serializers.pickle.PickleSerializer",
        },
        "KEY_PREFIX": "alakol",
        "TIMEOUT": 300,  # 5 минут по умолчанию
    },

    "long_term": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/3"),  # Docker service name
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 10,  # Меньше соединений для долгосрочного кеша
                "retry_on_timeout": True,
                "health_check_interval": 60,
            },
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        },
        "KEY_PREFIX": "alakol_longterm",
        "TIMEOUT": 3600,  # 1 час для долгосрочных данных
    }
}

# Cache времена жизни для различных типов данных
CACHE_TTL = {
    'hotels_list': 1800,         # 30 минут - список отелей (увеличено для продакшена)
    'hotel_detail': 3600,        # 1 час - детали отеля
    'search_results': 600,       # 10 минут - результаты поиска
    'room_availability': 30,    # 30 секунд - доступность номеров
    'hotel_reviews': 7200,       # 2 часа - отзывы отеля
    'features_and_amenities': 14400,  # 4 часа - удобства и особенности
    'static_content': 86400,     # 24 часа - статический контент
    'room_unavailability': 30,  # 30 секунд - недоступность номеров
}

# ==============================================
# SESSION CONFIGURATION
# ==============================================

# Session Configuration for production
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_COOKIE_AGE = 86400  # 24 часа
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False  # Don't save on every request in production

# ==============================================
# CSRF CONFIGURATION
# ==============================================

CSRF_TRUSTED_ORIGINS = [
    'https://ekol.kz',
    'https://www.ekol.kz',
    f'https://{os.getenv("DOMAIN_NAME", "")}' if os.getenv("DOMAIN_NAME") else '',
]
# Remove empty strings
CSRF_TRUSTED_ORIGINS = [origin for origin in CSRF_TRUSTED_ORIGINS if origin]

# ==============================================
# ROBOKASSA SETTINGS
# ==============================================

ROBOKASSA_MERCHANT_LOGIN = os.getenv('ROBOKASSA_MERCHANT_LOGIN')
ROBOKASSA_MERCHANT_PASSWORD_1 = os.getenv('ROBOKASSA_MERCHANT_PASSWORD_1')
ROBOKASSA_MERCHANT_PASSWORD_2 = os.getenv('ROBOKASSA_MERCHANT_PASSWORD_2')
ROBOKASSA_TEST_PASSWORD_1 = os.getenv('ROBOKASSA_TEST_PASSWORD_1')
ROBOKASSA_TEST_PASSWORD_2 = os.getenv('ROBOKASSA_TEST_PASSWORD_2')
ROBOKASSA_USE_TEST_MODE = os.getenv('ROBOKASSA_USE_TEST_MODE', False)  # Always False in production

# ==============================================
# CRONJOBS
# ==============================================

CRONJOBS = [
    ('*/5 * * * *', 'hotel.cron.handle_bookings_payment_status_processing'),
]

# ==============================================
# JAZZMIN ADMIN CONFIGURATION
# ==============================================

JAZZMIN_SETTINGS = {
    'site_header': "Alakol HMS",
    'site_brand': ".",
    'site_logo': "/images/logo.png",
    'copyright':  "Все права защищены 2025",
    "welcome_sign": "Добро пожаловать в Alakol HMS, войдите сейчас.",
    
    "language_chooser": False,
    
    "topmenu_links": [
        {"name": "Главная",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "AUTH_USER_MODEL.User"},
    ],

    "order_with_respect_to": [
        "hotel",
        "hotel.Hotel",
        "hotel.RoomTypeComplete",
        "hotel.Room",
        "hotel.RoomType",
        "hotel.Booking",
        "hotel.RoomServices",
        "hotel.Bookmark",
        "hotel.Coupon",
        "hotel.Review",
        "hotel.Notification",
        "userauths",
        "addons",
    ],
    
    "icons": {
        "admin.LogEntry": "fas fa-file",
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "userauths.User": "fas fa-user",
        "userauths.Profile":"fas fa-address-card",
        "hotel.Hotel": "fas fa-th",
        "hotel.RoomTypeComplete": "fas fa-cogs",
        "hotel.Room":"fas fa-bed",
        "hotel.RoomType":"fas fa-dollar-sign",
        "hotel.Booking":"fas fa-calendar-week",
        "hotel.RoomServices":"fas fa-user-cog",
        "hotel.Bookmark":"fas fa-heart",
        "hotel.Coupon":"fas fa-tag",
        "hotel.Review":"fas fa-star",
        "hotel.Notification":"fas fa-bell",
    },

    "show_ui_builder" : False  # Disable in production
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-indigo",
    "accent": "accent-olive",
    "navbar": "navbar-indigo navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-indigo",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": "default",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# ==============================================
# LOGGING CONFIGURATION
# ==============================================

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
            'level': 'WARNING',  # Only warnings and errors in production console
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'production.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'hotel.views': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'robokassa.robokassa': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'booking': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'userauths': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ==============================================
# ADDITIONAL PRODUCTION SETTINGS
# ==============================================

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Disable browsable API in production
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ]
} if 'rest_framework' in INSTALLED_APPS else {}

# Performance settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# ==============================================
# DOCKER PRODUCTION OPTIMIZATIONS
# ==============================================

# Application version for monitoring
VERSION = "1.0.0"

# Gunicorn settings (referenced in Dockerfile)
import multiprocessing
GUNICORN_WORKERS = min(4, (multiprocessing.cpu_count() * 2) + 1)
GUNICORN_THREADS = 2
GUNICORN_WORKER_CLASS = 'gthread'
GUNICORN_MAX_REQUESTS = 1000
GUNICORN_MAX_REQUESTS_JITTER = 100

# Session optimization for production
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_TEMP_DIR = '/tmp'

# Security enhancements
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Disable Django's own static file serving in production
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False

# Email backend for production (using AWS SES)
if os.getenv('AWS_SES_REGION_NAME'):
    EMAIL_BACKEND = 'anymail.backends.amazon_ses.EmailBackend'
    ANYMAIL = {
        'AMAZON_SES_REGION': os.getenv('AWS_SES_REGION_NAME', 'us-east-1'),
        'AMAZON_SES_CLIENT_PARAMS': {
            'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        },
    }
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'info@ekol.kz')
    SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'info@ekol.kz')
else:
    # Fallback to console email backend
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

print("🚀 Alakol HMS Production settings loaded successfully!") 