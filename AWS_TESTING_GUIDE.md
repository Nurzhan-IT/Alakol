# Руководство по тестированию AWS SES

## Быстрый старт

### 1. Настройка переменных окружения

Добавьте в файл `.env`:

```bash
# AWS SES Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=ap-southeast-1

# Email Configuration
DEFAULT_FROM_EMAIL=noreply@your-domain.com
```

### 2. Команды для тестирования

#### Базовый тест AWS SES
```bash
python manage.py test_aws_ses --test-basic --test-email 12farit21@gmail.com
```

#### Тест с конкретным бронированием
```bash
python manage.py test_aws_ses --booking-id bxeyyffnrh
```

#### Тест с последним оплаченным бронированием
```bash
python manage.py test_aws_ses
```

## Проверка работы в production

### 1. Мониторинг логов Django

Следите за сообщениями в логах:

```
INFO: Email успешно отправлен на user@example.com. MessageId: 01000...
INFO: Успешно отправлен email пользователю для бронирования abc123
INFO: Успешно отправлен email отелю для бронирования abc123
```

### 2. Проверка в AWS Console

1. Откройте AWS SES Console
2. Перейдите в раздел "Sending statistics"
3. Проверьте количество отправленных и доставленных писем

### 3. Тестирование через Robokassa Result URL

Для полного тестирования используйте тестовый платеж через Robokassa. После успешной оплаты должны отправиться оба email.

## Возможные проблемы и решения

### Ошибка: "The AWS Access Key Id you provided does not exist"
- Проверьте правильность AWS_ACCESS_KEY_ID
- Убедитесь, что ключ активен в AWS Console

### Ошибка: "Email address not verified"
- Подтвердите email адрес в AWS SES Console
- Для production выйдите из режима песочницы

### Ошибка: "Message rejected: Email address is not verified"
- В режиме песочницы можно отправлять только на подтвержденные адреса
- Подтвердите адрес получателя или выйдите из песочницы

### Fallback на старый способ отправки
Если AWS SES недоступен, система автоматически использует настроенный EMAIL_BACKEND:

```
WARNING: AWS SES credentials не настроены, email не отправлены
```

## Структура email

### Email пользователю
- **Тема**: Спасибо за бронирование с eKol! - ID: #[booking_id]
- **Содержание**: 
  - Благодарность за бронирование
  - Детали бронирования с русскими датами (например: "15 января 2025 г. (среда)")
  - **Раздел "Документы для заселения"** с инструкциями
  - Кнопка "Скачать чек бронирования"
  - Многоязычные ссылки на чеки (🇷🇺 🇰🇿 🇬🇧)
- **Стиль**: Профессиональный дизайн с выделенным разделом для чека

### Email отелю
- **Тема**: Новое подтверждение бронирования - ID: #[booking_id]
- **Содержание**: 
  - Уведомление о новом госте
  - Детали бронирования с русскими датами
  - Контактная информация гостя
- **Стиль**: Деловой стиль с важной информацией

## Безопасность

⚠️ **Важно**: Никогда не коммитьте реальные AWS credentials в репозиторий!

### Правильная настройка IAM

Создайте пользователя только с правами SES:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*"
        }
    ]
}
```

## Полная схема тестирования

1. **Настройка AWS SES**
   - Создание аккаунта AWS
   - Подтверждение домена/email
   - Создание IAM пользователя

2. **Настройка проекта**
   - Добавление переменных в .env
   - Проверка настроек Django

3. **Базовое тестирование**
   - Тест отправки простого email
   - Проверка логов

4. **Интеграционное тестирование**
   - Тест с реальным бронированием
   - Проверка через Robokassa

5. **Production тестирование**
   - Выход из песочницы AWS SES
   - Мониторинг в реальных условиях

## Команды для разработчиков

### Проверка настроек
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(f"AWS_REGION: {settings.AWS_REGION}")
>>> print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
```

### Создание тестового бронирования
```python
from hotel.models import Booking, Hotel, RoomType
from django.contrib.auth import get_user_model
from datetime import date, timedelta

# Создать тестовое бронирование для тестирования email
```

Система готова к использованию! 🚀 