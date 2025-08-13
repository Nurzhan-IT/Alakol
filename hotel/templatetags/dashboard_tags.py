"""
Кэшированные template tags для дашборда админки со статистикой.
"""

from django import template
from django.core.cache import cache
from django.conf import settings
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal

from hotel.models import Hotel, Review, Booking, Room, RoomType
from userauths.models import User, Profile
from hotel.cache_utils import CacheKeyGenerator, CacheHelper

register = template.Library()

# Константы для периодов фильтрации
PERIODS = {
    'today': 1,
    'week': 7,
    'month': 30,
    'year': 365,
    'all': None  # Без ограничений по времени
}

@register.simple_tag(takes_context=True)
def dashboard_stats(context, period='all'):
    """Получает основную статистику для дашборда с фильтрацией по периоду."""
    request = context['request']
    user = request.user
    is_manager = user.groups.filter(name='Manager').exists()
    
    cache_key = f"dashboard_stats:{period}:{'manager' if is_manager else 'admin'}:{user.id if is_manager else 'all'}"
    
    def get_dashboard_stats():
        now = timezone.now()
        
        # Определяем диапазон дат
        date_filter = {}
        if period != 'all' and period in PERIODS:
            start_date = now - timedelta(days=PERIODS[period])
            date_filter['created_at__gte'] = start_date
        
        # Базовые фильтры для бронирований
        booking_base = Booking.objects.filter(is_active=True)
        if date_filter:
            booking_base = booking_base.filter(**date_filter)
        
        # Фильтрация по отелям для менеджеров
        if is_manager:
            # Для менеджеров - только их отели
            user_hotels = Hotel.objects.filter(user=user, status="Live")
            booking_base = booking_base.filter(hotel__in=user_hotels)
            hotels_count = user_hotels.count()
        else:
            # Для остальных - все отели
            hotels_count = Hotel.objects.filter(status="Live").count()
            
        # Общая статистика - только оплаченные бронирования
        paid_bookings = booking_base.filter(payment_status='paid')
        total_bookings = paid_bookings.count()  # Изменено: считаем только оплаченные
        
        # Доходы в зависимости от роли пользователя
        if is_manager:
            # Для менеджеров - payment_for_hotel
            total_revenue = paid_bookings.aggregate(
                revenue=Sum('payment_for_hotel')
            )['revenue'] or Decimal('0.00')
        else:
            # Для остальных - prepayment
            total_revenue = paid_bookings.aggregate(
                revenue=Sum('prepayment')
            )['revenue'] or Decimal('0.00')
        
        # Активные пользователи (зарегистрированные в период)
        user_filter = {}
        if date_filter:
            user_filter['date_joined__gte'] = date_filter['created_at__gte']
        active_users = User.objects.filter(**user_filter).count()
        
        # Средний рейтинг отзывов
        review_filter = {}
        if date_filter:
            review_filter['date__gte'] = date_filter['created_at__gte']
        
        if is_manager:
            # Для менеджеров - только отзывы их отелей
            avg_rating = Review.objects.filter(
                hotel__user=user, 
                active=True, 
                **review_filter
            ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        else:
            # Для остальных - все отзывы
            avg_rating = Review.objects.filter(active=True, **review_filter).aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0
        
        return {
            'total_bookings': total_bookings,
            'paid_bookings': total_bookings,  # Теперь это одно и то же
            'total_revenue': total_revenue,
            'hotels_count': hotels_count,
            'active_users': active_users,
            'avg_rating': round(avg_rating, 1),
            'period': period,
            'is_manager': is_manager
        }
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_dashboard_stats,
        timeout=settings.CACHE_TTL.get('dashboard_stats', 300)  # 5 минут по умолчанию
    )

