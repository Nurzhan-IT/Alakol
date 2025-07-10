from django.test import TestCase, Client, RequestFactory
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.conf import settings
from django.http import HttpResponse
from datetime import timedelta, date
from decimal import Decimal
import json
from unittest.mock import patch, MagicMock

from hotel.models import (
    Booking, Hotel, HotelFeatures, HotelGallery, Room, RoomType, 
    RoomTypeGallery, RoomTypeFeatures, Review, Coupon
)
from hotel.services import handle_bookings_payment_status_processing_to_unpaid
from hotel.forms import RoomTypeAdminForm
from hotel.views import hotel_detail, index  # Импортируем тестируемые представления

User = get_user_model()

class BookingTestCase(TestCase):
    def test_handle_expired_bookings(self):
        # Создаём просроченное бронирование
        booking = Booking.objects.create(
            payment_status='processing',
            created_at=timezone.now() - timedelta(minutes=15),
            expires_at=timezone.now() - timedelta(minutes=5),
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=1),
            num_adults=1,
            total=100.00,
            before_discount=100.00,
            saved=0.00,
            total_days=1
        )
        # Выполняем очистку
        result = handle_bookings_payment_status_processing_to_unpaid()
        booking.refresh_from_db()
        self.assertEqual(booking.payment_status, 'unpaid')
        self.assertEqual(result, 'unpaid 1 expired bookings.')


class HotelModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Test Hotel',
            description='A test hotel description',
            image='hotel_gallery/test_image.jpg',
            address='Test Address',
            mobile='1234567890',
            email='hotel@example.com',
            status='Live',
            check_in_time=timezone.now().time(),
            check_out_time=timezone.now().time()
        )
        
        # Создание галереи отеля
        self.hotel_gallery = HotelGallery.objects.create(
            hotel=self.hotel,
            image='hotel_gallery/gallery_image.jpg'
        )
        
        # Создание особенностей отеля
        self.hotel_feature = HotelFeatures.objects.create(
            hotel=self.hotel,
            icon='wifi.png',
            name='Wi-Fi'
        )
        
        # Создание типа номера
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            type='Luxury',
            price=Decimal('100.00'),
            number_of_beds=2,
            room_capacity=4,
            room_size=30
        )
        
        # Создание номера
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_type=self.room_type,
            room_number='101',
            is_available=True
        )
        
    def test_hotel_creation(self):
        """Тест создания модели отеля"""
        self.assertEqual(self.hotel.name, 'Test Hotel')
        self.assertEqual(self.hotel.status, 'Live')
        self.assertEqual(self.hotel.user, self.user)
        
    def test_hotel_str(self):
        """Тест строкового представления модели отеля"""
        self.assertEqual(str(self.hotel), 'Test Hotel')
        
    def test_hotel_gallery(self):
        """Тест получения галереи отеля"""
        galleries = self.hotel.hotel_gallery()
        self.assertEqual(galleries.count(), 1)
        self.assertEqual(galleries.first(), self.hotel_gallery)
        
    def test_hotel_features(self):
        """Тест получения особенностей отеля"""
        features = self.hotel.hotel_features()
        self.assertEqual(features.count(), 1)
        self.assertEqual(features.first(), self.hotel_feature)


class RoomTypeModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Test Hotel',
            description='A test hotel description',
            image='hotel_gallery/test_image.jpg',
            address='Test Address',
            mobile='1234567890',
            email='hotel@example.com',
            status='Live'
        )
        
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            type='Luxury',
            price=Decimal('100.00'),
            number_of_beds=2,
            room_capacity=4,
            room_size=30,
            dynamic_pricing={'2023-12-25': 150.00}
        )
        
        # Создание номеров данного типа
        self.room1 = Room.objects.create(
            hotel=self.hotel,
            room_type=self.room_type,
            room_number='101',
            is_available=True
        )
        
        self.room2 = Room.objects.create(
            hotel=self.hotel,
            room_type=self.room_type,
            room_number='102',
            is_available=True
        )
        
    def test_room_type_creation(self):
        """Тест создания типа номера"""
        self.assertEqual(self.room_type.type, 'Luxury')
        self.assertEqual(self.room_type.price, Decimal('100.00'))
        self.assertEqual(self.room_type.hotel, self.hotel)
        
    def test_room_type_str(self):
        """Тест строкового представления типа номера"""
        self.assertEqual(str(self.room_type), f'Luxury - Test Hotel - {self.room_type.price}')
        
    def test_rooms_count(self):
        """Тест подсчета количества номеров данного типа"""
        self.assertEqual(self.room_type.rooms_count(), 2)
        
    def test_get_price_for_date(self):
        """Тест получения цены для конкретной даты с учетом динамических цен"""
        # Проверка динамической цены на указанную дату
        price_for_christmas = self.room_type.get_price_for_date(date(2023, 12, 25))
        self.assertEqual(price_for_christmas, Decimal('150.00'))
        
        # Проверка обычной цены на обычную дату
        price_for_regular_day = self.room_type.get_price_for_date(date(2023, 12, 1))
        self.assertEqual(price_for_regular_day, Decimal('100.00'))


class RoomModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Test Hotel',
            description='A test hotel description',
            image='hotel_gallery/test_image.jpg',
            address='Test Address',
            mobile='1234567890',
            email='hotel@example.com',
            status='Live'
        )
        
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            type='Luxury',
            price=Decimal('100.00'),
            number_of_beds=2,
            room_capacity=4,
            room_size=30
        )
        
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_type=self.room_type,
            room_number='101',
            is_available=True
        )
        
    def test_room_creation(self):
        """Тест создания номера"""
        self.assertEqual(self.room.room_number, '101')
        self.assertTrue(self.room.is_available)
        self.assertEqual(self.room.hotel, self.hotel)
        self.assertEqual(self.room.room_type, self.room_type)
        
    def test_room_str(self):
        """Тест строкового представления номера"""
        self.assertEqual(str(self.room), f'Test Hotel - Luxury -  Room 101')
        
    def test_price(self):
        """Тест получения цены номера"""
        self.assertEqual(self.room.price(), Decimal('100.00'))
        
    def test_number_of_beds(self):
        """Тест получения количества кроватей в номере"""
        self.assertEqual(self.room.number_of_beds(), 2)


class BookingModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Test Hotel',
            description='A test hotel description',
            image='hotel_gallery/test_image.jpg',
            address='Test Address',
            mobile='1234567890',
            email='hotel@example.com',
            status='Live'
        )
        
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            type='Luxury',
            price=Decimal('100.00'),
            number_of_beds=2,
            room_capacity=4,
            room_size=30
        )
        
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_type=self.room_type,
            room_number='101',
            is_available=True
        )
        
        self.booking = Booking.objects.create(
            user=self.user,
            payment_status='processing',
            full_name='Test User',
            email='test@example.com',
            hotel=self.hotel,
            room_type=self.room_type,
            before_discount=Decimal('100.00'),
            total=Decimal('100.00'),
            saved=Decimal('0.00'),
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=1),
            total_days=1,
            num_adults=2,
            num_children=0,
            created_at=timezone.now(),
            expires_at=timezone.now() + timedelta(minutes=30)
        )
        self.booking.set_rooms_from_objects([self.room])
        
    def test_booking_creation(self):
        """Тест создания бронирования"""
        self.assertEqual(self.booking.full_name, 'Test User')
        self.assertEqual(self.booking.payment_status, 'processing')
        self.assertEqual(self.booking.hotel, self.hotel)
        self.assertEqual(self.booking.room_type, self.room_type)
        self.assertEqual(self.booking.total_days, 1)
        
    def test_booking_str(self):
        """Тест строкового представления бронирования"""
        self.assertEqual(str(self.booking), f'{self.booking.booking_id}')
        
    def test_booking_expires_at(self):
        """Тест установки времени истечения бронирования"""
        self.assertTrue(self.booking.expires_at > timezone.now())
        self.assertTrue(self.booking.expires_at < timezone.now() + timedelta(minutes=31))


