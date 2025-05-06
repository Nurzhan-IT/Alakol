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



from hotel.models import Coupon, CouponUsers, Hotel, Room, Booking, RoomServices, HotelGallery, HotelFeatures, RoomType, RoomTypeGallery, Notification, Bookmark, Review

from datetime import datetime, timedelta
from decimal import Decimal
import json
import random
import string

# Импорт модуля Робокассы
from robokassa.robokassa import generate_payment_link, result_payment, check_success_payment


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
    context = {
        "hotel":hotel,
        "bookmark":bookmark,
        "reviews":reviews,
        "all_reviews":all_reviews,
        "room_type_images":room_type_images,
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

    if not all([checkin, checkout]):
        messages.warning(request, "Please enter your booking data to check availability.")
        return redirect("booking:booking_data", hotel.slug)
    
    # Конвертируем строки с датами в объекты datetime
    date_format = "%Y-%m-%d"
    user_checkin_date = datetime.strptime(checkin, date_format).date()
    user_checkout_date = datetime.strptime(checkout, date_format).date()
    
    # Получаем все доступные номера данного типа
    rooms = Room.objects.filter(room_type=room_type, is_available=True)
    
    # Получаем ID номеров, которые уже забронированы на указанные даты
    # Учитываем, что в день выезда номер уже доступен (за счет -1 день)
    booked_room_ids = Booking.objects.filter(
        Q(check_in_date__lt=user_checkout_date, check_out_date__gt=user_checkin_date),
        is_active=True,
        payment_status__in=["paid", "processing", "pending"]
    ).values_list('room__id', flat=True).distinct()
    
    # Исключаем забронированные номера из списка доступных
    available_rooms = rooms.exclude(id__in=booked_room_ids)
    
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
    }
    return render(request, "hotel/room_type_detail.html", context)



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
    
    if 'selection_data_obj' in request.session:

        if request.method == "POST":
            # Получаем данные из формы
            full_name = request.POST.get("full_name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            
            # Сохраняем данные пользователя в сессии для последующего использования при оплате
            if 'user_data' not in request.session:
                request.session['user_data'] = {}
                
            request.session['user_data'] = {
                'full_name': full_name,
                'email': email,
                'phone': phone
            }
            
            # Перенаправляем на страницу выбора способа оплаты
            return redirect("hotel:payment_method_selection")

        hotel = None

        for h_id, item in request.session['selection_data_obj'].items():
                
            id = int(item['hotel_id'])
            hotel_id = int(item['hotel_id'])

            checkin = item["checkin"]
            checkout = item["checkout"]
            adult = int(item["adult"])
            children = int(item["children"])
            room_type_ = item["room_type"]
            room_id = int(item["room_id"])
            
            room_type = RoomType.objects.get(id=room_type_)
            room = Room.objects.get(id=room_id)

            date_format = "%Y-%m-%d"
            checkin_date = datetime.strptime(checkin, date_format)
            checout_date = datetime.strptime(checkout, date_format)
            time_difference = checout_date - checkin_date
            total_days = time_difference.days

            room_count += 1
            days = total_days
            price = room_type.price

            room_price = price * room_count
            total = room_price * days
            
            hotel = Hotel.objects.get(id=id)

            request.session['selection_data_obj'][h_id]['room_number'] = room.room_number

        print("hotel ===", hotel)
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
        }

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
    room_count = 0
    
    for h_id, item in request.session['selection_data_obj'].items():
        room_type_ = item["room_type"]
        room_type = RoomType.objects.get(id=room_type_)
        
        date_format = "%Y-%m-%d"
        checkin_date = datetime.strptime(item["checkin"], date_format)
        checkout_date = datetime.strptime(item["checkout"], date_format)
        time_difference = checkout_date - checkin_date
        total_days = time_difference.days
        
        room_count += 1
        price = room_type.price
        
        room_price = price * room_count
        total = room_price * total_days
    
    context = {
        "total": total,
        "user_data": request.session['user_data'],
    }
    
    return render(request, "hotel/payment_method_selection.html", context)

def process_booking(request):
    """Создает бронирование из данных сессии и возвращает booking_id"""
    import logging
    logger = logging.getLogger(__name__)
    
    if 'selection_data_obj' not in request.session or 'user_data' not in request.session:
        messages.warning(request, "Missing booking information!")
        return None
    
    try:
        total = 0
        room_count = 0
        total_days = 0
        
        # Берем первый элемент для общих данных
        first_item = next(iter(request.session['selection_data_obj'].values()))
        hotel_id = int(first_item['hotel_id'])
        hotel = Hotel.objects.get(id=hotel_id)
        checkin = first_item["checkin"]
        checkout = first_item["checkout"]
        adult = int(first_item["adult"])
        children = int(first_item["children"])
        room_type_id = first_item["room_type"]
        room_type = RoomType.objects.get(id=room_type_id)
        
        date_format = "%Y-%m-%d"
        checkin_date = datetime.strptime(checkin, date_format)
        checkout_date = datetime.strptime(checkout, date_format)
        time_difference = checkout_date - checkin_date
        total_days = time_difference.days
        
        # Получаем данные пользователя из сессии
        user_data = request.session['user_data']
        full_name = user_data['full_name']
        email = user_data['email']
        phone = user_data['phone']
        
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
            payment_status="initiated"  # Статус "инициировано"
        )
        
        if request.user.is_authenticated:
            booking.user = request.user
            booking.save()
        
        # Добавляем комнаты к бронированию
        for h_id, item in request.session['selection_data_obj'].items():
            room_id = int(item["room_id"])
            room = Room.objects.get(id=room_id)
            booking.room.add(room)
            
            room_count += 1
            price = room_type.price
            
            room_price = price * room_count
            total = room_price * total_days
        
        # Обновляем сумму бронирования
        booking.total = float(total)
        booking.before_discount = float(total)
        booking.save()
        
        logger.info(f"Создано бронирование {booking.booking_id} на сумму {booking.total}")
        return booking
        
    except Exception as e:
        logger.error(f"Ошибка при создании бронирования: {str(e)}")
        return None

# Обновляем функцию Робокассы для создания бронирования перед платежом
@csrf_exempt
def create_robokassa_payment(request, payment_key=None):
    """Создает URL для перенаправления на платежную страницу Робокассы"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Проверяем доступность номеров перед созданием бронирования
        if payment_key is None and 'selection_data_obj' in request.session:
            unavailable_rooms = []
            
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
                
                # Проверяем, что номер не забронирован на указанные даты
                date_format = "%Y-%m-%d"
                checkin_date = datetime.strptime(item["checkin"], date_format).date()
                checkout_date = datetime.strptime(item["checkout"], date_format).date()
                
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
        if '/ru/' in domain:
            domain = domain.replace('/ru/', '/')
        elif '/en/' in domain:
            domain = domain.replace('/en/', '/')
        
        # Формируем URL-ы для успешной/неудачной оплаты БЕЗ языкового префикса
        success_url = f"{domain}/robokassa/success/"
        fail_url = f"{domain}/robokassa/failed/"
        result_url = f"{domain}/robokassa/result/"
        
        logger.info(f"Success URL: {success_url}")
        logger.info(f"Fail URL: {fail_url}")
        logger.info(f"Result URL: {result_url}")
        
        # Генерируем ссылку на оплату
        payment_link = generate_payment_link(
            cost=booking.total,
            number=int(booking.id),
            description=f"Оплата бронирования #{booking.booking_id}",
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