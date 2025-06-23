"""
Кэшированные template tags для оптимизации производительности шаблонов.
"""

from django import template
from django.core.cache import cache
from django.conf import settings
from django.db.models import Avg, Count

from hotel.models import Hotel, Review, Booking
from hotel.cache_utils import CacheKeyGenerator, CacheHelper

register = template.Library()


@register.inclusion_tag('hotel/templatetags/cached_hotel_card.html')
def cached_hotel_card(hotel, show_rating=True):
    """
    Кэшированная карточка отеля для списков.
    Кэширует рейтинг и количество отзывов.
    """
    cache_key = f"hotel_card_data:{hotel.id}"
    
    def get_hotel_card_data():
        if show_rating:
            reviews_data = Review.objects.filter(
                hotel=hotel, 
                active=True
            ).aggregate(
                avg_rating=Avg('rating'),
                count=Count('id')
            )
            
            return {
                'avg_rating': reviews_data['avg_rating'] or 0,
                'reviews_count': reviews_data['count'] or 0
            }
        return {}
    
    card_data = CacheHelper.get_or_set_complex(
        cache_key,
        get_hotel_card_data,
        timeout=settings.CACHE_TTL['hotel_reviews']
    )
    
    return {
        'hotel': hotel,
        'show_rating': show_rating,
        'avg_rating': card_data.get('avg_rating', 0),
        'reviews_count': card_data.get('reviews_count', 0)
    }


@register.simple_tag
def cached_hotel_rating(hotel_id):
    """Получает кэшированный рейтинг отеля."""
    cache_key = f"hotel_rating:{hotel_id}"
    
    def get_rating():
        return Review.objects.filter(
            hotel_id=hotel_id, 
            active=True
        ).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_rating,
        timeout=settings.CACHE_TTL['hotel_reviews']
    )


@register.simple_tag
def cached_hotel_reviews_count(hotel_id):
    """Получает кэшированное количество отзывов отеля."""
    cache_key = f"hotel_reviews_count:{hotel_id}"
    
    def get_count():
        return Review.objects.filter(
            hotel_id=hotel_id, 
            active=True
        ).count()
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_count,
        timeout=settings.CACHE_TTL['hotel_reviews']
    )


@register.simple_tag
def cached_site_stats():
    """Получает кэшированную статистику сайта."""
    cache_key = "site_statistics"
    
    def get_stats():
        return {
            'total_hotels': Hotel.objects.filter(status="Live").count(),
            'total_bookings': Booking.objects.filter(is_active=True).count(),
            'total_reviews': Review.objects.filter(active=True).count(),
            'average_rating': Review.objects.filter(active=True).aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0
        }
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_stats,
        timeout=settings.CACHE_TTL['static_content']
    )


@register.simple_tag
def cached_featured_hotels(limit=6):
    """Получает кэшированный список рекомендуемых отелей."""
    cache_key = f"featured_hotels:limit_{limit}"
    
    def get_featured_hotels():
        return Hotel.objects.filter(
            status="Live",
            featured=True
        ).prefetch_related(
            'hotelfeatures_set',
            'reviews'
        )[:limit]
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_featured_hotels,
        timeout=settings.CACHE_TTL['hotels_list']
    )


@register.simple_tag
def cached_popular_hotels(limit=6):
    """Получает кэшированный список популярных отелей по просмотрам."""
    cache_key = f"popular_hotels:limit_{limit}"
    
    def get_popular_hotels():
        return Hotel.objects.filter(
            status="Live"
        ).order_by('-views').prefetch_related(
            'hotelfeatures_set',
            'reviews'
        )[:limit]
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_popular_hotels,
        timeout=settings.CACHE_TTL['hotels_list']
    )


@register.filter
def room_price_for_date(room_type, date_str):
    """
    Получает цену номера на конкретную дату БЕЗ кэширования (для реального времени).
    Учитывает динамическое ценообразование.
    """
    if not date_str:
        return room_type.price
    
    # Убираем кэширование для динамических цен - они должны обновляться в реальном времени
    if room_type.dynamic_pricing and isinstance(room_type.dynamic_pricing, dict):
        return room_type.dynamic_pricing.get(date_str, room_type.price)
    return room_type.price


@register.inclusion_tag('hotel/templatetags/cached_room_availability.html')
def cached_room_availability(hotel_id, room_type_id, checkin_date, checkout_date):
    """
    Показывает кэшированную информацию о доступности номеров.
    """
    cache_key = CacheKeyGenerator.room_availability(
        hotel_id, 
        str(checkin_date), 
        str(checkout_date)
    )
    
    def get_availability():
        from hotel.models import Room
        from booking.models import RoomUnavailability
        from django.db.models import Q
        
        # Получаем все номера данного типа
        rooms = Room.objects.filter(
            room_type_id=room_type_id, 
            is_available=True
        )
        
        # Получаем забронированные номера
        booked_rooms = Booking.objects.filter(
            Q(check_in_date__lt=checkout_date, check_out_date__gt=checkin_date),
            is_active=True,
            payment_status__in=["paid", "processing", "pending"]
        ).values_list('room__id', flat=True)
        
        # Получаем недоступные номера
        unavailable_rooms = RoomUnavailability.objects.filter(
            Q(start_date__lt=checkout_date, end_date__gt=checkin_date)
        ).values_list('room__id', flat=True)
        
        excluded_ids = set(list(booked_rooms) + list(unavailable_rooms))
        available_rooms = rooms.exclude(id__in=excluded_ids)
        
        return {
            'total_rooms': rooms.count(),
            'available_rooms': available_rooms.count(),
            'booked_rooms': len(booked_rooms),
            'unavailable_rooms': len(unavailable_rooms)
        }
    
    availability_data = CacheHelper.get_or_set_complex(
        cache_key,
        get_availability,
        timeout=settings.CACHE_TTL['room_availability']
    )
    
    return {
        'hotel_id': hotel_id,
        'room_type_id': room_type_id,
        'availability': availability_data
    }


@register.simple_tag(takes_context=True)
def cached_user_bookings_count(context):
    """Получает количество бронирований пользователя БЕЗ кэширования (для реального времени)."""
    request = context['request']
    
    if not request.user.is_authenticated:
        return 0
    
    # Убираем кэширование для данных пользователя - они должны обновляться в реальном времени
    return Booking.objects.filter(
        user=request.user,
        is_active=True
    ).count()


@register.simple_tag
def cache_status_info():
    """Возвращает информацию о состоянии кэша для отладки."""
    try:
        from django.core.cache import caches
        
        info = {}
        for alias, cache_config in settings.CACHES.items():
            try:
                cache_instance = caches[alias]
                # Простая проверка работоспособности
                cache_instance.set('cache_test', 'test', 1)
                test_result = cache_instance.get('cache_test')
                info[alias] = 'OK' if test_result == 'test' else 'ERROR'
            except Exception as e:
                info[alias] = f'ERROR: {str(e)}'
        
        return info
    except Exception as e:
        return {'error': str(e)} 