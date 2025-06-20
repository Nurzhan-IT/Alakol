from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.models import Q, Prefetch, Count
from django.core.cache import cache
from django.conf import settings

from hotel.models import Hotel, Room, Booking, RoomServices, HotelGallery, HotelFeatures, RoomType
from hotel.views import calculate_total_price  # Импортируем функцию для расчета динамических цен
from hotel.cache_utils import CacheKeyGenerator, CacheInvalidator
from booking.cache_utils import BookingCacheHelper, cache_booking_function

from datetime import datetime, timedelta
from decimal import Decimal
import json

from django.contrib import messages
import logging
logger = logging.getLogger(__name__)

@cache_booking_function(
    key_func=lambda request: (
        f"room_availability_check:"
        f"{request.POST.get('hotel-id', '')}:"
        f"{request.POST.get('room-type-id', request.POST.get('room-type', ''))}:"
        f"{request.POST.get('checkin', '')}:"
        f"{request.POST.get('checkout', '')}"
        if request.method == "POST" else "invalid_method"
    ),
    timeout=settings.CACHE_TTL.get('booking_availability_check', 120)
)
def check_room_availability(request):
    if request.method == "POST":
        id = request.POST.get("hotel-id")
        checkin = request.POST.get("checkin")
        checkout = request.POST.get("checkout")
        adult = request.POST.get("adult")
        children = request.POST.get("children")
        room_type = request.POST.get("room-type", "")
        room_type_id = request.POST.get("room-type-id", "")
        
        # Проверяем кэш для данного запроса
        cached_result = BookingCacheHelper.get_cached_booking_availability_check(
            int(id) if id else 0,
            int(room_type_id) if room_type_id else 0,
            checkin or "",
            checkout or ""
        )
        
        if cached_result and not settings.DEBUG:
            logger.debug(f"Возвращаем кэшированный результат проверки доступности")
            # Если есть кэшированный результат, возвращаем его
            return cached_result
        
        # Подробное логирование всех параметров запроса
        logger.info(f"Получен POST запрос с параметрами: hotel-id={id}, checkin={checkin}, checkout={checkout}, "
                   f"adult={adult}, children={children}, room-type={room_type}, room-type-id={room_type_id}")
        
        print(f"POST data: hotel-id={id}, checkin={checkin}, checkout={checkout}, adult={adult}, children={children}, room-type={room_type}, room-type-id={room_type_id}")
        
        # Проверяем, не является ли room-type пустой строкой
        if room_type == "":
            room_type = None
            
        # Проверяем, не является ли room-type-id пустой строкой
        if room_type_id == "":
            room_type_id = None
            
        missing_params = []
        if not id:
            missing_params.append("hotel-id")
        if not checkin:
            missing_params.append("checkin")
        if not checkout:
            missing_params.append("checkout")
        if not adult:
            missing_params.append("adult")
        if not children:
            missing_params.append("children")
        # Проверяем наличие хотя бы одного из параметров room-type или room-type-id
        if not room_type and not room_type_id:
            missing_params.append("room-type или room-type-id")
            
        if missing_params:
            logger.error(f"Отсутствуют обязательные параметры: {', '.join(missing_params)}")
            messages.error(request, f"Пожалуйста, заполните все обязательные поля: {', '.join(missing_params)}")
            return redirect("hotel:index")

        try:
            # Оптимизация: используем select_related для получения связанных данных отеля за один запрос
            hotel = Hotel.objects.select_related().get(status="Live", id=id)
        except Hotel.DoesNotExist:
            logger.error(f"Hotel with id={id} not found")
            messages.error(request, "Отель не найден.")
            return redirect("hotel:index")

        try:
            # Если room_type совпадает с room_type_id, значит это ID, а не slug
            if room_type and room_type.isdigit() and room_type_id and room_type == room_type_id:
                logger.info(f"room-type содержит ID типа номера: {room_type}")
                try:
                    room_type_obj = RoomType.objects.select_related('hotel').get(hotel=hotel, id=room_type)
                    logger.info(f"Найден тип номера по id (из поля room-type): {room_type}")
                except RoomType.DoesNotExist:
                    logger.error(f"RoomType с id={room_type} не найден")
                    messages.error(request, "Выбранный тип номера недоступен. Пожалуйста, выберите другой тип номера.")
                    return redirect("hotel:detail", slug=hotel.slug)
            # Иначе приоритет поиска: сначала по ID, затем по slug
            elif room_type_id:
                try:
                    room_type_obj = RoomType.objects.select_related('hotel').get(hotel=hotel, id=room_type_id)
                    logger.info(f"Найден тип номера по id: {room_type_id}")
                except (RoomType.DoesNotExist, ValueError):
                    # Если не удалось найти по ID, пробуем найти по slug
                    if room_type:
                        room_type_obj = RoomType.objects.select_related('hotel').get(hotel=hotel, slug=room_type)
                        logger.info(f"Найден тип номера по slug: {room_type}")
                    else:
                        raise RoomType.DoesNotExist("Не найден тип номера ни по id, ни по slug")
            elif room_type:
                # Пробуем сначала как ID, потом как slug
                try:
                    if room_type.isdigit():
                        room_type_obj = RoomType.objects.select_related('hotel').get(hotel=hotel, id=room_type)
                        logger.info(f"Найден тип номера по id (из поля room-type): {room_type}")
                    else:
                        room_type_obj = RoomType.objects.select_related('hotel').get(hotel=hotel, slug=room_type)
                        logger.info(f"Найден тип номера по slug: {room_type}")
                except (RoomType.DoesNotExist, ValueError):
                    raise RoomType.DoesNotExist(f"Не найден тип номера: {room_type}")
            else:
                raise RoomType.DoesNotExist("Не предоставлены данные для поиска типа номера")
                
        except RoomType.DoesNotExist as e:
            logger.error(f"RoomType not found: {str(e)}, hotel id={id}, room-type={room_type}, room-type-id={room_type_id}")
            messages.error(request, "Выбранный тип номера недоступен. Пожалуйста, выберите другой тип номера.")
            return redirect("hotel:detail", slug=hotel.slug)

        # Сохраняем данные о датах поиска в новой сессии room_type_search_dates
        if 'room_type_search_dates' not in request.session:
            request.session['room_type_search_dates'] = {}
        
        request.session['room_type_search_dates'] = {
            'checkin': checkin,
            'checkout': checkout,
            'adult': adult,
            'children': children,
        }
        print("room_type_search_dates === ", request.session['room_type_search_dates'])
        request.session.modified = True
        
        logger.info(f"Redirecting to room_type_detail with hotel_slug={hotel.slug}, room_type_slug={room_type_obj.slug}")
        url = reverse("hotel:room_type_detail", args=[hotel.slug, room_type_obj.slug])
        url_with_params = f"{url}?hotel-id={id}&checkin={checkin}&checkout={checkout}&adult={adult}&children={children}&room_type={room_type_obj.slug}"
        response = HttpResponseRedirect(url_with_params)
        
        # Кэшируем результат успешной проверки доступности
        if id and room_type_id and checkin and checkout:
            BookingCacheHelper.cache_booking_availability_check(
                int(id), int(room_type_id), checkin, checkout, {
                    'success': True,
                    'redirect_url': url_with_params,
                    'hotel_slug': hotel.slug,
                    'room_type_slug': room_type_obj.slug
                }
            )
        
        return response

    else:
        logger.warning("Non-POST request to check_room_availability")
        return redirect("hotel:index")
    
