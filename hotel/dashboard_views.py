"""
Views для дашборда администратора с экспортом данных.
"""

import csv
import json
from datetime import datetime, timedelta
from decimal import Decimal

from django.http import HttpResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hotel.models import Hotel, Review, Booking, Room, RoomType
from userauths.models import User
from hotel.templatetags.dashboard_tags import (
    dashboard_stats, top_hotels_by_bookings, recent_bookings,
    daily_revenue_stats, payment_status_distribution,
    weekly_bookings_trend, room_type_popularity, dashboard_quick_stats
)


@staff_member_required
@require_http_methods(["GET"])
def export_dashboard_csv(request):
    """Экспорт статистики дашборда в CSV формате."""
    
    # Получаем параметры из запроса
    period = request.GET.get('period', 'all')
    export_type = request.GET.get('type', 'main_stats')
    
    # Создаем HTTP ответ с типом CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="dashboard_export_{export_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    # Добавляем BOM для корректного отображения кириллицы в Excel
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    if export_type == 'main_stats':
        # Экспорт основной статистики
        from hotel.templatetags.dashboard_tags import dashboard_stats
        
        # Создаем фиктивный context для template tag
        class FakeRequest:
            def __init__(self, user):
                self.user = user
        
        fake_context = {'request': FakeRequest(request.user)}
        stats = dashboard_stats(fake_context, period)
        
        writer.writerow(['Основная статистика дашборда'])
        writer.writerow(['Период:', _get_period_name(period)])
        writer.writerow(['Дата экспорта:', timezone.now().strftime('%d.%m.%Y %H:%M')])
        writer.writerow([])
        
        writer.writerow(['Показатель', 'Значение'])
        writer.writerow(['Всего бронирований', stats.get('total_bookings', 0)])
        writer.writerow(['Оплаченных бронирований', stats.get('paid_bookings', 0)])
        writer.writerow(['Общий доход', f"{stats.get('total_revenue', 0)} ₸"])
        writer.writerow(['Количество отелей', stats.get('hotels_count', 0)])
        writer.writerow(['Активные пользователи', stats.get('active_users', 0)])
        writer.writerow(['Средний рейтинг', stats.get('avg_rating', 0)])
    
    elif export_type == 'top_hotels':
        # Экспорт топ отелей
        from hotel.templatetags.dashboard_tags import top_hotels_by_bookings
        
        # Создаем фиктивный context для template tag
        class FakeRequest:
            def __init__(self, user):
                self.user = user
        
        fake_context = {'request': FakeRequest(request.user)}
        hotels = top_hotels_by_bookings(fake_context, limit=10, period=period)
        
        writer.writerow(['Топ отелей по бронированиям'])
        writer.writerow(['Период:', _get_period_name(period)])
        writer.writerow(['Дата экспорта:', timezone.now().strftime('%d.%m.%Y %H:%M')])
        writer.writerow([])
        
        writer.writerow(['Место', 'Название отеля', 'Количество бронирований', 'Средний рейтинг'])
        for i, hotel in enumerate(hotels, 1):
            writer.writerow([
                i,
                hotel.get('name', 'N/A'),
                hotel.get('bookings_count', 0),
                hotel.get('average_rating', 0)
            ])
    
    elif export_type == 'daily_revenue':
        # Экспорт дневных доходов
        from hotel.templatetags.dashboard_tags import daily_revenue_stats
        
        # Создаем фиктивный context для template tag
        class FakeRequest:
            def __init__(self, user):
                self.user = user
        
        fake_context = {'request': FakeRequest(request.user)}
        daily_data = daily_revenue_stats(fake_context, days=30)
        
        writer.writerow(['Дневная статистика доходов'])
        writer.writerow(['Дата экспорта:', timezone.now().strftime('%d.%m.%Y %H:%M')])
        writer.writerow([])
        
        writer.writerow(['День', 'Доходы (₸)', 'Количество бронирований'])
        for data in daily_data:
            writer.writerow([
                data.get('day_name', 'N/A'),
                data.get('revenue', '0'),
                data.get('bookings_count', 0)
            ])
    
    elif export_type == 'payment_status':
        # Экспорт статусов оплаты
        payment_data = payment_status_distribution()
        
        writer.writerow(['Распределение статусов оплаты'])
        writer.writerow(['Дата экспорта:', timezone.now().strftime('%d.%m.%Y %H:%M')])
        writer.writerow([])
        
        writer.writerow(['Статус', 'Название', 'Количество'])
        for data in payment_data:
            writer.writerow([
                data.get('status', 'N/A'),
                data.get('status_name', 'N/A'),
                data.get('count', 0)
            ])
    
    elif export_type == 'recent_bookings':
        # Экспорт последних бронирований
        from hotel.templatetags.dashboard_tags import recent_bookings
        
        # Создаем фиктивный context для template tag
        class FakeRequest:
            def __init__(self, user):
                self.user = user
        
        fake_context = {'request': FakeRequest(request.user)}
        bookings = recent_bookings(fake_context, limit=50)
        
        writer.writerow(['Последние бронирования'])
        writer.writerow(['Дата экспорта:', timezone.now().strftime('%d.%m.%Y %H:%M')])
        writer.writerow([])
        
        writer.writerow([
            'ID бронирования', 'Пользователь', 'Отель', 'Сумма (₸)',
            'Статус оплаты', 'Дата создания', 'Дата заезда', 'Дата выезда'
        ])
        for booking in bookings:
            writer.writerow([
                booking.get('booking_id', 'N/A'),
                booking.get('user_name', 'N/A'),
                booking.get('hotel_name', 'N/A'),
                booking.get('total', '0'),
                booking.get('payment_status', 'N/A'),
                _parse_datetime(booking.get('created_at')),
                booking.get('check_in_date', 'N/A'),
                booking.get('check_out_date', 'N/A')
            ])
    
    elif export_type == 'room_popularity':
        # Экспорт популярности типов номеров
        room_data = room_type_popularity()
        
        writer.writerow(['Популярность типов номеров'])
        writer.writerow(['Дата экспорта:', timezone.now().strftime('%d.%m.%Y %H:%M')])
        writer.writerow([])
        
        writer.writerow(['Тип номера', 'Отель', 'Количество бронирований', 'Доходы (₸)', 'Цена за номер (₸)'])
        for room in room_data:
            writer.writerow([
                room.get('type', 'N/A'),
                room.get('hotel_name', 'N/A'),
                room.get('bookings_count', 0),
                room.get('revenue', '0'),
                room.get('price', '0')
            ])
    
    else:
        # Комплексный экспорт всей статистики
        writer.writerow(['Полная статистика дашборда'])
        writer.writerow(['Период:', _get_period_name(period)])
        writer.writerow(['Дата экспорта:', timezone.now().strftime('%d.%m.%Y %H:%M')])
        writer.writerow([])
        
        # Основная статистика
        from hotel.templatetags.dashboard_tags import dashboard_stats
        
        # Создаем фиктивный context для template tag
        class FakeRequest:
            def __init__(self, user):
                self.user = user
        
        fake_context = {'request': FakeRequest(request.user)}
        stats = dashboard_stats(fake_context, period)
        writer.writerow(['ОСНОВНАЯ СТАТИСТИКА'])
        writer.writerow(['Показатель', 'Значение'])
        writer.writerow(['Всего бронирований', stats.get('total_bookings', 0)])
        writer.writerow(['Оплаченных бронирований', stats.get('paid_bookings', 0)])
        writer.writerow(['Общий доход', f"{stats.get('total_revenue', 0)} ₸"])
        writer.writerow(['Количество отелей', stats.get('hotels_count', 0)])
        writer.writerow(['Активные пользователи', stats.get('active_users', 0)])
        writer.writerow(['Средний рейтинг', stats.get('avg_rating', 0)])
        writer.writerow([])
        
        # Топ отелей
        from hotel.templatetags.dashboard_tags import top_hotels_by_bookings
        
        # Создаем фиктивный context для template tag
        class FakeRequest:
            def __init__(self, user):
                self.user = user
        
        fake_context = {'request': FakeRequest(request.user)}
        hotels = top_hotels_by_bookings(fake_context, limit=5, period=period)
        writer.writerow(['ТОП-5 ОТЕЛЕЙ'])
        writer.writerow(['Место', 'Название', 'Бронирования', 'Рейтинг'])
        for i, hotel in enumerate(hotels, 1):
            writer.writerow([
                i,
                hotel.get('name', 'N/A'),
                hotel.get('bookings_count', 0),
                hotel.get('average_rating', 0)
            ])
    
    return response