@register.simple_tag(takes_context=True)
def top_hotels_by_bookings(context, limit=5, period='all'):
    """Получает топ отелей по количеству бронирований."""
    request = context['request']
    user = request.user
    is_manager = user.groups.filter(name='Manager').exists()
    
    cache_key = f"top_hotels_bookings:{limit}:{period}:{'manager' if is_manager else 'admin'}:{user.id if is_manager else 'all'}"
    
    def get_top_hotels():
        now = timezone.now()
        
        # Определяем диапазон дат
        date_filter = {}
        if period != 'all' and period in PERIODS:
            start_date = now - timedelta(days=PERIODS[period])
            date_filter['created_at__gte'] = start_date
        
        # Базовый queryset отелей
        hotels_base = Hotel.objects.filter(status="Live")
        if is_manager:
            # Для менеджеров - только их отели
            hotels_base = hotels_base.filter(user=user)
        
        # Получаем топ отелей с учетом только оплаченных бронирований
        booking_filter = Q(
            booking__is_active=True,
            booking__payment_status='paid',  # Только оплаченные
            **{f'booking__{k}': v for k, v in date_filter.items()}
        )
        
        hotels = hotels_base.annotate(
            bookings_count=Count('booking', filter=booking_filter)
        ).order_by('-bookings_count')[:limit]
        
        # Преобразуем в список для кэширования
        result = []
        for hotel in hotels:
            result.append({
                'id': hotel.id,
                'name': hotel.name,
                'bookings_count': hotel.bookings_count,
                'slug': hotel.slug,
                'average_rating': hotel.average_rating() or 0
            })
        
        return result
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_top_hotels,
        timeout=settings.CACHE_TTL.get('dashboard_stats', 300)
    )

@register.simple_tag(takes_context=True)
def recent_bookings(context, limit=10):
    """Получает последние бронирования."""
    request = context['request']
    user = request.user
    is_manager = user.groups.filter(name='Manager').exists()
    
    cache_key = f"recent_bookings:{limit}:{'manager' if is_manager else 'admin'}:{user.id if is_manager else 'all'}"
    
    def get_recent_bookings():
        bookings_base = Booking.objects.filter(
            is_active=True,
            payment_status='paid'  # Только оплаченные
        ).select_related('user', 'hotel', 'room_type')
        
        if is_manager:
            # Для менеджеров - только бронирования их отелей
            bookings_base = bookings_base.filter(hotel__user=user)
        
        bookings = bookings_base.order_by('-created_at')[:limit]
        
        # Преобразуем в список для кэширования
        result = []
        for booking in bookings:
            result.append({
                'id': booking.id,
                'booking_id': booking.booking_id,
                'user_name': booking.full_name or (booking.user.full_name if booking.user else 'Гость'),
                'hotel_name': booking.hotel.name if booking.hotel else 'N/A',
                'total': str(booking.total),
                'payment_status': booking.payment_status,
                'created_at': booking.created_at.isoformat(),
                'check_in_date': booking.check_in_date.isoformat(),
                'check_out_date': booking.check_out_date.isoformat(),
            })
        
        return result
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_recent_bookings,
        timeout=300  # 5 минут
    )

