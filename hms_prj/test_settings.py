"""
Настройки Django для тестирования в CI/CD
"""
from .production_settings import *

# Отключаем DEBUG для более реалистичных тестов
DEBUG = False
TEMPLATE_DEBUG = False

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

# Статические файлы
STATIC_ROOT = '/tmp/staticfiles'
MEDIA_ROOT = '/tmp/media'

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