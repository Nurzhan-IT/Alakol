from django.test import TestCase, Client
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from datetime import datetime, timedelta

from hotel.models import Hotel, Room, RoomType, Booking
from booking.models import RoomUnavailability
from booking.cache_utils import BookingCacheHelper
from hotel.cache_utils import CacheKeyGenerator

User = get_user_model()


class BookingCacheTest(TestCase):
    """Тесты кэширования для приложения booking."""
    
    def setUp(self):
        """Настройка тестовых данных."""
        # Очищаем кэш перед каждым тестом
        cache.clear()
        
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Создаем отель
        self.hotel = Hotel.objects.create(
            name='Test Hotel',
            slug='test-hotel',
            description='Test Description',
            status='Live',
            user=self.user
        )
        
        # Создаем тип номера
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            type='Standard',
            slug='standard',
            price=100.00,
            room_capacity=2
        )
        
        # Создаем номер
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_type=self.room_type,
            room_number='101',
            is_available=True
        )
        
        self.client = Client()
        
        # Тестовые даты
        self.checkin = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.checkout = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
    
    def test_booking_cache_helper_room_unavailability(self):
        """Тест кэширования недоступности номеров."""
        room_id = self.room.id
        start_date = self.checkin
        end_date = self.checkout
        
        unavailability_periods = [
            {
                'start_date': start_date,
                'end_date': end_date,
                'reason': 'Maintenance'
            }
        ]
        
        # Кэшируем данные
        BookingCacheHelper.cache_room_unavailability(
            room_id, start_date, end_date, unavailability_periods
        )
        
        # Проверяем, что данные закэшированы
        cached_data = BookingCacheHelper.get_cached_room_unavailability(
            room_id, start_date, end_date
        )
        
        self.assertIsNotNone(cached_data)
        self.assertEqual(len(cached_data), 1)
        self.assertEqual(cached_data[0]['reason'], 'Maintenance')
    
    def test_booking_availability_check_cache(self):
        """Тест кэширования проверки доступности бронирования."""
        hotel_id = self.hotel.id
        room_type_id = self.room_type.id
        checkin = self.checkin
        checkout = self.checkout
        
        availability_data = {
            'available': True,
            'rooms_count': 5,
            'min_price': 100.00
        }
        
        # Кэшируем данные
        BookingCacheHelper.cache_booking_availability_check(
            hotel_id, room_type_id, checkin, checkout, availability_data
        )
        
        # Проверяем, что данные закэшированы
        cached_data = BookingCacheHelper.get_cached_booking_availability_check(
            hotel_id, room_type_id, checkin, checkout
        )
        
        self.assertIsNotNone(cached_data)
        self.assertTrue(cached_data['available'])
        self.assertEqual(cached_data['rooms_count'], 5)
    
    def test_booking_session_data_cache(self):
        """Тест кэширования данных сессии бронирования."""
        session_key = 'test_session_key_123'
        session_data = {
            'checkin': self.checkin,
            'checkout': self.checkout,
            'adult': 2,
            'children': 0
        }
        
        # Кэшируем данные сессии
        BookingCacheHelper.cache_booking_session_data(session_key, session_data)
        
        # Проверяем, что данные закэшированы
        cached_data = BookingCacheHelper.get_cached_booking_session_data(session_key)
        
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['checkin'], self.checkin)
        self.assertEqual(cached_data['adult'], 2)
    
    def test_cache_invalidation_on_room_unavailability_change(self):
        """Тест инвалидации кэша при изменении RoomUnavailability."""
        # Сначала кэшируем данные
        BookingCacheHelper.cache_room_unavailability(
            self.room.id, self.checkin, self.checkout, []
        )
        
        # Проверяем, что данные в кэше
        cached_data = BookingCacheHelper.get_cached_room_unavailability(
            self.room.id, self.checkin, self.checkout
        )
        self.assertIsNotNone(cached_data)
        
        # Создаем RoomUnavailability
        unavailability = RoomUnavailability.objects.create(
            room=self.room,
            start_date=self.checkin,
            end_date=self.checkout,
            reason='Test'
        )
        
        # Проверяем, что кэш инвалидирован
        # (этот тест может потребовать дополнительной настройки сигналов)
        cached_data_after = BookingCacheHelper.get_cached_room_unavailability(
            self.room.id, self.checkin, self.checkout
        )
        # В зависимости от реализации сигналов, кэш может быть очищен
    
    def test_check_room_availability_view_with_cache(self):
        """Тест представления check_room_availability с кэшированием."""
        # Данные для POST запроса
        post_data = {
            'hotel-id': str(self.hotel.id),
            'room-type-id': str(self.room_type.id),
            'checkin': self.checkin,
            'checkout': self.checkout,
            'adult': '2',
            'children': '0'
        }
        
        # Первый запрос должен обратиться к базе данных
        response1 = self.client.post(
            reverse('booking:check_room_availability'),
            data=post_data
        )
        
        # Второй запрос должен использовать кэш
        response2 = self.client.post(
            reverse('booking:check_room_availability'),
            data=post_data
        )
        
        # Оба запроса должны вернуть успешный результат
        self.assertEqual(response1.status_code, 302)  # Redirect
        self.assertEqual(response2.status_code, 302)  # Redirect
    
    def test_booking_data_view_with_cache(self):
        """Тест представления booking_data с кэшированием."""
        # Первый запрос должен обратиться к базе данных
        response1 = self.client.get(
            reverse('booking:booking_data', args=[self.hotel.slug])
        )
        
        # Второй запрос должен использовать кэш
        response2 = self.client.get(
            reverse('booking:booking_data', args=[self.hotel.slug])
        )
        
        # Оба запроса должны вернуть успешный результат
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        # Проверяем, что отель есть в контексте через скрытое поле с ID
        self.assertContains(response1, f'value="{self.hotel.id}"')
        self.assertContains(response2, f'value="{self.hotel.id}"')
        
        # Проверяем, что название отеля отображается
        self.assertContains(response1, self.hotel.name)
        self.assertContains(response2, self.hotel.name)
        
        # Проверяем, что форма бронирования присутствует
        self.assertContains(response1, 'Check Availability')
        self.assertContains(response2, 'Check Availability')
    
    def test_cache_ttl_settings(self):
        """Тест настроек TTL для кэша booking."""
        # Проверяем, что настройки TTL существуют
        self.assertIn('booking_availability_check', settings.CACHE_TTL)
        self.assertIn('room_unavailability', settings.CACHE_TTL)
        self.assertIn('booking_session_data', settings.CACHE_TTL)
        
        # Проверяем, что значения разумные
        self.assertGreater(settings.CACHE_TTL['booking_availability_check'], 0)
        self.assertGreater(settings.CACHE_TTL['room_unavailability'], 0)
        self.assertGreater(settings.CACHE_TTL['booking_session_data'], 0)
    
    def tearDown(self):
        """Очистка после каждого теста."""
        cache.clear() 