# Рекомендации по улучшению конфигурации проекта Alakol HMS

## Анализ проекта

Проект использует Django с системой управления отелями, включающей:
- Бронирование номеров
- Платежную систему (Robokassa)
- Многоязычность (RU, KK, EN)
- Email уведомления (AWS SES/Mailgun)
- Кеширование (Redis)
- Админ-панель (Jazzmin)

## Что уже перенесено в .env

✅ **Уже используются переменные окружения:**
- База данных (PostgreSQL)
- Email сервисы (AWS SES, Mailgun)
- Robokassa настройки
- Redis кеширование
- Адрес сайта

## Что КРИТИЧЕСКИ нужно перенести в .env

### 1. SECRET_KEY ⚠️ КРИТИЧНО!
**Текущее состояние:** Хардкод в settings.py
```python
SECRET_KEY = 'django-insecure-m*t5wynyhd=2udczig6#n&0337+m=ga!p=cglnd-+srqdpq4r2'
```

**Что изменить:**
```python
SECRET_KEY = os.getenv('SECRET_KEY')
```

### 2. DEBUG ⚠️ КРИТИЧНО!
**Текущее состояние:** Хардкод True
```python
DEBUG = True
```

**Что изменить:**
```python
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
```

### 3. ALLOWED_HOSTS ⚠️ КРИТИЧНО!
**Текущее состояние:** Открыто для всех
```python
ALLOWED_HOSTS = ["*"]
```

**Что изменить:**
```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

## Дополнительные настройки для переноса в .env

### 4. Временная зона
```python
TIME_ZONE = os.getenv('TIME_ZONE', 'Asia/Yekaterinburg')
```

### 5. Язык по умолчанию
```python
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en')
```

### 6. CSRF доверенные источники
```python
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000').split(',')
```

### 7. Настройки логирования
```python
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
LOG_FILE = os.getenv('LOG_FILE', 'debug.log')
```

### 8. Настройки сессий
```python
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', '86400'))
SESSION_EXPIRE_AT_BROWSER_CLOSE = os.getenv('SESSION_EXPIRE_AT_BROWSER_CLOSE', 'False').lower() == 'true'
```

## Рекомендуемые дополнительные переменные

### Безопасность
- `SECURE_SSL_REDIRECT` - перенаправление на HTTPS
- `SECURE_HSTS_SECONDS` - HSTS заголовки
- `CSRF_COOKIE_SECURE` - безопасные CSRF куки
- `SESSION_COOKIE_SECURE` - безопасные session куки

### Мониторинг и логирование
- `SENTRY_DSN` - для мониторинга ошибок
- `LOG_LEVEL` - уровень логирования
- `ENABLE_LOGGING_TO_FILE` - включение логирования в файл

### Производительность
- `CACHE_TIMEOUT_DEFAULT` - время кеширования по умолчанию
- `DATABASE_CONN_MAX_AGE` - время жизни подключений к БД

### Интеграции
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` - для SMS
- `GOOGLE_ANALYTICS_ID` - для аналитики
- `RECAPTCHA_PUBLIC_KEY`, `RECAPTCHA_PRIVATE_KEY` - для защиты от ботов

## Предлагаемые изменения в settings.py

### settings.py (изменения)
```python
# Критически важные настройки
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Локализация
TIME_ZONE = os.getenv('TIME_ZONE', 'Asia/Yekaterinburg')
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en')

# Безопасность
CSRF_TRUSTED_ORIGINS = [
    origin.strip() 
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000').split(',')
]

# Сессии
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', '86400'))
SESSION_EXPIRE_AT_BROWSER_CLOSE = os.getenv('SESSION_EXPIRE_AT_BROWSER_CLOSE', 'False').lower() == 'true'

# Логирование
LOGGING['handlers']['file']['filename'] = os.getenv('LOG_FILE', 'debug.log')
LOGGING['handlers']['file']['level'] = os.getenv('LOG_LEVEL', 'DEBUG')
LOGGING['handlers']['console']['level'] = os.getenv('LOG_LEVEL', 'DEBUG')
```

## Структура проекта - рекомендации

### 1. Создать отдельные settings файлы
```
hms_prj/
├── settings/
│   ├── __init__.py
│   ├── base.py      # Общие настройки
│   ├── development.py  # Для разработки
│   ├── production.py   # Для продакшена
│   └── testing.py      # Для тестов
```

### 2. Добавить валидацию переменных окружения
```python
# В начало settings.py
required_env_vars = ['SECRET_KEY', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
```

### 3. Создать .env.example
Шаблон создан в файле `env_template.txt`

## Итоговые приоритеты

### 🔴 Критично (сделать немедленно)
1. SECRET_KEY в .env
2. DEBUG в .env 
3. ALLOWED_HOSTS в .env

### 🟡 Важно (сделать в ближайшее время)
4. CSRF_TRUSTED_ORIGINS в .env
5. Настройки логирования
6. Временная зона и язык

### 🟢 Желательно (для улучшения)
7. Разделение настроек по окружениям
8. Добавление мониторинга
9. Улучшение безопасности 