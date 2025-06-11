# РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ КОДА DJANGO

# 1. Добавить кэширование в settings.py
CACHES_OPTIMIZATION = """
# Добавить в hms_prj/settings.py

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 часа
"""

# 2. Оптимизация представлений с кэшированием
VIEWS_OPTIMIZATION = """
# В hotel/views.py добавить:
from django.views.decorators.cache import cache_page
from django.core.cache import cache

@cache_page(60 * 15)  # Кэш на 15 минут
def index(request):
    # Существующий код...

def hotel_detail(request, slug):
    # Кэшировать дорогие запросы
    cache_key = f'hotel_detail_{slug}'
    cached_data = cache.get(cache_key)
    
    if not cached_data:
        hotel = get_object_or_404(
            Hotel.objects.select_related('user')
                         .prefetch_related(
                             'roomtype_set__roomtype_gallery',
                             'hotelgallery_set',
                             'hotelfeatures_set',
                             'reviews__user'
                         ), 
            status="Live", 
            slug=slug
        )
        cache.set(cache_key, hotel, 60 * 30)  # 30 минут
    else:
        hotel = cached_data
"""

# 3. Оптимизация запросов к базе данных
DATABASE_OPTIMIZATION = """
# В hotel/models.py добавить индексы:

class Hotel(models.Model):
    # ... существующие поля ...
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'featured']),
            models.Index(fields=['slug']),
            models.Index(fields=['date']),
        ]

class Booking(models.Model):
    # ... существующие поля ...
    
    class Meta:
        indexes = [
            models.Index(fields=['payment_status']),
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['hotel', 'payment_status']),
            models.Index(fields=['user', 'payment_status']),
        ]
"""

# 4. Использование bulk операций
BULK_OPERATIONS = """
# Вместо циклов использовать bulk операции:

# ПЛОХО:
for room in rooms:
    room.is_available = False
    room.save()

# ХОРОШО:
Room.objects.filter(id__in=room_ids).update(is_available=False)

# Или для создания:
Room.objects.bulk_create([
    Room(hotel=hotel, room_type=room_type, room_number=num)
    for num in range(1, 51)
])
"""

# 5. Асинхронные задачи
ASYNC_TASKS = """
# В hotel/tasks.py (создать новый файл):
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_confirmation_email(booking_id):
    # Отправка email в фоновом режиме
    booking = Booking.objects.get(id=booking_id)
    send_mail(
        'Подтверждение бронирования',
        f'Ваше бронирование #{booking.booking_id} подтверждено',
        'noreply@alakol.com',
        [booking.email],
    )

# В views.py вызывать:
# send_booking_confirmation_email.delay(booking.id)
"""

print("Эффект: Увеличение RPS на 100-150%")
print("Время внедрения: 2-3 дня")
print("Сложность: Средняя")