def booking_data(request, slug):
    # Пытаемся получить отель из кэша
    cache_key = CacheKeyGenerator.hotel_detail(slug)
    cached_hotel = cache.get(cache_key)
    
    if cached_hotel:
        hotel = cached_hotel
        logger.debug(f"Отель {slug} получен из кэша")
    else:
        # Оптимизация: используем select_related для загрузки связанных объектов отеля
        hotel = get_object_or_404(Hotel.objects.select_related(), status="Live", slug=slug)
        # Кэшируем отель
        cache.set(cache_key, hotel, settings.CACHE_TTL.get('hotel_detail', 1800))
        logger.debug(f"Отель {slug} закэширован")
    
    context = {
        "hotel": hotel,
    }
    return render(request, "booking/booking_data.html", context)


def add_to_selection(request):
    # Кэшируем данные сессии бронирования
    session_key = request.session.session_key or request.session._get_or_create_session_key()
    
    # Проверяем наличие данных о поиске типа номера
    if 'room_type_search_dates' in request.session:
        # Используем эти данные для обновления booking_common_data
        if 'booking_common_data' not in request.session:
            request.session['booking_common_data'] = {}
        
        # Обновляем booking_common_data данными из room_type_search_dates
        booking_common_data = {
            'checkin': request.session['room_type_search_dates'].get('checkin', request.GET['checkin']),
            'checkout': request.session['room_type_search_dates'].get('checkout', request.GET['checkout']),
            'adult': request.session['room_type_search_dates'].get('adult', request.GET['adult']),
            'children': request.session['room_type_search_dates'].get('children', request.GET['children']),
        }
        request.session['booking_common_data'] = booking_common_data
        
        # Кэшируем данные сессии
        BookingCacheHelper.cache_booking_session_data(session_key, booking_common_data)
    else:
        # Если room_type_search_dates отсутствует, используем данные из запроса
        if 'booking_common_data' not in request.session:
            booking_common_data = {
                'checkin': request.GET['checkin'],
                'checkout': request.GET['checkout'],
                'adult': request.GET['adult'],
                'children': request.GET['children'],
            }
            request.session['booking_common_data'] = booking_common_data
            
            # Кэшируем данные сессии
            BookingCacheHelper.cache_booking_session_data(session_key, booking_common_data)
    
    room_selection = {}
    current_hotel_id = request.GET['hotel_id']

    room_id = str(request.GET['id'])
    room_type_id = request.GET['room_type']
    
    # Оптимизация: если нужно получить room_capacity из базы, делаем это за один запрос
    need_room_capacity = 'room_capacity' not in request.GET or not request.GET['room_capacity']
    room_type_obj = None
    
    if need_room_capacity:
        # Пытаемся получить тип номера из кэша
        cache_key = f"room_type:{room_type_id}"
        cached_room_type = cache.get(cache_key)
        
        if cached_room_type:
            room_type_obj = cached_room_type
            logger.debug(f"Тип номера {room_type_id} получен из кэша")
        else:
            try:
                room_type_obj = RoomType.objects.get(id=room_type_id)
                # Кэшируем тип номера на 1 час
                cache.set(cache_key, room_type_obj, 3600)
                logger.debug(f"Тип номера {room_type_id} закэширован")
            except RoomType.DoesNotExist:
                pass

    room_selection[room_id] = {
        'hotel_id': current_hotel_id,
        'hotel_name': request.GET['hotel_name'],
        'room_name': request.GET['room_name'],
        'room_price': request.GET['room_price'],
        'number_of_beds': request.GET['number_of_beds'],
        'room_number': request.GET['room_number'],
        'room_type': room_type_id,
        'room_id': request.GET['room_id'],
    }

    # Добавляем room_capacity
    if 'room_capacity' in request.GET and request.GET['room_capacity']:
        room_selection[room_id]['room_capacity'] = request.GET['room_capacity']
    else:
        # Используем полученный ранее объект вместо нового запроса
        if room_type_obj:
            room_selection[room_id]['room_capacity'] = room_type_obj.room_capacity
        else:
            room_selection[room_id]['room_capacity'] = 0

    # Проверяем, есть ли уже номера в корзине и из какого они отеля
    if 'selection_data_obj' in request.session and request.session['selection_data_obj']:
        # Получаем первый номер из корзины для проверки отеля
        first_item_id = next(iter(request.session['selection_data_obj']))
        first_item = request.session['selection_data_obj'][first_item_id]
        existing_hotel_id = first_item['hotel_id']
        
        # Если пытаемся добавить номер из другого отеля
        if existing_hotel_id != current_hotel_id:
            # Возвращаем сообщение с предложением очистить корзину
            return JsonResponse({
                "error": True,
                "message": "Вы можете бронировать номера только из одного отеля. Хотите очистить данные о уже выбранных номерах?",
                "hotel_id": current_hotel_id
            })
    
    if 'selection_data_obj' in request.session:
        if room_id in request.session['selection_data_obj']:
            # Обновляем только данные о комнате, общие данные теперь хранятся отдельно
            selection_data = request.session['selection_data_obj']
            request.session['selection_data_obj'] = selection_data
        else:
            selection_data = request.session['selection_data_obj']
            selection_data.update(room_selection)
            request.session['selection_data_obj'] = selection_data
    else:
        request.session['selection_data_obj'] = room_selection
    
    # Помечаем сессию как измененную
    request.session.modified = True
    
    data = {
        "data": request.session['selection_data_obj'], 
        'total_selected_items': len(request.session['selection_data_obj'])
    }
    return JsonResponse(data)


