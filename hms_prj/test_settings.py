"""
Настройки Django для тестирования в CI/CD
"""
from .production_settings import *

# Отключаем DEBUG для более реалистичных тестов
DEBUG = False
TEMPLATE_DEBUG = False

# Упрощенный INSTALLED_APPS для тестирования (убираем зависимости, которых нет в test.txt)
INSTALLED_APPS = [
    # Убираем jazzmin для тестов - может вызывать проблемы
    # 'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    # Custom Apps
    'hotel',
    'booking',
    'addon',
    'userauths',
    'user_dashboard',
    'search',
    'robokassa',
    'legal',
    'news',

    # Third Party Apps (только те, что есть в base.txt)
    'import_export',
    'mathfilters',
    'taggit',
    # 'anymail',  # Убираем для тестов - нет в base.txt
    'geoip2',   # Оставляем - есть в base.txt
    'channels',
    # 'modeltranslation',  # Убираем для тестов - вызывает ошибки admin
    'django.contrib.humanize',
    'django_crontab',
]

# Используем in-memory базу данных для скорости
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'test_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'TEST': {
            'NAME': 'test_alakol_hms',
        }
    }
}

# Простое кеширование для тестов
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Отключаем миграции для скорости
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Email backend для тестов
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Отключаем логирование для тестов
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Статические файлы для тестов
STATIC_ROOT = '/tmp/staticfiles'
MEDIA_ROOT = '/tmp/media'

# Отключаем сжатие статических файлов для тестов
STORAGES = {
    **STORAGES,
    "staticfiles": {
        "BACKEND": 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# Простое хранилище статических файлов без манифеста
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Отключаем WhiteNoise для тестов
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False

# Английская локализация для тестов
LANGUAGE_CODE = 'en-us'  # Принудительно английский для тестов
USE_I18N = True
USE_TZ = True

# Единственный язык для тестов - английский
LANGUAGES = [
    ('en', 'English'),
]

# Отключаем переводы для тестов
USE_I18N = False

# Секретный ключ для тестов
SECRET_KEY = os.getenv('SECRET_KEY', 'test-secret-key-for-ci-only-not-for-production')

# Разрешенные хосты
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Отключаем SSL для тестов
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Простой пароль хеширование для скорости
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Отключаем проверки админки для тестов (из-за modeltranslation ошибок)
SILENCED_SYSTEM_CHECKS = [
    'admin.E030',  # prepopulated_fields ошибки
    'admin.E108',  # list_display ошибки
]

# Настройки Robokassa для тестов
ROBOKASSA_MERCHANT_LOGIN = 'test_merchant'
ROBOKASSA_MERCHANT_PASSWORD_1 = 'test_password1'
ROBOKASSA_MERCHANT_PASSWORD_2 = 'test_password2'
ROBOKASSA_USE_TEST_MODE = True  # Правильное название переменной
ROBOKASSA_TEST_PASSWORD_1 = 'test_password1'
ROBOKASSA_TEST_PASSWORD_2 = 'test_password2'