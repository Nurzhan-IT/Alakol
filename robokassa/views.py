from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Prefetch
from django.conf import settings
from django.utils import timezone
import logging

from hotel.models import Booking, Hotel, Room

logger = logging.getLogger(__name__)

@csrf_exempt
def robokassa_result(request):
    """
    Обработчик для Result URL Robokassa.
    Оптимизирует запросы к БД с использованием select_related.
    """
    if request.method != 'POST':
        return HttpResponse("Only POST requests are accepted", status=405)
    
    try:
        # Извлекаем ID заказа из POST-параметров
        order_id = request.POST.get('InvId')
        if not order_id:
            logger.error("Missing InvId parameter")
            return HttpResponse("Error: Missing InvId", status=400)
        
        # Получаем бронирование вместе со связанными данными за один запрос
        booking = get_object_or_404(
            Booking.objects.select_related('hotel', 'user', 'room_type'),
            id=order_id
        )
        
        # Обновляем статус бронирования
        booking.payment_status = "paid"
        booking.save(update_fields=['payment_status'])
        
        logger.info(f"Payment confirmed for booking {booking.booking_id}, Robokassa InvId: {order_id}")
        return HttpResponse("OK" + str(booking.booking_id))
        
    except Exception as e:
        logger.error(f"Error processing Robokassa result: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)

@csrf_exempt
def robokassa_success(request):
    """
    Обработчик для Success URL Robokassa.
    Использует оптимизированные запросы для предотвращения проблемы N+1.
    """
    try:
        # Извлекаем ID заказа из GET-параметров
        order_id = request.GET.get('InvId')
        if not order_id:
            logger.error("Missing InvId parameter")
            return redirect('/')
        
        # Получаем бронирование вместе со связанными данными и номерами за один запрос
        booking = get_object_or_404(
            Booking.objects.select_related('hotel', 'user', 'room_type')
                           .prefetch_related(
                               Prefetch(
                                   'room',
                                   queryset=Room.objects.select_related('room_type')
                               )
                           ),
            id=order_id
        )
        
        # Оптимизация: проверяем статус без дополнительных запросов
        if booking.payment_status != "paid":
            booking.payment_status = "paid"
            booking.save(update_fields=['payment_status'])
        
        context = {
            "booking": booking,
            "rooms": list(booking.room.all()),  # Используем prefetch_related данные
        }
        
        logger.info(f"Showing success page for booking {booking.booking_id}")
        return render(request, "hotel/payment_success.html", context)
        
    except Exception as e:
        logger.error(f"Error processing success page: {str(e)}")
        return redirect('/')

@csrf_exempt
def robokassa_fail(request):
    """
    Обработчик для Fail URL Robokassa.
    Использует оптимизированные запросы для предотвращения проблемы N+1.
    """
    try:
        # Извлекаем ID заказа из GET-параметров
        order_id = request.GET.get('InvId')
        if not order_id:
            logger.error("Missing InvId parameter")
            return redirect('/')
        
        # Получаем бронирование с минимальным набором необходимых связанных данных
        booking = get_object_or_404(
            Booking.objects.select_related('hotel'),
            id=order_id
        )
        
        # Оптимизация: обновляем только нужное поле
        booking.payment_status = "failed"
        booking.save(update_fields=['payment_status'])
        
        context = {
            "booking": booking,
        }
        
        logger.info(f"Showing failure page for booking {booking.booking_id}")
        return render(request, "hotel/payment_failed.html", context)
        
    except Exception as e:
        logger.error(f"Error processing failure page: {str(e)}")
        return redirect('/')

def get_active_bookings_for_hotel(hotel_slug, start_date=None, end_date=None):
    """
    Получает все активные бронирования для отеля в заданном диапазоне дат.
    Демонстрирует использование оптимизированных запросов.
    
    Args:
        hotel_slug: Slug отеля
        start_date: Начальная дата (по умолчанию - сегодня)
        end_date: Конечная дата (по умолчанию - через 30 дней)
    
    Returns:
        QuerySet бронирований с предварительно загруженными связанными данными
    """
    # Устанавливаем значения по умолчанию для дат
    if start_date is None:
        start_date = timezone.now().date()
    if end_date is None:
        end_date = start_date + timezone.timedelta(days=30)
    
    # Получаем отель с предварительной загрузкой типов номеров
    hotel = get_object_or_404(
        Hotel.objects.prefetch_related('roomtype_set'),
        slug=hotel_slug
    )
    
    # Получаем все активные бронирования в указанном диапазоне дат
    # с предварительной загрузкой связанных данных
    bookings = Booking.objects.select_related(
        'hotel', 'user', 'room_type'
    ).prefetch_related(
        Prefetch(
            'room',
            queryset=Room.objects.select_related('room_type')
        )
    ).filter(
        hotel=hotel,
        is_active=True,
        payment_status__in=['paid', 'processing'],
        check_in_date__lte=end_date,
        check_out_date__gte=start_date
    ).order_by('check_in_date')
    
    return bookings
