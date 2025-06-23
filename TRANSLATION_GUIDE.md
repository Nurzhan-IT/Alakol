# Руководство по многоязычным переводам

## Что было сделано

Добавлен многоязычный перевод для сообщений `messages.error`, `messages.success`, `messages.warning` на три языка:
- Английский (en)
- Русский (ru) 
- Казахский (kk)

## Обновленные файлы

### Python файлы с переводами:
- `booking/admin.py` - добавлен импорт `gettext_lazy`
- `booking/views.py` - все сообщения переведены
- `hotel/decorators.py` - все сообщения переведены  
- `hotel/views.py` - все сообщения переведены
- `user_dashboard/views.py` - все сообщения переведены
- `userauths/views.py` - все сообщения переведены

### Файлы переводов:
- `locale/en/LC_MESSAGES/django.po` - английский (создан)
- `locale/ru/LC_MESSAGES/django.po` - русский (обновлен)
- `locale/kk/LC_MESSAGES/django.po` - казахский (обновлен)

## Как компилировать переводы

После внесения изменений в .po файлы, необходимо скомпилировать их в .mo файлы:

```bash
# Для русского языка
cd locale/ru/LC_MESSAGES
django-admin compilemessages

# Для казахского языка  
cd locale/kk/LC_MESSAGES
django-admin compilemessages

# Для английского языка
cd locale/en/LC_MESSAGES
django-admin compilemessages

# Или для всех языков сразу из корня проекта
django-admin compilemessages
```

## Как обновить переводы

Если добавлены новые строки для перевода:

```bash
# Извлечь все строки для перевода
django-admin makemessages -l ru
django-admin makemessages -l kk
django-admin makemessages -l en

# Обновить существующие переводы
django-admin makemessages -l ru --update
django-admin makemessages -l kk --update  
django-admin makemessages -l en --update
```

## Использование в коде

Все сообщения теперь используют `gettext_lazy` для переводов:

```python
from django.utils.translation import gettext_lazy as _

# Вместо:
messages.error(request, "Hotel not found.")

# Используется:
messages.error(request, _("Hotel not found."))

# Для сообщений с параметрами:
messages.error(request, _("Room %(room_number)s is not available") % {'room_number': room_number})
```

## Настройки локализации

Убедитесь, что в `settings.py` настроены:

```python
USE_I18N = True
USE_L10N = True

LANGUAGES = [
    ('en', 'English'),
    ('ru', 'Русский'),  
    ('kk', 'Қазақша'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]
```

## Переведенные категории сообщений

1. **Сообщения о бронировании**
   - Отсутствие выбранных номеров
   - Недостающие обязательные поля
   - Отель не найден
   - Тип номера недоступен

2. **Сообщения о доступности номеров**
   - Номер недоступен для бронирования
   - Номер уже забронирован
   - Номер отмечен как недоступный

3. **Сообщения об оплате**
   - Ошибки создания платежа
   - Ошибки верификации платежа
   - Успешная оплата
   - Доступ к квитанции

4. **Сообщения аутентификации**
   - Вход в систему
   - Регистрация
   - Выход из системы
   - Ошибки входа

5. **Сообщения профиля**
   - Обновление профиля

Все сообщения поддерживают параметризацию для динамического содержимого.