class CouponModelTestCase(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code='TEST10',
            type='Percentage',
            discount=10,
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=30),
            active=True,
            make_public=True
        )
        
    def test_coupon_creation(self):
        """Тест создания купона"""
        self.assertEqual(self.coupon.code, 'TEST10')
        self.assertEqual(self.coupon.type, 'Percentage')
        self.assertEqual(self.coupon.discount, 10)
        self.assertTrue(self.coupon.active)
        
    def test_coupon_str(self):
        """Тест строкового представления купона"""
        self.assertEqual(str(self.coupon), 'TEST10')


class ReviewModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Test Hotel',
            description='A test hotel description',
            image='hotel_gallery/test_image.jpg',
            address='Test Address',
            mobile='1234567890',
            email='hotel@example.com',
            status='Live'
        )
        
        self.review = Review.objects.create(
            user=self.user,
            hotel=self.hotel,
            review='Great hotel and service!',
            rating=5,
            active=True
        )
        
    def test_review_creation(self):
        """Тест создания отзыва"""
        self.assertEqual(self.review.review, 'Great hotel and service!')
        self.assertEqual(self.review.rating, 5)
        self.assertTrue(self.review.active)
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.hotel, self.hotel)
        
    def test_review_str(self):
        """Тест строкового представления отзыва"""
        self.assertEqual(str(self.review), f'testuser - {self.review.rating}')


class HotelViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Test Hotel',
            description='A test hotel description',
            image='hotel_gallery/test_image.jpg',
            address='Test Address',
            mobile='1234567890',
            email='hotel@example.com',
            status='Live',
            check_in_time=timezone.now().time(),
            check_out_time=timezone.now().time()
        )
        
        # Форсируем создание и сохранение slug
        if not self.hotel.slug:
            self.hotel.slug = slugify(self.hotel.name) + "-test123"
            self.hotel.save()
        
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            type='Luxury',
            price=Decimal('100.00'),
            number_of_beds=2,
            room_capacity=4,
            room_size=30
        )
        
    def test_index_view(self):
        """Тест маршрутизации к главной странице с учетом i18n"""
        # Очищаем кэш перед тестом
        from django.core.cache import cache
        cache.clear()
        
        # Проверяем правильность URL-маршрутизации
        url = reverse('hotel:index')
        
        # Проверяем, что URL заканчивается на / и содержит разделитель /
        self.assertTrue(url.endswith('/'))
        self.assertTrue('/' in url)
        
        # Используем RequestFactory для создания запроса напрямую
        request = self.factory.get(url)
        request.user = self.user  # Устанавливаем пользователя
        
        # Патчим весь механизм кэширования для тестов
        with patch('hotel.cache_utils.CacheHelper.get_or_set_complex') as mock_cache:
            # Настраиваем мок для возврата списка с нашим тестовым отелем
            mock_cache.return_value = [self.hotel]
            
            # Патчим вызов render
            with patch('hotel.views.render') as mock_render:
                # Настраиваем render для возврата нужного ответа
                mock_render.return_value = HttpResponse(status=200)
                
                # Вызываем представление напрямую
                response = index(request)
                
                # Проверяем код ответа
                self.assertEqual(response.status_code, 200)
                
                # Проверяем, что render был вызван с правильными аргументами
                mock_render.assert_called_once()
                args, kwargs = mock_render.call_args
                self.assertEqual(args[0], request)
                self.assertEqual(args[1], "hotel/index.html")
                # В представлении index контекст передается как третий позиционный аргумент,
                # а не как именованный аргумент context
                self.assertIn("hotel", args[2])
                # Проверяем, что hotel в контексте является списком
                self.assertIsInstance(args[2]["hotel"], list)
    
    def test_hotel_detail_view(self):
        """Тест маршрутизации к детальной странице отеля с учетом i18n"""
        # Проверяем существование URL
        url = reverse('hotel:detail', args=[self.hotel.slug])
        
        # Проверяем структуру URL
        self.assertTrue('/detail/' in url)
        self.assertTrue(url.endswith('/'))
        self.assertTrue(self.hotel.slug in url)
        
        # Используем RequestFactory для создания запроса напрямую
        request = self.factory.get(url)
        request.user = self.user  # Устанавливаем пользователя
        
        # Патчим метод get_object_or_404 внутри представления
        with patch('hotel.views.Hotel.objects.get') as mock_get:
            # Настраиваем мок для возврата нашего объекта отеля
            mock_get.return_value = self.hotel
            
            # Патчим остальные вызовы, чтобы они возвращали пустые данные
            with patch('hotel.views.RoomTypeGallery.objects.filter', return_value=MagicMock()):
                with patch('hotel.views.Review.objects.filter', return_value=MagicMock()):
                    with patch('hotel.views.Bookmark.objects.filter', return_value=MagicMock()):
                        with patch('hotel.views.render') as mock_render:
                            # Настраиваем render для возврата нужного ответа
                            mock_render.return_value = HttpResponse(status=200)
                            
                            # Вызываем представление напрямую
                            response = hotel_detail(request, slug=self.hotel.slug)
                            
                            # Проверяем код ответа
                            self.assertEqual(response.status_code, 200)


class RoomTypeAdminFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Test Hotel',
            description='A test hotel description',
            image='hotel_gallery/test_image.jpg',
            address='Test Address',
            mobile='1234567890',
            email='hotel@example.com',
            status='Live'
        )
    
    def test_dynamic_pricing_input_validation(self):
        """Тест валидации динамических цен в различных сценариях"""
        # Базовые данные формы
        base_form_data = {
            'hotel': self.hotel.id,
            'type': 'Luxury',
            'price': '100.00',
            'number_of_beds': 2,
            'room_capacity': 4,
            'room_size': 30,
        }
        
        # Тест 1: Пустые данные динамических цен (должны быть валидны)
        form_data = base_form_data.copy()
        form_data['dynamic_pricing_input'] = '{}'
        form = RoomTypeAdminForm(data=form_data)
        
        # Выводим ошибки для отладки
        if not form.is_valid():
            self.fail(f"Форма с пустыми динамическими ценами должна быть валидна. Ошибки: {form.errors}")
        
        # Тест 2: Неправильный формат JSON
        form_data = base_form_data.copy()
        form_data['dynamic_pricing_input'] = '{"2023-12-25": 150.00, "2023-12-31" 200.00}'  # отсутствует двоеточие
        form = RoomTypeAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('dynamic_pricing_input', form.errors)
        
        # Тест 3: Неправильный формат даты
        form_data = base_form_data.copy()
        form_data['dynamic_pricing_input'] = '{"2023/12/25": 150.00}'  # неправильный формат даты
        form = RoomTypeAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('dynamic_pricing_input', form.errors)
        
        # Тест 4: Отрицательная цена
        form_data = base_form_data.copy()
        form_data['dynamic_pricing_input'] = '{"2023-12-25": -150.00}'  # отрицательная цена
        form = RoomTypeAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('dynamic_pricing_input', form.errors)


class BookingServiceTestCase(TestCase):
    def setUp(self):
        # Создаём действительное бронирование с expires_at в будущем
        self.active_booking = Booking.objects.create(
            payment_status='processing',
            created_at=timezone.now() - timedelta(minutes=15),
            expires_at=timezone.now() + timedelta(minutes=15),
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=1),
            num_adults=1,
            total=100.00,
            before_discount=100.00,
            saved=0.00,
            total_days=1
        )
        
        # Создаём просроченное бронирование
        self.expired_booking = Booking.objects.create(
            payment_status='processing',
            created_at=timezone.now() - timedelta(minutes=30),
            expires_at=timezone.now() - timedelta(minutes=5),
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=1),
            num_adults=1,
            total=100.00,
            before_discount=100.00,
            saved=0.00,
            total_days=1
        )
        
    def test_handle_expired_bookings(self):
        """Тест обработки просроченных бронирований"""
        result = handle_bookings_payment_status_processing_to_unpaid()
        
        # Проверяем, что только просроченное бронирование было отменено
        self.expired_booking.refresh_from_db()
        self.active_booking.refresh_from_db()
        
        self.assertEqual(self.expired_booking.payment_status, 'unpaid')
        self.assertEqual(self.active_booking.payment_status, 'processing')
        self.assertEqual(result, 'unpaid 1 expired bookings.')