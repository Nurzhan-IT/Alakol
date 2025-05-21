from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q, Count, OuterRef
import uuid

from hotel.models import Coupon, CouponUsers, Hotel, Room, Booking, RoomServices, HotelGallery, HotelFeatures, RoomType, RoomTypeGallery, Notification, Bookmark, Review
from booking.models import RoomUnavailability

from datetime import datetime, timedelta
from decimal import Decimal
import json
import random
import string

# Импорт модуля Робокассы
from robokassa.robokassa import generate_payment_link, result_payment, check_success_payment

from hotel.decorators import require_selection_data

def index(request):
    hotel = Hotel.objects.filter(status="Live")
    context = {
        "hotel":hotel
    }
    return render(request, "hotel/index.html", context)


def hotel_detail(request, slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    room_type_images = RoomTypeGallery.objects.filter(hotel=hotel)
    try:
        reviews = Review.objects.filter(user=request.user, hotel=hotel)
    except:
        reviews = None
    all_reviews = Review.objects.filter(hotel=hotel, active=True)
    
    if request.user.is_authenticated:
        bookmark = Bookmark.objects.filter(user=request.user, hotel=hotel)
    else:
        bookmark = None
        
    # Подготовка данных для таблицы динамических цен
    room_types = RoomType.objects.filter(hotel=hotel)
    
    # Собираем все даты из dynamic_pricing всех типов номеров
    all_dates = []
    for room_type in room_types:
        if room_type.dynamic_pricing and isinstance(room_type.dynamic_pricing, dict):
            all_dates.extend([date for date in room_type.dynamic_pricing.keys()])
    
    # Сортируем и удаляем дубликаты
    unique_dates = sorted(set(all_dates))
    
    # Группируем даты по неделям или другим интервалам
    date_ranges = []
    range_prices = {}
    
    if unique_dates:
        from datetime import datetime
        
        # Преобразуем строки в даты для сортировки
        date_objects = []
        for date_str in unique_dates:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                date_objects.append((date_str, date_obj))
            except ValueError:
                continue
        
        # Сортируем даты
        date_objects.sort(key=lambda x: x[1])
        
        # Получаем первую и последнюю даты в отсортированном списке
        if date_objects:
            # Группируем даты по интервалам (например, неделям)
            from datetime import timedelta
            
            step = 7  # Количество дней в одном интервале
            current_date_index = 0
            
            while current_date_index < len(date_objects):
                start_date = date_objects[current_date_index][1]
                end_date = start_date + timedelta(days=step-1)
                
                # Находим конечную дату в интервале
                end_index = current_date_index
                while end_index < len(date_objects) and date_objects[end_index][1] <= end_date:
                    end_index += 1
                
                # Если достигли конца списка, используем последнюю доступную дату
                if end_index > len(date_objects) - 1:
                    end_index = len(date_objects) - 1
                
                actual_end_date = date_objects[end_index][1]
                
                # Форматируем интервал для отображения
                date_range = f"{start_date.strftime('%d.%m.%Y')} - {actual_end_date.strftime('%d.%m.%Y')}"
                date_ranges.append(date_range)
                
                # Сохраняем цены для каждого типа номера в этом интервале дат
                range_prices[date_range] = {}
                
                # Для каждого типа номера вычисляем среднюю цену в этом интервале
                for room_type in room_types:
                    if room_type.dynamic_pricing and isinstance(room_type.dynamic_pricing, dict):
                        # Собираем цены для дат в интервале
                        prices_in_range = []
                        current_index = current_date_index
                        
                        while current_index <= end_index:
                            date_str = date_objects[current_index][0]
                            if date_str in room_type.dynamic_pricing:
                                try:
                                    price = float(room_type.dynamic_pricing[date_str])
                                    prices_in_range.append(price)
                                except (ValueError, TypeError):
                                    pass
                            current_index += 1
                        
                        # Если есть цены в интервале, вычисляем среднюю
                        if prices_in_range:
                            avg_price = sum(prices_in_range) / len(prices_in_range)
                            range_prices[date_range][room_type.id] = int(avg_price)
                
                # Переходим к следующему интервалу
                current_date_index = end_index + 1
    
    context = {
        "hotel": hotel,
        "bookmark": bookmark,
        "reviews": reviews,
        "all_reviews": all_reviews,
        "room_type_images": room_type_images,
        "date_ranges": date_ranges,
        "range_prices": range_prices,
    }
    return render(request, "hotel/hotel_detail.html", context)


def room_type_detail(request, slug, rt_slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)
    room_type = RoomType.objects.get(hotel=hotel, slug=rt_slug)
    
    id = request.GET.get("hotel-id")
    checkin = request.GET.get("checkin")
    checkout = request.GET.get("checkout")
    adult = request.GET.get("adult")
    children = request.GET.get("children")
    room_type_ = request.GET.get("room-type")

    # Если даты не переданы через GET, но есть в сессии - берем их оттуда
    if not all([checkin, checkout]) and 'booking_common_data' in request.session:
        booking_data = request.session['booking_common_data']
        checkin = booking_data.get('checkin')
        checkout = booking_data.get('checkout')
        adult = booking_data.get('adult', adult)
        children = booking_data.get('children', children)
    
    if not all([checkin, checkout]):
        messages.warning(request, "Please enter your booking data to check availability.")
        return redirect("booking:booking_data", hotel.slug)
    
    # Конвертируем строки с датами в объекты datetime
    date_format = "%Y-%m-%d"
    user_checkin_date = datetime.strptime(checkin, date_format).date()
    user_checkout_date = datetime.strptime(checkout, date_format).date()
    
    # Проверяем, активен ли отель на выбранные даты
    hotel_available = hotel.is_active_for_dates(user_checkin_date, user_checkout_date)
    if not hotel_available:
        messages.warning(request, "Отель не доступен для бронирования на выбранные даты.")
        return redirect("hotel:detail", hotel.slug)
    
    # Получаем все доступные номера данного типа
    rooms = Room.objects.filter(room_type=room_type, is_available=True)
    
    # Получаем ID номеров, которые уже забронированы на указанные даты
    # Учитываем, что в день выезда номер уже доступен (за счет -1 день)
    booked_room_ids = Booking.objects.filter(
        Q(check_in_date__lt=user_checkout_date, check_out_date__gt=user_checkin_date),
        is_active=True,
        payment_status__in=["paid", "processing", "pending"]
    ).values_list('room__id', flat=True).distinct()

    # Получаем ID номеров, которые находятся в RoomUnavailability на указанные даты
    unavailable_room_ids = RoomUnavailability.objects.filter(
        Q(start_date__lt=user_checkout_date, end_date__gt=user_checkin_date)
    ).values_list('room__id', flat=True).distinct()
    
    # Исключаем забронированные номера из списка доступных
    available_rooms = rooms.exclude(id__in=booked_room_ids).exclude(id__in=unavailable_room_ids)
    
    # Рассчитываем стоимость с учетом динамических цен
    total_days = (user_checkout_date - user_checkin_date).days
    dynamic_price = calculate_total_price(room_type, user_checkin_date, user_checkout_date)

    dynamic_price_json_data = room_type.dynamic_pricing
    
    # Проверяем статусы комнат в selection_data_obj
    room_statuses = {}
    if 'selection_data_obj' in request.session and request.session['selection_data_obj']:
        selection_data = request.session['selection_data_obj']
        booking_common_data = request.session.get('booking_common_data', {})
        room_type_search_dates = request.session.get('room_type_search_dates', {})
        
        for room in available_rooms:
            room_statuses[room.id] = "Add To Selection"
            
            # Проверяем, есть ли комната в selection_data_obj
            for index, item in selection_data.items():
                try:
                    if int(item['room_id']) == room.id:
                        # Проверяем совпадение дат
                        if booking_common_data.get('checkin') == room_type_search_dates.get('checkin') and \
                           booking_common_data.get('checkout') == room_type_search_dates.get('checkout'):
                            room_statuses[room.id] = "Added To Selection"
                        else:
                            room_statuses[room.id] = "Update"
                        break
                except (KeyError, ValueError):
                    continue
    else:
        # Если selection_data_obj не существует, все кнопки будут "Add To Selection"
        for room in available_rooms:
            room_statuses[room.id] = "Add To Selection"
    
    context = {
        "hotel": hotel,
        "room_type": room_type,
        "rooms": available_rooms,
        "id": id,
        "checkin": checkin,
        "checkout": checkout,
        "adult": adult,
        "children": children,
        "room_type_": room_type_,
        "dynamic_price": dynamic_price,  # Добавляем динамическую цену в контекст
        "dynamic_price_json_data": dynamic_price_json_data,
        "total_days": total_days,        # Добавляем общее количество дней
        "room_statuses": room_statuses,  # Добавляем статусы кнопок для комнат
    }
    return render(request, "hotel/room_type_detail.html", context)


def get_visitor_id(request):
    """Получает или создает уникальный идентификатор посетителя"""
    if not request.session.get('visitor_id'):
        request.session['visitor_id'] = str(uuid.uuid4())
    return request.session['visitor_id']


@require_selection_data
def selected_rooms(request):
    # request.session.pop('selection_data_obj', None)

    total = 0
    room_count = 0
    total_days = 0
    adult = 0 
    children = 0 
    checkin = "0" 
    checkout = "" 
    children = 0 
    if request.session['selection_data_obj'] == {} or 'selection_data_obj' not in request.session :
        messages.warning(request, "You don't have any room selections yet!")
        return redirect("/")
    # Если пришли данные POST с датами, обновим booking_common_data
    if request.method == "POST" and 'selection_data_obj' in request.session:
        update_booking_dates = False
        # Проверяем, есть ли в запросе данные о датах
        if 'checkin' in request.POST and 'checkout' in request.POST:
            checkin = request.POST.get('checkin')
            checkout = request.POST.get('checkout')
            update_booking_dates = True
            
            # Создаем или обновляем booking_common_data в сессии
            if 'booking_common_data' not in request.session:
                request.session['booking_common_data'] = {}
                request.session['booking_common_data']['adult'] = request.POST.get('adult', '1')
                request.session['booking_common_data']['children'] = request.POST.get('children', '0')
            
            request.session['booking_common_data']['checkin'] = checkin
            request.session['booking_common_data']['checkout'] = checkout
            request.session.modified = True
            
            print(f"Обновлены данные в сессии: checkin={checkin}, checkout={checkout}")
    
    if 'selection_data_obj' in request.session and 'booking_common_data' in request.session:
        if request.method == "POST" and not 'checkin' in request.POST:
            # Получаем данные из формы
            full_name = request.POST.get("full_name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            country_code = request.POST.get("country_code") # Получаем код страны
            
            # Сохраняем данные пользователя в сессии для последующего использования при оплате
            if 'user_data' not in request.session:
                request.session['user_data'] = {}
                
            request.session['user_data'] = {
                'full_name': full_name,
                'email': email,
                'phone': phone,
                'country_code': country_code # Сохраняем код страны
            }
            
            # Перенаправляем на страницу выбора способа оплаты
            return redirect("hotel:payment_method_selection")

        hotel = None
        total = 0
        room_types_data = {}  # Словарь для хранения данных о типах номеров

        # Получаем общие данные бронирования
        if 'booking_common_data' in request.session:
            booking_data = request.session['booking_common_data']
            checkin = booking_data['checkin']
            checkout = booking_data['checkout']
            adult = int(booking_data['adult'])
            children = int(booking_data['children'])
            
            # Расчет общей стоимости и количества дней
            date_format = "%Y-%m-%d"
            try:
                checkin_date = datetime.strptime(checkin, date_format).date()
                checkout_date = datetime.strptime(checkout, date_format).date()
                time_difference = checkout_date - checkin_date
                total_days = time_difference.days
            except Exception as e:
                print(f"Ошибка при расчете дат: {e}")
                # Устанавливаем значения по умолчанию, если даты некорректны
                today = datetime.now().strftime(date_format)
                tomorrow = (datetime.now() + timedelta(days=1)).strftime(date_format)
                booking_data['checkin'] = today
                booking_data['checkout'] = tomorrow
                request.session['booking_common_data'] = booking_data
                request.session.modified = True
                checkin = today
                checkout = tomorrow
                checkin_date = datetime.strptime(checkin, date_format).date()
                checkout_date = datetime.strptime(checkout, date_format).date()
                time_difference = checkout_date - checkin_date
                total_days = time_difference.days
            
            # Получаем первую комнату для определения отеля
            if len(request.session['selection_data_obj']) > 0:
                first_item_id = next(iter(request.session['selection_data_obj']))
                first_item = request.session['selection_data_obj'][first_item_id]
                hotel_id = int(first_item['hotel_id'])
                try:
                    hotel = Hotel.objects.get(id=hotel_id)
                except Hotel.DoesNotExist:
                    print(f"Отель с ID {hotel_id} не найден")
        
        for h_id, item in request.session['selection_data_obj'].items():
                
            room_type_ = item["room_type"]
            room_id = int(item["room_id"])
            
            room_type = RoomType.objects.get(id=room_type_)
            room = Room.objects.get(id=room_id)

            # Используем динамические цены вместо фиксированной цены
            # Рассчитываем стоимость с учетом динамических цен
            room_total = calculate_total_price(room_type, checkin_date, checkout_date)
            total += room_total
            
            # Сохраняем данные о комнате и добавляем информацию о slug типа комнаты
            request.session['selection_data_obj'][h_id]['room_number'] = room.room_number
            request.session['selection_data_obj'][h_id]['room_type_slug'] = room_type.slug
            
            # Обновляем хранимую цену в сессии с учетом динамического ценообразования
            request.session['selection_data_obj'][h_id]['room_price'] = str(room_total)
            request.session.modified = True
            
            # Сохраняем данные о типе номера для последующего использования
            room_types_data[room_type_] = {
                'id': room_type.id,
                'slug': room_type.slug,
                'name': room_type.type if hasattr(room_type, 'type') else str(room_type)
            }

        # Обновляем room_types_data в сессии для использования в JavaScript
        request.session['room_types_data'] = room_types_data
        request.session.modified = True

        # print("hotel ===", hotel)
        print("selection_data_obj ===", request.session['selection_data_obj'])
        print("room_types_data ===", room_types_data)
        if 'booking_common_data' in request.session:
            print("booking_common_data ===", request.session['booking_common_data'])
        else:
            print("booking_common_data не найден в сессии")
            # Создаем booking_common_data со значениями по умолчанию, если он отсутствует
            today = datetime.now().strftime("%Y-%m-%d")
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            request.session['booking_common_data'] = {
                'checkin': today,
                'checkout': tomorrow,
                'adult': 1,
                'children': 0
            }
            checkin = today
            checkout = tomorrow
            adult = 1
            children = 0
            
            # Рассчитываем total_days
            date_format = "%Y-%m-%d"
            checkin_date = datetime.strptime(checkin, date_format)
            checkout_date = datetime.strptime(checkout, date_format)
            time_difference = checkout_date - checkin_date
            total_days = time_difference.days
            
            # Пересчитываем total с новыми значениями дат
            total = 0
            for h_id, item in request.session['selection_data_obj'].items():
                room_type_ = item["room_type"]
                room_type = RoomType.objects.get(id=room_type_)
                price = room_type.price
                total += price * total_days
            print("booking_common_data ===", request.session['booking_common_data'])
        
        
        # Получаем информацию о пользователе
        if request.user.is_authenticated:
            print("User:", request.user.username)
            print("User ID:", request.user.id)
        else:
            visitor_id = get_visitor_id(request)
            print("Visitor ID:", visitor_id)
            print("User: Anonymous")
            print("User ID: Not authenticated")
        
        # Получаем первый тип номера для отображения на странице
        first_room_type = None
        if len(request.session['selection_data_obj']) > 0:
            first_id = next(iter(request.session['selection_data_obj']))
            first_room_type_id = request.session['selection_data_obj'][first_id]['room_type']
            try:
                first_room_type = RoomType.objects.get(id=first_room_type_id)
            except RoomType.DoesNotExist:
                pass

        # Преобразуем room_types_data в формат, подходящий для JSON
        room_types_json = {}
        for key, value in room_types_data.items():
            room_types_json[str(key)] = value
            
        context = {
            "data":request.session['selection_data_obj'], 
            "total_selected_items": len(request.session['selection_data_obj']),
            "total":total,
            "total_days":total_days,
            "adult":adult,
            "children":children,   
            "checkin":checkin,   
            "checkout":checkout,   
            "hotel":hotel,
            "room_types_data": json.dumps(room_types_json),
            "first_room_type": first_room_type, # Первый тип номера
        }
        print("context ===", context)
        return render(request, "hotel/selected_rooms.html", context)
    else:
        messages.warning(request, "You don't have any room selections yet!")
        return redirect("/")

def payment_method_selection(request):
    """Страница выбора способа оплаты"""
    
    if 'selection_data_obj' not in request.session or 'user_data' not in request.session:
        messages.warning(request, "You don't have any room selections or missing user information!")
        return redirect("/")
    
    # Расчет итоговой суммы для отображения
    total = 0
    total_days = 0
    checkin = ""
    checkout = ""
    
    # Получаем общие данные бронирования
    if 'booking_common_data' in request.session:
        booking_data = request.session['booking_common_data']
        checkin = booking_data['checkin']
        checkout = booking_data['checkout']
        
        # Расчет количества дней
        date_format = "%Y-%m-%d"
        checkin_date = datetime.strptime(checkin, date_format).date()
        checkout_date = datetime.strptime(checkout, date_format).date()
        time_difference = checkout_date - checkin_date
        total_days = time_difference.days
        
        # Рассчитываем общую стоимость с учетом динамических цен
        for h_id, item in request.session['selection_data_obj'].items():
            room_type_id = item["room_type"]
            room_type = RoomType.objects.get(id=room_type_id)
            
            # Рассчитываем стоимость с учетом динамических цен
            room_total = calculate_total_price(room_type, checkin_date, checkout_date)
            total += room_total
    
    context = {
        "total": total,
        "user_data": request.session['user_data'],
        "checkin": checkin,
        "checkout": checkout,
        "total_days": total_days,
    }
    
    return render(request, "hotel/payment_method_selection.html", context)

def process_booking(request):
    """Создает бронирование из данных сессии и возвращает booking_id"""
    import logging
    logger = logging.getLogger(__name__)
    
    if 'selection_data_obj' not in request.session or 'user_data' not in request.session or 'booking_common_data' not in request.session:
        messages.warning(request, "Missing booking information!")
        return None
    
    booking = None
    try:
        total = 0
        room_count = 0
        
        # Получаем общие данные бронирования
        booking_data = request.session['booking_common_data']
        checkin = booking_data['checkin']
        checkout = booking_data['checkout']
        adult = int(booking_data['adult'])
        children = int(booking_data['children'])
        
        # Получаем первый элемент для определения отеля
        first_item_id = next(iter(request.session['selection_data_obj']))
        first_item = request.session['selection_data_obj'][first_item_id]
        hotel_id = int(first_item['hotel_id'])
        hotel = Hotel.objects.get(id=hotel_id)
        room_type_id = first_item["room_type"]
        room_type = RoomType.objects.get(id=room_type_id)
        
        date_format = "%Y-%m-%d"
        checkin_date = datetime.strptime(checkin, date_format).date()
        checkout_date = datetime.strptime(checkout, date_format).date()
        time_difference = checkout_date - checkin_date
        total_days = time_difference.days
        
        # Проверяем, активен ли отель на выбранные даты
        hotel_available = hotel.is_active_for_dates(checkin_date, checkout_date)
        if not hotel_available:
            messages.warning(request, "Отель не доступен для бронирования на выбранные даты.")
            return None
        
        # Получаем данные пользователя из сессии
        user_data = request.session['user_data']
        full_name = user_data['full_name']
        email = user_data['email']
        phone = user_data['phone']
        country_code = user_data.get('country_code', '')  # Получаем код страны, по умолчанию пустая строка
        
        # Создаем бронирование
        booking = Booking.objects.create(
            hotel=hotel,
            room_type=room_type,
            check_in_date=checkin,
            check_out_date=checkout,
            total_days=total_days,
            num_adults=adult,
            num_children=children,
            full_name=full_name,
            email=email,
            phone=phone,
            country_code=country_code,  # Сохраняем код страны
            payment_status="initiated"  # Статус "инициировано"
        )
        
        if request.user.is_authenticated:
            booking.user = request.user
            booking.save()
        
        # Добавляем комнаты к бронированию и рассчитываем общую стоимость
        for h_id, item in request.session['selection_data_obj'].items():
            room_id = int(item["room_id"])
            room = Room.objects.get(id=room_id)
            booking.room.add(room)
            
            # Получаем тип комнаты для текущей комнаты
            room_type_id = item["room_type"]
            room_type = RoomType.objects.get(id=room_type_id)
            
            # Рассчитываем стоимость с учетом динамических цен
            room_total = calculate_total_price(room_type, checkin_date, checkout_date)
            total += room_total
        
        # Обновляем сумму бронирования
        from decimal import Decimal
        booking.total = Decimal(str(total))
        booking.before_discount = Decimal(str(total))
        booking.save()
        
        logger.info(f"Создано бронирование {booking.booking_id} на сумму {booking.total}")
        logger.info (f"{booking.booking_id}: selection_data_obj ===", request.session['selection_data_obj'])
        logger.info (f"{booking.booking_id}: booking_common_data ===", request.session['booking_common_data'])
        return booking
        
    except Exception as e:
        logger.error(f"Ошибка при создании бронирования: {str(e)}")
        # Если объект бронирования был создан, но произошла ошибка - удаляем его
        if booking and booking.id:
            try:
                booking.delete()
                logger.info(f"Удалено неполное бронирование из-за ошибки")
            except Exception as del_err:
                logger.error(f"Ошибка при удалении неполного бронирования: {str(del_err)}")
        return None

# Обновляем функцию Робокассы для создания бронирования перед платежом
@csrf_exempt
def create_robokassa_payment(request, payment_key=None):
    """Создает URL для перенаправления на платежную страницу Робокассы"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Проверяем доступность номеров перед созданием бронирования
        if payment_key is None and 'selection_data_obj' in request.session and 'booking_common_data' in request.session:
            unavailable_rooms = []
            
            # Получаем общие данные бронирования для проверки дат
            booking_data = request.session['booking_common_data']
            date_format = "%Y-%m-%d"
            checkin_date = datetime.strptime(booking_data['checkin'], date_format).date()
            checkout_date = datetime.strptime(booking_data['checkout'], date_format).date()
            
            # Получаем информацию об отеле
            first_item_id = next(iter(request.session['selection_data_obj']))
            first_item = request.session['selection_data_obj'][first_item_id]
            hotel_id = int(first_item['hotel_id'])
            hotel = Hotel.objects.get(id=hotel_id)
            
            # Проверяем, активен ли отель на выбранные даты
            hotel_available = hotel.is_active_for_dates(checkin_date, checkout_date)
            if not hotel_available:
                messages.warning(request, "Отель не доступен для бронирования на выбранные даты.")
                return redirect("/")
            
            for h_id, item in request.session['selection_data_obj'].items():
                room_id = int(item["room_id"])
                room = Room.objects.get(id=room_id)
                
                # Проверяем, что номер всё еще доступен (is_available = True)
                if not room.is_available:
                    unavailable_rooms.append({
                        'h_id': h_id,
                        'room': room,
                        'reason': 'not_available'
                    })
                    continue
                
                # Ищем пересекающиеся бронирования с оплаченным или находящимся в процессе оплаты статусом
                overlapping_bookings = Booking.objects.filter(
                    Q(check_in_date__lt=checkout_date, check_out_date__gt=checkin_date),
                    Q(payment_status__in=["paid", "processing", "pending"]),
                    room=room,
                    is_active=True
                ).exists()
                
                if overlapping_bookings:
                    unavailable_rooms.append({
                        'h_id': h_id,
                        'room': room,
                        'reason': 'already_booked'
                    })
                    continue

                # Проверяем, что номер не находится в таблице RoomUnavailability
                unavailable = RoomUnavailability.objects.filter(
                    room=room,
                    start_date__lt=checkout_date,
                    end_date__gt=checkin_date
                ).exists()

                if unavailable:
                    unavailable_rooms.append({
                        'h_id': h_id,
                        'room': room,
                        'reason': 'marked_unavailable'
                    })
            
            # Если есть недоступные номера, удаляем их из сессии и показываем сообщение
            if unavailable_rooms:
                for item in unavailable_rooms:
                    h_id = item['h_id']
                    room = item['room']
                    reason = item['reason']
                    
                    # Удаляем номер из сессии
                    if h_id in request.session['selection_data_obj']:
                        room_number = request.session['selection_data_obj'][h_id].get('room_number', 'неизвестный')
                        del request.session['selection_data_obj'][h_id]
                        request.session.modified = True
                        
                        if reason == 'not_available':
                            messages.error(request, f"Номер {room_number} недоступен для бронирования и был удален из списка.")
                        elif reason == 'marked_unavailable':
                            messages.error(request, f"Номер {room_number} отмечен как недоступный на выбранные даты и был удален из списка.")
                        else:
                            messages.error(request, f"Номер {room_number} уже забронирован на выбранные даты и был удален из списка.")
                
                # Если после удаления недоступных номеров в сессии не осталось выбранных номеров,
                # перенаправляем на страницу выбора номеров
                if not request.session['selection_data_obj']:
                    messages.error(request, "Все выбранные номера недоступны для бронирования.")
                    return redirect("/")
                else:
                    # Если остались доступные номера, перенаправляем на страницу выбранных номеров
                    messages.warning(request, "Некоторые выбранные номера недоступны. Пожалуйста, проверьте список и продолжите бронирование.")
                    return redirect("hotel:selected_rooms")
        
        # Если бронирование еще не создано
        booking = None
        if payment_key is None:
            # Создаем бронирование из данных в сессии
            booking = process_booking(request)
            if not booking:
                messages.error(request, "Failed to create booking!")
                return redirect("/")
        else:
            # Если уже есть ID бронирования, получаем его
            booking = get_object_or_404(Booking, booking_id=payment_key)
        
        logger.info(f"Создание платежа для бронирования {booking.booking_id}")
        
        # Используем абсолютный домен без языкового префикса
        domain = request.build_absolute_uri('/').rstrip('/')

        relative_path = request.path
        culture='ru'

        if '/ru/' in domain:
            domain = domain.replace('/ru/', '/')
        elif '/en/' in domain:
            domain = domain.replace('/en/', '/')
        elif '/kk/' in domain:
            domain = domain.replace('/kk/', '/')

        if '/ru/' in relative_path:
            culture = 'ru'
        elif '/en/' in relative_path:
            culture = 'en'
        elif '/kk/' in relative_path:
            culture = 'ru'
        
        # Формируем URL-ы для успешной/неудачной оплаты БЕЗ языкового префикса
        success_url = f"{domain}/robokassa/success/"
        fail_url = f"{domain}/robokassa/failed/"
        result_url = f"{domain}/robokassa/result/"
        
        logger.info(f"Success URL: {success_url}")
        logger.info(f"Fail URL: {fail_url}")
        logger.info(f"Result URL: {result_url}")
        
        try:
            # Конвертируем booking.total в decimal.Decimal перед передачей в generate_payment_link
            from decimal import Decimal
            payment_total = Decimal(str(booking.total))
            
            # Генерируем ссылку на оплату
            payment_link = generate_payment_link(
                cost=payment_total,
                number=int(booking.id),
                description=booking.booking_id,
                culture=culture,
                email=booking.email
            )
            
            # Сохраняем InvId в booking сразу после генерации ссылки
            booking.robokassa_inv_id = int(booking.id)
            
            # Обновляем статус платежа
            booking.payment_status = "processing"
            booking.save()
            
            logger.info(f"Сгенерированная ссылка на оплату: {payment_link}")
            logger.info(f"InvId {booking.robokassa_inv_id} сохранен в бронировании {booking.booking_id}")
            
            # Если это AJAX-запрос, возвращаем JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'payment_url': payment_link,
                    'success_url': success_url,
                    'fail_url': fail_url
                })
            
            # Иначе перенаправляем на страницу оплаты
            return redirect(payment_link)
            
        except Exception as e:
            logger.error(f"Ошибка при создании платежной ссылки: {str(e)}")
            # Если произошла ошибка и бронирование было создано, удаляем его
            if booking and booking.id and payment_key is None:
                try:
                    booking.delete()
                    logger.info(f"Удалено бронирование {booking.booking_id} из-за ошибки создания платежа")
                except Exception as del_err:
                    logger.error(f"Ошибка при удалении бронирования: {str(del_err)}")
            
            # Сообщаем об ошибке пользователю
            messages.error(request, f"Ошибка при создании платежа: {str(e)}")
            return redirect("/")
            
    except Exception as e:
        logger.error(f"Ошибка при создании платежа: {str(e)}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        messages.error(request, f"Error: {str(e)}")
        return redirect("/")

@csrf_exempt
def robokassa_result(request):
    """Обработчик для Result URL"""
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        logger.info(f"Получен POST-запрос от Робокассы: {request.POST}")
        
        try:
            result = result_payment(request.POST)
            logger.info(f"Результат проверки подписи: {result}")
            
            if result.startswith('OK'):
                # Извлекаем ID заказа
                order_id = int(request.POST.get('InvId', 0))
                try:
                    booking = Booking.objects.get(id=order_id)
                    booking.payment_status = "paid"  # Устанавливаем статус "оплачено"
                    # Проверяем, не был ли InvId уже сохранен
                    if booking.robokassa_inv_id is None:
                        booking.robokassa_inv_id = order_id  # Сохраняем InvId в модель
                        logger.info(f"Сохранен InvId {order_id} в бронировании {booking.booking_id}")
                    
                    booking.save()
                    
                    logger.info(f"Платеж успешно обработан для бронирования {booking.booking_id}, Robokassa InvId: {order_id}")
                    
                    # Создаем уведомление
                    noti = Notification.objects.create(booking=booking, type="Booking Confirmed")
                    if request.user.is_authenticated:
                        noti.user = request.user
                        noti.save()
                    
                    # Отправляем электронное письмо клиенту - с обработкой ошибок
                    try:
                        merge_data = {
                            'booking': booking, 
                            'booking_rooms': booking.room.all(), 
                            'full_name': booking.full_name, 
                            'subject': f"Booking Completed - Invoice & Summary - ID: #{booking.booking_id}", 
                        }
                        subject = f"Booking Completed - Invoice & Summary - ID: #{booking.booking_id}"
                        text_body = render_to_string("email/booking_completed.txt", merge_data)
                        html_body = render_to_string("email/booking_completed.html", merge_data)
                        
                        msg = EmailMultiAlternatives(
                            subject=subject, 
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[booking.email], 
                            body=text_body
                        )
                        msg.attach_alternative(html_body, "text/html")
                        msg.send(fail_silently=True)  # fail_silently=True для игнорирования ошибок отправки
                    except Exception as email_error:
                        # Логируем ошибку, но не отменяем успешную обработку платежа
                        logger.error(f"Ошибка при отправке email: {str(email_error)}")
                    
                    # Удаляем данные о номерах из сессии
                    if 'selection_data_obj' in request.session:
                        del request.session['selection_data_obj']
                    
                    # Удаляем общие данные бронирования из сессии
                    if 'booking_common_data' in request.session:
                        del request.session['booking_common_data']
                    
                    # Удаляем данные пользователя из сессии
                    if 'user_data' in request.session:
                        del request.session['user_data']
                    
                except Booking.DoesNotExist:
                    logger.error(f"Бронирование с ID {order_id} не найдено")
                    return HttpResponse("ERROR: Booking not found", status=404)
                
                return HttpResponse(result)
            else:
                logger.error(f"Неверная подпись платежа: {result}")
                return HttpResponse("ERROR: Invalid signature", status=400)
                
        except Exception as e:
            logger.error(f"Ошибка при обработке платежа: {str(e)}")
            return HttpResponse(f"ERROR: {str(e)}", status=500)
    
    logger.warning("Получен не POST-запрос")
    return HttpResponseBadRequest("Invalid request method")

@csrf_exempt
def robokassa_success(request, booking_id):
    """Обработчик для Success URL с указанием booking_id"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        booking = get_object_or_404(Booking, booking_id=booking_id)
        logger.info(f"Обработка успешного платежа для бронирования {booking_id}")
        
        # Проверяем прямую подпись платежа, если она есть в параметрах запроса
        payment_verified = False
        
        # Проверяем, есть ли параметры от Робокассы в запросе
        if 'OutSum' in request.GET and 'InvId' in request.GET and 'SignatureValue' in request.GET:
            payment_verified = check_success_payment(request.GET)
            logger.info(f"Проверка подписи Робокассы: {payment_verified}")
            
            # Если подпись подтверждена и InvId еще не сохранен, сохраняем его
            if payment_verified and booking.robokassa_inv_id is None:
                booking.robokassa_inv_id = int(request.GET.get('InvId', 0))
                logger.info(f"Сохранен InvId {booking.robokassa_inv_id} в бронировании {booking.booking_id}")
        
        # Если нет параметров, проверяем, был ли уже оплачен заказ ранее через Result URL
        # или через robokassa_success_direct
        if not payment_verified:
            if booking.payment_status == "paid":
                # Если бронирование уже отмечено как оплаченное, это легитимно
                payment_verified = True
                logger.info(f"Бронирование {booking_id} уже было отмечено как оплаченное")
            else:
                # Попытка доступа к success без прямых параметров и без предварительной обработки Result URL
                # Вероятная попытка обойти оплату
                logger.warning(f"Попытка доступа к странице успешной оплаты без верификации: {booking_id}")
                messages.error(request, "Ошибка: Оплата не подтверждена системой. Если вы произвели оплату, обратитесь в службу поддержки.")
                return redirect("/")
        
        # Если оплата подтверждена, обновляем статус и очищаем сессию
        if payment_verified:
            if booking.payment_status != "paid":
                booking.payment_status = "paid"
                booking.save()
                messages.success(request, f'Ваше бронирование успешно оплачено!')
                logger.info(f"Статус бронирования {booking_id} обновлен на 'paid'")
            
            # Удаляем данные из сессии
            if 'selection_data_obj' in request.session:
                del request.session['selection_data_obj']
            
            if 'booking_common_data' in request.session:
                del request.session['booking_common_data']
            
            if 'user_data' in request.session:
                del request.session['user_data']
            
            context = {
                "booking": booking, 
                'rooms': booking.room.all(), 
            }
            return render(request, "hotel/payment_success.html", context)
        else:
            # На всякий случай, хотя мы должны были перенаправить раньше
            messages.error(request, "Ошибка: Оплата не подтверждена системой.")
            return redirect("/")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке успешного платежа: {str(e)}")
        messages.error(request, f"Произошла ошибка: {str(e)}")
        return redirect("/")

@csrf_exempt
def robokassa_failed(request, booking_id):
    """Обработчик для Fail URL"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        booking = get_object_or_404(Booking, booking_id=booking_id)
        logger.info(f"Обработка неудачного платежа для бронирования {booking_id}")
        
        # Если в запросе есть InvId и он еще не сохранен в booking
        inv_id = request.GET.get('InvId') or request.POST.get('InvId')
        if inv_id and booking.robokassa_inv_id is None:
            booking.robokassa_inv_id = int(inv_id)
            logger.info(f"Сохранен InvId {inv_id} в бронировании {booking_id}")
        
        booking.payment_status = "failed"
        booking.save()
        
        # Удаляем данные из сессии
        if 'selection_data_obj' in request.session:
            del request.session['selection_data_obj']
            
        if 'booking_common_data' in request.session:
            del request.session['booking_common_data']
        
        if 'user_data' in request.session:
            del request.session['user_data']
        
        logger.info(f"Статус бронирования {booking_id} обновлен на 'failed'")
        
        context = {
            "booking": booking, 
        }
        return render(request, "hotel/payment_failed.html", context)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке неудачного платежа: {str(e)}")
        messages.error(request, f"Error: {str(e)}")
        return redirect("/")

@csrf_exempt
def robokassa_success_direct(request):
    """Обработчик для Success URL без указания booking_id"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Проверяем, есть ли необходимые параметры в запросе
    if not all(param in request.GET for param in ['OutSum', 'InvId', 'SignatureValue']):
        logger.warning("Отсутствуют обязательные параметры в запросе success от Робокассы")
        messages.error(request, "Ошибка: Недостаточно данных для проверки платежа")
        return redirect('/')
    
    inv_id = request.GET.get('InvId')
    
    # Проверяем подпись
    if not check_success_payment(request.GET):
        logger.warning(f"Неверная подпись платежа в запросе success от Робокассы: InvId={inv_id}")
        messages.error(request, "Ошибка: Верификация платежа не пройдена")
        return redirect('/')
    
    # Если подпись правильная, находим бронирование и обновляем его статус
    try:
        booking = Booking.objects.get(id=int(inv_id))
        logger.info(f"Подпись подтверждена, обрабатываем успешный платеж для бронирования {booking.booking_id}")
        
        # Обновляем статус платежа и сохраняем InvId если он еще не сохранен
        booking.payment_status = "paid"
        
        if booking.robokassa_inv_id is None:
            booking.robokassa_inv_id = int(inv_id)
            logger.info(f"Сохранен InvId {inv_id} в бронировании {booking.booking_id}")
        
        booking.save()
        
        # Удаляем данные из сессии
        if 'selection_data_obj' in request.session:
            del request.session['selection_data_obj']
        
        if 'booking_common_data' in request.session:
            del request.session['booking_common_data']
        
        if 'user_data' in request.session:
            del request.session['user_data']
        
        # Перенаправляем на страницу успеха с указанием booking_id
        return redirect('hotel:robokassa_success', booking_id=booking.booking_id)
    except Exception as e:
        logger.error(f"Ошибка при обработке прямого success URL: {str(e)}")
        messages.error(request, "Ошибка при обработке платежа")
        return redirect('/')

@csrf_exempt
def robokassa_failed_direct(request):
    """Обработчик для Fail URL без указания booking_id"""
    import logging
    logger = logging.getLogger(__name__)
    
    inv_id = request.GET.get('InvId') or request.POST.get('InvId')
    if inv_id:
        try:
            # Сначала пытаемся найти booking по robokassa_inv_id
            try:
                booking = Booking.objects.get(robokassa_inv_id=int(inv_id))
                logger.info(f"Найдено бронирование по robokassa_inv_id: {booking.booking_id}")
            except Booking.DoesNotExist:
                # Если не найдено, пробуем по id
                booking = Booking.objects.get(id=int(inv_id))
                logger.info(f"Найдено бронирование по id: {booking.booking_id}")
                
                # Если InvId еще не сохранен, сохраняем его
                if booking.robokassa_inv_id is None:
                    booking.robokassa_inv_id = int(inv_id)
                    logger.info(f"Сохранен InvId {inv_id} в бронировании {booking.booking_id}")
            
            logger.info(f"Перенаправление с /robokassa/failed/ на страницу неудачного платежа для бронирования {booking.booking_id}")
            # Сразу устанавливаем статус 'failed'
            booking.payment_status = "failed"
            booking.save()
            
            # Удаляем данные из сессии при неудачной оплате
            if 'selection_data_obj' in request.session:
                del request.session['selection_data_obj']
                
            if 'booking_common_data' in request.session:
                del request.session['booking_common_data']
                
            if 'user_data' in request.session:
                del request.session['user_data']
                
            return redirect('hotel:robokassa_failed', booking_id=booking.booking_id)
        except Exception as e:
            logger.error(f"Ошибка при обработке прямого failed URL: {str(e)}")
            return redirect('/')
    logger.warning("InvId не найден в запросе")
    return redirect('/')

@csrf_exempt
def invoice(request, booking_id):
    from django.shortcuts import redirect, get_object_or_404
    from django.contrib import messages
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        booking = get_object_or_404(Booking, booking_id=booking_id)
        
        # Проверяем статус оплаты
        if booking.payment_status != "paid":
            logger.warning(f"Попытка доступа к неоплаченной квитанции: {booking_id}, статус: {booking.payment_status}")
            messages.error(request, "Доступ к квитанции возможен только для оплаченных бронирований.")
            return redirect("/")
        
        context = {
            "booking": booking,  
            "room": booking.room.all(),  
        }
        return render(request, "hotel/invoice.html", context)
    except Exception as e:
        logger.error(f"Ошибка при доступе к квитанции {booking_id}: {str(e)}")
        messages.error(request, f"Произошла ошибка при получении квитанции: {str(e)}")
        return redirect("/")

# Добавим вспомогательную функцию для расчета общей стоимости с учетом динамических цен
def calculate_total_price(room_type, checkin_date, checkout_date):
    """
    Рассчитывает общую стоимость проживания с учетом динамических цен.
    
    Args:
        room_type: Объект модели RoomType
        checkin_date: Дата заезда (datetime.date)
        checkout_date: Дата выезда (datetime.date)
    
    Returns:
        Decimal: Общая стоимость проживания
    """
    from decimal import Decimal
    
    total = Decimal('0.00')
    current_date = checkin_date
    
    # Проходим по всем дням пребывания
    while current_date < checkout_date:
        # Получаем цену для текущего дня
        price_for_day = room_type.get_price_for_date(current_date)
        # Убедимся, что price_for_day - это Decimal, преобразуем явно во избежание ошибок
        total += Decimal(str(price_for_day))
        
        # Переходим к следующему дню
        current_date += timedelta(days=1)
    
    return total