from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from django.template import RequestContext


from hotel.models import Hotel, Room, Booking, RoomServices, HotelGallery, HotelFeatures, RoomType
from hotel.views import calculate_total_price  # Импортируем функцию для расчета динамических цен

from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
import logging
logger = logging.getLogger(__name__)

def check_room_availability(request):
    if request.method == "POST":
        id = request.POST.get("hotel-id")
        checkin = request.POST.get("checkin")
        checkout = request.POST.get("checkout")
        adult = request.POST.get("adult")
        children = request.POST.get("children")
        room_type = request.POST.get("room-type", "")
        room_type_id = request.POST.get("room-type-id", "")
        
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
            hotel = Hotel.objects.get(status="Live", id=id)
        except Hotel.DoesNotExist:
            logger.error(f"Hotel with id={id} not found")
            messages.error(request, "Отель не найден.")
            return redirect("hotel:index")

        try:
            # Если room_type совпадает с room_type_id, значит это ID, а не slug
            if room_type and room_type.isdigit() and room_type_id and room_type == room_type_id:
                logger.info(f"room-type содержит ID типа номера: {room_type}")
                try:
                    room_type_obj = RoomType.objects.get(hotel=hotel, id=room_type)
                    logger.info(f"Найден тип номера по id (из поля room-type): {room_type}")
                except RoomType.DoesNotExist:
                    logger.error(f"RoomType с id={room_type} не найден")
                    messages.error(request, "Выбранный тип номера недоступен. Пожалуйста, выберите другой тип номера.")
                    return redirect("hotel:detail", slug=hotel.slug)
            # Иначе приоритет поиска: сначала по ID, затем по slug
            elif room_type_id:
                try:
                    room_type_obj = RoomType.objects.get(hotel=hotel, id=room_type_id)
                    logger.info(f"Найден тип номера по id: {room_type_id}")
                except (RoomType.DoesNotExist, ValueError):
                    # Если не удалось найти по ID, пробуем найти по slug
                    if room_type:
                        room_type_obj = RoomType.objects.get(hotel=hotel, slug=room_type)
                        logger.info(f"Найден тип номера по slug: {room_type}")
                    else:
                        raise RoomType.DoesNotExist("Не найден тип номера ни по id, ни по slug")
            elif room_type:
                # Пробуем сначала как ID, потом как slug
                try:
                    if room_type.isdigit():
                        room_type_obj = RoomType.objects.get(hotel=hotel, id=room_type)
                        logger.info(f"Найден тип номера по id (из поля room-type): {room_type}")
                    else:
                        room_type_obj = RoomType.objects.get(hotel=hotel, slug=room_type)
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
        return HttpResponseRedirect(url_with_params)

    else:
        logger.warning("Non-POST request to check_room_availability")
        return redirect("hotel:index")
    
def booking_data(request, slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    context = {
        "hotel":hotel,
    }
    return render(request, "booking/booking_data.html", context)


def add_to_selection(request):
    # Проверяем наличие данных о поиске типа номера
    if 'room_type_search_dates' in request.session:
        # Используем эти данные для обновления booking_common_data
        if 'booking_common_data' not in request.session:
            request.session['booking_common_data'] = {}
        
        # Обновляем booking_common_data данными из room_type_search_dates
        request.session['booking_common_data'] = {
            'checkin': request.session['room_type_search_dates'].get('checkin', request.GET['checkin']),
            'checkout': request.session['room_type_search_dates'].get('checkout', request.GET['checkout']),
            'adult': request.session['room_type_search_dates'].get('adult', request.GET['adult']),
            'children': request.session['room_type_search_dates'].get('children', request.GET['children']),
        }
    else:
        # Если room_type_search_dates отсутствует, используем данные из запроса
        if 'booking_common_data' not in request.session:
            request.session['booking_common_data'] = {
                'checkin': request.GET['checkin'],
                'checkout': request.GET['checkout'],
                'adult': request.GET['adult'],
                'children': request.GET['children'],
            }
    
    room_selection = {}

    room_selection[str(request.GET['id'])] = {
        'hotel_id': request.GET['hotel_id'],
        'hotel_name': request.GET['hotel_name'],
        'room_name': request.GET['room_name'],
        'room_price': request.GET['room_price'],
        'number_of_beds': request.GET['number_of_beds'],
        'room_number': request.GET['room_number'],
        'room_type': request.GET['room_type'],
        'room_id': request.GET['room_id'],
    }

    if 'selection_data_obj' in request.session:
        if str(request.GET['id']) in request.session['selection_data_obj']:
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
    return redirect(request.META.get("HTTP_REFERER"))


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
        try:
            hotel = Hotel.objects.get(id=id)
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
        
        # Вычисляем общую стоимость бронирования с учетом динамических цен
        for h_id, item in request.session['selection_data_obj'].items():
            room_type_id = item["room_type"]
            try:
                room_type = RoomType.objects.get(id=room_type_id)
                # Рассчитываем стоимость комнаты с учетом динамических цен
                room_total = calculate_total_price(room_type, checkin_date, checkout_date)
                total += room_total
                
                # Добавляем slug типа номера в данные сессии
                if not 'room_type_slug' in item:
                    request.session['selection_data_obj'][h_id]['room_type_slug'] = room_type.slug
                    request.session.modified = True
            except RoomType.DoesNotExist:
                logger.error(f"Тип номера с ID {room_type_id} не найден")
    
    # Получаем первый тип номера для отображения на странице
    first_room_type = None
    if 'selection_data_obj' in request.session and len(request.session['selection_data_obj']) > 0:
        first_id = next(iter(request.session['selection_data_obj']))
        first_room_type_id = request.session['selection_data_obj'][first_id]['room_type']
        try:
            first_room_type = RoomType.objects.get(id=first_room_type_id)
        except RoomType.DoesNotExist:
            pass
    
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

