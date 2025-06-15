from django.utils import timezone
from django.db.models import Q, Prefetch
from hotel.models import Booking, Room

def handle_bookings_payment_status_processing_to_unpaid():
    """
    Находит и отменяет просроченные бронирования со статусом 'Processing'.
    Использует оптимизированные запросы для предотвращения проблемы N+1.
    """
    try:
        # Используем один запрос для выборки и обновления
        expired_bookings = Booking.objects.filter(
            payment_status='processing',
            expires_at__lt=timezone.now()
        )
        # Получаем ID бронирований для логирования (при необходимости)
        booking_ids = list(expired_bookings.values_list('booking_id', flat=True)[:100])
        
        # Выполняем массовое обновление одним запросом
        count = expired_bookings.update(payment_status='unpaid')
        
        if count > 0:
            print(f"unpaid {count} expired bookings: {', '.join(booking_ids[:5])}{'...' if len(booking_ids) > 5 else ''}")
        return f"unpaid {count} expired bookings."
    except Exception as e:
        print(f"Error cleaning expired bookings: {str(e)}")
        return f"Error: {str(e)}"

def get_bookings_with_related_data(status=None, limit=100):
    """
    Получает бронирования со связанными данными одним запросом.
    Демонстрирует использование select_related и prefetch_related для устранения проблемы N+1.
    
    Args:
        status: Опциональный фильтр по статусу бронирования
        limit: Ограничение количества результатов
    
    Returns:
        QuerySet бронирований со связанными данными
    """
    # Базовый запрос
    query = Booking.objects.select_related(
        'hotel',  # Загружаем отель одним запросом
        'room_type',  # Загружаем тип номера одним запросом
        'user'  # Загружаем пользователя одним запросом
    ).prefetch_related(
        # Эффективно загружаем все номера для каждого бронирования
        Prefetch(
            'room',
            queryset=Room.objects.select_related('room_type')
        )
    )
    
    # Применяем фильтр по статусу, если указан
    if status:
        query = query.filter(payment_status=status)
    
    # Ограничиваем количество результатов
    return query[:limit]  