@register.simple_tag(takes_context=True)
def daily_revenue_stats(context, days=30):
    """Получает статистику доходов по дням."""
    request = context['request']
    user = request.user
    is_manager = user.groups.filter(name='Manager').exists()
    
    cache_key = f"daily_revenue:{days}:{'manager' if is_manager else 'admin'}:{user.id if is_manager else 'all'}"
    
    def get_daily_stats():
        now = timezone.now()
        start_date = now - timedelta(days=days)
        
        # Группируем по дням
        from django.db.models.functions import TruncDate
        
        bookings_base = Booking.objects.filter(
            is_active=True,
            payment_status='paid',
            created_at__gte=start_date
        )
        
        if is_manager:
            # Для менеджеров - только их отели
            bookings_base = bookings_base.filter(hotel__user=user)
        
        # Выбираем поле для суммирования в зависимости от роли
        revenue_field = 'payment_for_hotel' if is_manager else 'prepayment'
        
        daily_data = bookings_base.annotate(
            day=TruncDate('created_at')
        ).values('day').annotate(
            revenue=Sum(revenue_field),
            bookings_count=Count('id')
        ).order_by('day')
        
        # Создаем полный список дней для заполнения пропусков
        all_days = []
        current_date = start_date.date()
        end_date = now.date()
        
        while current_date <= end_date:
            all_days.append(current_date)
            current_date += timedelta(days=1)
        
        # Создаем словарь с данными по дням
        data_by_day = {}
        for data in daily_data:
            day_key = data['day']
            data_by_day[day_key] = {
                'revenue': float(data['revenue'] or 0),
                'bookings_count': data['bookings_count']
            }
        
        # Заполняем результат, включая дни без данных
        result = []
        for day in all_days:
            day_data = data_by_day.get(day, {'revenue': 0, 'bookings_count': 0})
            result.append({
                'day': day.isoformat(),
                'day_name': day.strftime('%d.%m'),
                'day_full': day.strftime('%d %B'),
                'revenue': day_data['revenue'],
                'bookings_count': day_data['bookings_count']
            })
        
        # Если нет данных, добавляем несколько дней с нулевыми значениями для демонстрации
        if not result:
            for i in range(7):  # Последние 7 дней
                demo_date = (now - timedelta(days=i)).date()
                result.insert(0, {
                    'day': demo_date.isoformat(),
                    'day_name': demo_date.strftime('%d.%m'),
                    'day_full': demo_date.strftime('%d %B'),
                    'revenue': 0,
                    'bookings_count': 0
                })
        
        return result
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_daily_stats,
        timeout=settings.CACHE_TTL.get('dashboard_stats', 300)
    )

@register.simple_tag
def payment_status_distribution():
    """Получает распределение бронирований по статусам оплаты."""
    cache_key = "payment_status_distribution"
    
    def get_payment_distribution():
        distribution = Booking.objects.filter(
            is_active=True
        ).values('payment_status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Преобразуем в список для кэширования
        result = []
        status_names = {
            'initiated': 'Инициирована',
            'processing': 'Обрабатывается', 
            'pending': 'Ожидает',
            'paid': 'Оплачена',
            'cancelled': 'Отменена',
            'failed': 'Неудачна',
            'refunded': 'Возвращена'
        }
        
        for item in distribution:
            result.append({
                'status': item['payment_status'],
                'status_name': status_names.get(item['payment_status'], item['payment_status']),
                'count': item['count']
            })
        
        return result
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_payment_distribution,
        timeout=settings.CACHE_TTL.get('dashboard_stats', 300)
    )

@register.simple_tag
def weekly_bookings_trend(weeks=8):
    """Получает тренд бронирований по неделям."""
    cache_key = f"weekly_bookings_trend:{weeks}"
    
    def get_weekly_trend():
        now = timezone.now()
        start_date = now - timedelta(weeks=weeks)
        
        from django.db.models.functions import TruncWeek
        
        weekly_data = Booking.objects.filter(
            is_active=True,
            created_at__gte=start_date
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            bookings_count=Count('id'),
            paid_count=Count('id', filter=Q(payment_status='paid'))
        ).order_by('week')
        
        # Преобразуем в список для кэширования
        result = []
        for data in weekly_data:
            result.append({
                'week': data['week'].isoformat(),
                'week_name': f"Неделя {data['week'].strftime('%d.%m')}",
                'bookings_count': data['bookings_count'],
                'paid_count': data['paid_count']
            })
        
        return result
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_weekly_trend,
        timeout=settings.CACHE_TTL.get('dashboard_stats', 300)
    )

@register.simple_tag
def room_type_popularity():
    """Получает популярность типов номеров."""
    cache_key = "room_type_popularity"
    
    def get_room_popularity():
        room_types = RoomType.objects.annotate(
            bookings_count=Count('booking', filter=Q(booking__is_active=True)),
            revenue=Sum('booking__total', filter=Q(booking__payment_status='paid'))
        ).filter(
            bookings_count__gt=0
        ).order_by('-bookings_count')[:10]
        
        # Преобразуем в список для кэширования
        result = []
        for room_type in room_types:
            result.append({
                'id': room_type.id,
                'type': room_type.type,
                'hotel_name': room_type.hotel.name if room_type.hotel else 'N/A',
                'bookings_count': room_type.bookings_count,
                'revenue': str(room_type.revenue or Decimal('0.00')),
                'price': str(room_type.price)
            })
        
        return result
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_room_popularity,
        timeout=settings.CACHE_TTL.get('dashboard_stats', 300)
    )