def delete_session(request):
    request.session.pop('selection_data_obj', None)
    request.session.pop('booking_common_data', None)
    request.session.pop('room_types_data', None)
    return redirect(request.META.get("HTTP_REFERER"))


# Новый метод для очистки сессии и добавления нового номера
def clear_session_and_add_new(request):
    # Очищаем данные о выбранных номерах
    request.session.pop('selection_data_obj', None)
    request.session.pop('booking_common_data', None)
    request.session.pop('room_types_data', None)
    
    # Добавляем новый номер
    return add_to_selection(request)


def delete_selection(request):
    hotel_id = str(request.GET['id'])
    if 'selection_data_obj' in request.session:
        if hotel_id in request.session['selection_data_obj']:
            selection_data = request.session['selection_data_obj']
            del request.session['selection_data_obj'][hotel_id]
            request.session['selection_data_obj'] = selection_data

    total = 0
    total_days = 0
    room_count = 0
    adult = 0 
    children = 0 
    checkin = "" 
    checkout = "" 
    hotel = None
    first_room_type = None

    if 'selection_data_obj' in request.session and len(request.session['selection_data_obj']) > 0:
        # Проверяем наличие booking_common_data
        if 'booking_common_data' not in request.session:
            # Создаем booking_common_data со значениями по умолчанию
            today = datetime.now().strftime("%Y-%m-%d")
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            request.session['booking_common_data'] = {
                'checkin': today,
                'checkout': tomorrow,
                'adult': 1,
                'children': 0
            }
        
        # Получаем общие данные бронирования
        booking_data = request.session['booking_common_data']
        checkin = booking_data['checkin']
        checkout = booking_data['checkout']
        adult = int(booking_data['adult'])
        children = int(booking_data['children'])
        
        # Получаем данные о первой комнате для определения отеля
        first_room_id = next(iter(request.session['selection_data_obj']))
        first_room = request.session['selection_data_obj'][first_room_id]
        id = int(first_room['hotel_id'])
        
        # Оптимизация: используем select_related для загрузки связанных данных отеля
        try:
            hotel = Hotel.objects.select_related().get(id=id)
        except Hotel.DoesNotExist:
            logger.error(f"Отель с ID {id} не найден")
        
        # Расчет общей стоимости и количества дней
        date_format = "%Y-%m-%d"
        try:
            checkin_date = datetime.strptime(checkin, date_format).date()
            checkout_date = datetime.strptime(checkout, date_format).date()
            time_difference = checkout_date - checkin_date
            total_days = time_difference.days
        except Exception as e:
            logger.error(f"Ошибка при обработке дат: {e}")
            # Если есть ошибка в датах, используем значения по умолчанию
            today = datetime.now().strftime(date_format)
            tomorrow = (datetime.now() + timedelta(days=1)).strftime(date_format)
            checkin = today
            checkout = tomorrow
            checkin_date = datetime.strptime(checkin, date_format).date()
            checkout_date = datetime.strptime(checkout, date_format).date()
            time_difference = checkout_date - checkin_date
            total_days = time_difference.days
        
        # Оптимизация N+1: получаем все ID типов номеров и загружаем их одним запросом
        room_type_ids = [item["room_type"] for item_id, item in request.session['selection_data_obj'].items()]
        
        # Получаем все типы номеров одним запросом
        room_types_dict = {}
        if room_type_ids:
            room_types = RoomType.objects.filter(id__in=room_type_ids)
            room_types_dict = {str(rt.id): rt for rt in room_types}
        
            # Получаем первый тип номера для отображения на странице
            if room_types:
                first_room_type_id = request.session['selection_data_obj'][first_room_id]['room_type']
                first_room_type = room_types_dict.get(first_room_type_id)
        
        # Вычисляем общую стоимость бронирования с учетом динамических цен
        for h_id, item in request.session['selection_data_obj'].items():
            room_type_id = item["room_type"]
            room_type = room_types_dict.get(room_type_id)
            
            if room_type:
                # Рассчитываем стоимость комнаты с учетом динамических цен
                room_total = calculate_total_price(room_type, checkin_date, checkout_date)
                total += room_total
                
                # Добавляем slug типа номера в данные сессии, если его нет
                if not 'room_type_slug' in item:
                    request.session['selection_data_obj'][h_id]['room_type_slug'] = room_type.slug
                    request.session['selection_data_obj'][h_id]['room_capacity'] = room_type.room_capacity
                    request.session.modified = True
            else:
                logger.error(f"Тип номера с ID {room_type_id} не найден")
    
    context = {
        "data": request.session['selection_data_obj'] if 'selection_data_obj' in request.session else {},
        "total_selected_items": len(request.session['selection_data_obj']) if 'selection_data_obj' in request.session else 0,
        "total": total,
        "total_days": total_days,
        "adult": adult,
        "children": children,
        "checkin": checkin,
        "checkout": checkout,
        "hotel": hotel,
        "first_room_type": first_room_type,
    }
    
    # Добавляем JavaScript для инициализации скриптов после загрузки через AJAX
    init_script = """
    <script>
    // Инициализируем скрипты после загрузки
    if (typeof initAsyncInterface === 'function') {
        setTimeout(function() {
            initAsyncInterface();
        }, 100);
    }
    </script>
    """
    
    template = render_to_string(
        "hotel/async/selected_rooms.html",
        context,
        request=request
    )
    
    # Добавляем скрипт инициализации в конец шаблона
    template_with_script = template + init_script
    
    return JsonResponse({
        "data": template_with_script, 
        'total_selected_items': len(request.session['selection_data_obj']) if 'selection_data_obj' in request.session else 0
    })