@staff_member_required
@require_http_methods(["GET"])
def export_dashboard_json(request):
    """Экспорт статистики дашборда в JSON формате для API или импорта."""
    
    period = request.GET.get('period', 'all')
    export_type = request.GET.get('type', 'full')
    
    data = {
        'export_info': {
            'period': period,
            'period_name': _get_period_name(period),
            'export_date': timezone.now().isoformat(),
            'export_type': export_type
        }
    }
    
    if export_type == 'full' or export_type == 'stats':
        data['main_stats'] = dashboard_stats(period)
        data['quick_stats'] = dashboard_quick_stats()
    
    if export_type == 'full' or export_type == 'hotels':
        data['top_hotels'] = top_hotels_by_bookings(limit=10, period=period)
    
    if export_type == 'full' or export_type == 'bookings':
        data['recent_bookings'] = recent_bookings(limit=20)
    
    if export_type == 'full' or export_type == 'revenue':
        data['monthly_revenue'] = monthly_revenue_stats(months=12)
        data['weekly_trend'] = weekly_bookings_trend(weeks=8)
    
    if export_type == 'full' or export_type == 'analytics':
        data['payment_distribution'] = payment_status_distribution()
        data['room_popularity'] = room_type_popularity()
    
    # Создаем JSON response
    response = JsonResponse(data, json_dumps_params={
        'ensure_ascii': False,
        'indent': 2,
        'default': _json_serializer
    })
    
    # Устанавливаем заголовки для скачивания файла
    if request.GET.get('download', 'false').lower() == 'true':
        filename = f"dashboard_export_{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def invalidate_dashboard_cache(request):
    """Принудительная инвалидация кэша дашборда."""
    
    from hotel.templatetags.dashboard_tags import invalidate_dashboard_cache
    
    try:
        result = invalidate_dashboard_cache()
        return JsonResponse({
            'success': True,
            'message': 'Кэш дашборда успешно инвалидирован',
            'details': result
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка при инвалидации кэша: {str(e)}'
        }, status=500)