@register.simple_tag(takes_context=True)
def dashboard_quick_stats(context):
    """Получает быстрые показатели для карточек."""
    request = context['request']
    user = request.user
    is_manager = user.groups.filter(name='Manager').exists()
    
    cache_key = f"dashboard_quick_stats:{'manager' if is_manager else 'admin'}:{user.id if is_manager else 'all'}"
    
    def get_quick_stats():
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Базовые фильтры
        base_filter = {'is_active': True, 'payment_status': 'paid'}
        if is_manager:
            base_filter['hotel__user'] = user
        
        # Сегодняшние показатели (только оплаченные)
        today_bookings = Booking.objects.filter(
            created_at__date=today,
            **base_filter
        ).count()
        
        # Вчерашние показатели для сравнения (только оплаченные)
        yesterday_bookings = Booking.objects.filter(
            created_at__date=yesterday,
            **base_filter
        ).count()
        
        # Общие показатели (только оплаченные)
        total_active_bookings = Booking.objects.filter(**base_filter).count()
        
        # Доходы в зависимости от роли
        revenue_field = 'payment_for_hotel' if is_manager else 'prepayment'
        total_revenue = Booking.objects.filter(**base_filter).aggregate(
            revenue=Sum(revenue_field)
        )['revenue'] or Decimal('0.00')
        
        # Рост бронирований
        growth_rate = 0
        if yesterday_bookings > 0:
            growth_rate = ((today_bookings - yesterday_bookings) / yesterday_bookings) * 100
        
        return {
            'today_bookings': today_bookings,
            'yesterday_bookings': yesterday_bookings,
            'total_bookings': total_active_bookings,
            'total_revenue': str(total_revenue),
            'growth_rate': round(growth_rate, 1),
            'avg_booking_value': str(
                total_revenue / total_active_bookings if total_active_bookings > 0 
                else Decimal('0.00')
            )
        }
    
    return CacheHelper.get_or_set_complex(
        cache_key,
        get_quick_stats,
        timeout=300  # 5 минут - часто обновляемые данные
    )

@register.filter
def format_currency(value):
    """Форматирует значение как валюту."""
    try:
        amount = Decimal(str(value))
        return f"{amount:,.2f} ₸"
    except (ValueError, TypeError):
        return "0.00 ₸"

@register.filter
def format_percentage(value):
    """Форматирует значение как процент."""
    try:
        return f"{float(value):+.1f}%"
    except (ValueError, TypeError):
        return "0.0%"

@register.simple_tag
def invalidate_dashboard_cache():
    """Инвалидирует кэш дашборда. Использовать при изменении данных."""
    cache_patterns = [
        'dashboard_stats:*',
        'top_hotels_bookings:*',
        'recent_bookings:*',
        'monthly_revenue:*',
        'payment_status_distribution',
        'weekly_bookings_trend:*',
        'room_type_popularity',
        'dashboard_quick_stats'
    ]
    
    # В Django нет встроенного способа удаления по паттерну,
    # поэтому придется удалять конкретные ключи
    keys_to_delete = []
    for pattern in cache_patterns:
        if '*' in pattern:
            # Для упрощения удаляем основные варианты
            base_pattern = pattern.replace('*', '')
            for period in ['all', 'today', 'week', 'month', 'year']:
                keys_to_delete.append(f"{base_pattern}{period}")
            for i in range(1, 21):  # Лимиты от 1 до 20
                keys_to_delete.append(f"{base_pattern}{i}")
        else:
            keys_to_delete.append(pattern)
    
    cache.delete_many(keys_to_delete)
    return f"Инвалидировано {len(keys_to_delete)} ключей кэша"