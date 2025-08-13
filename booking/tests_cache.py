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
        """Тест того, что кэширование недоступности номеров отключено."""
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
        
        # Пытаемся закэшировать данные (но кэширование отключено)
        BookingCacheHelper.cache_room_unavailability(
            room_id, start_date, end_date, unavailability_periods
        )
        
        # Проверяем, что данные НЕ закэшированы (кэширование отключено)
        cached_data = BookingCacheHelper.get_cached_room_unavailability(
            room_id, start_date, end_date
        )
        
        self.assertIsNone(cached_data)  # Кэширование отключено для данных реального времени
    
    def test_booking_availability_check_cache(self):
        """Тест того, что кэширование проверки доступности бронирования отключено."""
        hotel_id = self.hotel.id
        room_type_id = self.room_type.id
        checkin = self.checkin
        checkout = self.checkout
        
        availability_data = {
            'available': True,
            'rooms_count': 5,
            'min_price': 100.00
        }
        
        # Пытаемся закэшировать данные (но кэширование отключено)
        BookingCacheHelper.cache_booking_availability_check(
            hotel_id, room_type_id, checkin, checkout, availability_data
        )
        
        # Проверяем, что данные НЕ закэшированы (кэширование отключено)
        cached_data = BookingCacheHelper.get_cached_booking_availability_check(
            hotel_id, room_type_id, checkin, checkout
        )
        
        self.assertIsNone(cached_data)  # Кэширование отключено для данных реального времени
    
    def test_booking_session_data_cache(self):
        """Тест того, что кэширование данных сессии бронирования отключено."""
        session_key = 'test_session_key_123'
        session_data = {
            'checkin': self.checkin,
            'checkout': self.checkout,
            'adult': 2,
            'children': 0
        }
        
        # Пытаемся закэшировать данные сессии (но кэширование отключено)
        BookingCacheHelper.cache_booking_session_data(session_key, session_data)
        
        # Проверяем, что данные НЕ закэшированы (кэширование отключено)
        cached_data = BookingCacheHelper.get_cached_booking_session_data(session_key)
        
        self.assertIsNone(cached_data)  # Кэширование отключено для данных реального времени
    
    def test_cache_invalidation_on_room_unavailability_change(self):
        """Тест того, что кэширование отключено и инвалидация не требуется."""
        # Пытаемся закэшировать данные (но кэширование отключено)
        BookingCacheHelper.cache_room_unavailability(
            self.room.id, self.checkin, self.checkout, []
        )
        
        # Проверяем, что данные НЕ в кэше (кэширование отключено)
        cached_data = BookingCacheHelper.get_cached_room_unavailability(
            self.room.id, self.checkin, self.checkout
        )
        self.assertIsNone(cached_data)  # Кэширование отключено
        
        # Создаем RoomUnavailability
        unavailability = RoomUnavailability.objects.create(
            room=self.room,
            start_date=self.checkin,
            end_date=self.checkout,
            reason='Test'
        )
        
        # Проверяем, что кэш по-прежнему пуст (кэширование отключено)
        cached_data_after = BookingCacheHelper.get_cached_room_unavailability(
            self.room.id, self.checkin, self.checkout
        )
        self.assertIsNone(cached_data_after)  # Кэширование отключено для данных реального времени
    
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
        self.assertContains(response1, 'Проверить свободные номера')
        self.assertContains(response2, 'Проверить свободные номера')
    
    def test_cache_ttl_settings(self):
        """Тест настроек TTL для кэша booking."""
        # Проверяем, что основные настройки TTL существуют
        self.assertIn('hotels_list', settings.CACHE_TTL)
        self.assertIn('hotel_detail', settings.CACHE_TTL)
        self.assertIn('search_results', settings.CACHE_TTL)
        self.assertIn('static_content', settings.CACHE_TTL)
        
        # Проверяем, что значения разумные
        self.assertGreater(settings.CACHE_TTL['hotels_list'], 0)
        self.assertGreater(settings.CACHE_TTL['hotel_detail'], 0)
        
        # Проверяем, что настройки для данных реального времени отключены
        # (эти настройки закомментированы для обеспечения данных реального времени)
        self.assertNotIn('room_availability', settings.CACHE_TTL)
        self.assertNotIn('room_unavailability', settings.CACHE_TTL)
        self.assertNotIn('booking_availability_check', settings.CACHE_TTL)
        self.assertNotIn('booking_session_data', settings.CACHE_TTL)
        self.assertNotIn('booking_data', settings.CACHE_TTL)
        self.assertNotIn('user_bookings', settings.CACHE_TTL)
        self.assertNotIn('dynamic_pricing', settings.CACHE_TTL)
    
    def tearDown(self):
        """Очистка после каждого теста."""
        cache.clear() 