@staff_member_required
@require_http_methods(["GET"])
def dashboard_api_stats(request):
    """API endpoint для получения статистики дашборда в реальном времени."""
    
    period = request.GET.get('period', 'all')
    
    try:
        from hotel.templatetags.dashboard_tags import (
            dashboard_stats, dashboard_quick_stats, 
            top_hotels_by_bookings, recent_bookings
        )
        
        # Создаем фиктивный context для template tags
        class FakeRequest:
            def __init__(self, user):
                self.user = user
        
        fake_context = {'request': FakeRequest(request.user)}
        
        data = {
            'main_stats': dashboard_stats(fake_context, period),
            'quick_stats': dashboard_quick_stats(fake_context),
            'top_hotels': top_hotels_by_bookings(fake_context, limit=5, period=period),
            'recent_bookings': recent_bookings(fake_context, limit=10),
            'last_updated': timezone.now().isoformat()
        }
        
        return JsonResponse(data, json_dumps_params={
            'ensure_ascii': False,
            'default': _json_serializer
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Ошибка получения статистики: {str(e)}'
        }, status=500)


def _get_period_name(period):
    """Возвращает читаемое название периода."""
    periods = {
        'today': 'Сегодня',
        'week': 'Последние 7 дней',
        'month': 'Последние 30 дней',
        'year': 'Последние 365 дней',
        'all': 'Все время'
    }
    return periods.get(period, 'Все время')


def _parse_datetime(date_str):
    """Парсит datetime строку в читаемый формат."""
    if not date_str:
        return 'N/A'
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%d.%m.%Y %H:%M')
    except (ValueError, AttributeError):
        return str(date_str)


def _json_serializer(obj):
    """Кастомный JSON сериализатор для специальных типов данных."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime,)):
        return obj.isoformat()
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")