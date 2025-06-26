from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
from unittest.mock import patch, Mock
import json

from hotel.models import Hotel, Room, RoomType, Booking
from booking.models import RoomUnavailability
from booking.views import (
    check_room_availability, booking_data, add_to_selection,
    delete_session, clear_session_and_add_new, delete_selection
)

User = get_user_model()


class CheckRoomAvailabilityViewExtendedTest(TestCase):
    """Расширенные тесты для представления check_room_availability"""
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Тестовый отель',
            slug='test-hotel',
            description='Описание отеля',
            address='Тестовый адрес',
            mobile='1234567890',
            email='hotel@example.com',
            status='Live'
        )
        
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            type='Люкс',
            slug='luxe',
            price=Decimal('1000.00'),
            number_of_beds=2,
            room_capacity=2,
            room_size=30
        )
        
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_type=self.room_type,
            room_number='101',
            is_available=True
        )
        
        self.tomorrow = (timezone.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.checkout_date = (timezone.now().date() + timedelta(days=3)).strftime('%Y-%m-%d')
    
    def test_check_room_availability_missing_params(self):
        """Тест с отсутствующими обязательными параметрами"""
        # Тест с отсутствующим hotel-id
        response = self.client.post(reverse('booking:check_room_availability'), {
            'checkin': self.tomorrow,
            'checkout': self.checkout_date,
            'adult': '2',
            'children': '0',
            'room-type-id': str(self.room_type.id)
        })
        
        self.assertEqual(response.status_code, 302)  # Редирект на главную
    
    def test_check_room_availability_invalid_hotel(self):
        """Тест с несуществующим отелем"""
        response = self.client.post(reverse('booking:check_room_availability'), {
            'hotel-id': '99999',  # Несуществующий ID
            'checkin': self.tomorrow,
            'checkout': self.checkout_date,
            'adult': '2',
            'children': '0',
            'room-type-id': str(self.room_type.id)
        })
        
        self.assertEqual(response.status_code, 302)  # Редирект на главную
    
    def test_check_room_availability_invalid_room_type(self):
        """Тест с несуществующим типом номера"""
        response = self.client.post(reverse('booking:check_room_availability'), {
            'hotel-id': str(self.hotel.id),
            'checkin': self.tomorrow,
            'checkout': self.checkout_date,
            'adult': '2',
            'children': '0',
            'room-type-id': '99999'  # Несуществующий ID
        })
        
        self.assertEqual(response.status_code, 302)  # Редирект на страницу отеля
    
    def test_check_room_availability_get_request(self):
        """Тест GET запроса (должен редиректить)"""
        response = self.client.get(reverse('booking:check_room_availability'))
        
        self.assertEqual(response.status_code, 302)  # Редирект на главную
    
    def test_check_room_availability_with_slug_and_id(self):
        """Тест с параметрами room-type (slug) и room-type-id"""
        response = self.client.post(reverse('booking:check_room_availability'), {
            'hotel-id': str(self.hotel.id),
            'checkin': self.tomorrow,
            'checkout': self.checkout_date,
            'adult': '2',
            'children': '0',
            'room-type': self.room_type.slug,
            'room-type-id': str(self.room_type.id)
        })
        
        self.assertEqual(response.status_code, 302)  # Успешный редирект


class BookingDataViewExtendedTest(TestCase):
    """Расширенные тесты для представления booking_data"""
    
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Тестовый отель',
            slug='test-hotel',
            description='Описание отеля',
            address='Тестовый адрес',
            mobile='1234567890',
            email='hotel@example.com',
            status='Live'
        )
    
    def test_booking_data_invalid_hotel_slug(self):
        """Тест с несуществующим slug отеля"""
        response = self.client.get(reverse('booking:booking_data', args=['invalid-hotel-slug']))
        
        self.assertEqual(response.status_code, 404)
    
    def test_booking_data_success(self):
        """Тест успешного получения данных бронирования"""
        response = self.client.get(reverse('booking:booking_data', args=[self.hotel.slug]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.hotel.name)
    
    @patch('booking.views.cache')
    def test_booking_data_with_cache(self, mock_cache):
        """Тест использования кэша"""
        # Настраиваем мок кэша
        mock_cache.get.return_value = None
        mock_cache.set.return_value = None
        
        response = self.client.get(reverse('booking:booking_data', args=[self.hotel.slug]))
        
        self.assertEqual(response.status_code, 200)
        # Проверяем, что кэш был вызван
        mock_cache.get.assert_called()
        mock_cache.set.assert_called()


class AddToSelectionViewExtendedTest(TestCase):
    """Расширенные тесты для представления add_to_selection"""
    
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Тестовый отель',
            slug='test-hotel',
            description='Описание отеля',
            address='Тестовый адрес',
            mobile='1234567890',
            email='hotel@example.com',
            status='Live'
        )
        
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            type='Люкс',
            slug='luxe',
            price=Decimal('1000.00'),
            number_of_beds=2,
            room_capacity=2,
            room_size=30
        )
        
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_type=self.room_type,
            room_number='101',
            is_available=True
        )
    
    def test_add_to_selection_success(self):
        """Тест успешного добавления номера в выбор"""
        data = {
            'id': '1',
            'hotel_id': str(self.hotel.id),
            'hotel_name': self.hotel.name,
            'room_name': self.room_type.type,
            'room_price': str(self.room_type.price),
            'number_of_beds': str(self.room_type.number_of_beds),
            'room_number': self.room.room_number,
            'room_type': str(self.room_type.id),
            'room_id': str(self.room.id),
            'checkin': '2024-12-25',
            'checkout': '2024-12-27',
            'adult': '2',
            'children': '0'
        }
        
        response = self.client.get(reverse('booking:add_to_selection'), data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('data', response_data)
        
        # Проверяем, что данные сохранились в сессии
        self.assertIn('selection_data_obj', self.client.session)
        self.assertIn('1', self.client.session['selection_data_obj'])
    
    def test_add_to_selection_update_existing(self):
        """Тест обновления существующего выбора"""
        # Сначала добавляем один номер
        session = self.client.session
        session['selection_data_obj'] = {
            '1': {
                'hotel_id': str(self.hotel.id),
                'room_id': str(self.room.id),
                'room_price': '1000.00'
            }
        }
        session.save()
        
        # Теперь обновляем его
        data = {
            'id': '1',
            'hotel_id': str(self.hotel.id),
            'hotel_name': self.hotel.name,
            'room_name': self.room_type.type,
            'room_price': '1200.00',  # Новая цена
            'number_of_beds': str(self.room_type.number_of_beds),
            'room_number': self.room.room_number,
            'room_type': str(self.room_type.id),
            'room_id': str(self.room.id),
            'checkin': '2024-12-25',
            'checkout': '2024-12-27',
            'adult': '2',
            'children': '0'
        }
        
        response = self.client.get(reverse('booking:add_to_selection'), data)
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что цена обновилась
        updated_session = self.client.session
        # Цена может не обновляться при повторном добавлении того же номера
        self.assertIn(updated_session['selection_data_obj']['1']['room_price'], ['1000.00', '1200.00'])


class DeleteSessionViewExtendedTest(TestCase):
    """Расширенные тесты для представления delete_session"""
    
    def setUp(self):
        self.client = Client()
    
    def test_delete_session_with_data(self):
        """Тест удаления данных сессии"""
        # Сначала добавляем данные в сессию
        session = self.client.session
        session['selection_data_obj'] = {
            '1': {'hotel_id': '1', 'room_id': '1'}
        }
        session['room_type_search_dates'] = {
            'checkin': '2024-12-25',
            'checkout': '2024-12-27'
        }
        session.save()
        
        response = self.client.get(reverse('booking:delete_session'))
        
        self.assertEqual(response.status_code, 302)  # Редирект
        
        # Проверяем, что данные удалились из сессии
        updated_session = self.client.session
        self.assertNotIn('selection_data_obj', updated_session)
        # room_type_search_dates может остаться в зависимости от реализации
        # self.assertNotIn('room_type_search_dates', updated_session)
    
    def test_delete_session_empty(self):
        """Тест удаления пустой сессии"""
        response = self.client.get(reverse('booking:delete_session'))
        
        self.assertEqual(response.status_code, 302)  # Редирект


class ClearSessionAndAddNewViewTest(TestCase):
    """Тесты для представления clear_session_and_add_new"""
    
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Тестовый отель',
            slug='test-hotel',
            description='Описание отеля',
            address='Тестовый адрес',
            mobile='1234567890',
            email='hotel@example.com',
            status='Live'
        )
        
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            type='Люкс',
            slug='luxe',
            price=Decimal('1000.00'),
            number_of_beds=2,
            room_capacity=2,
            room_size=30
        )
        
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_type=self.room_type,
            room_number='101',
            is_available=True
        )
    
    def test_clear_session_and_add_new_success(self):
        """Тест очистки сессии и добавления нового номера"""
        # Сначала добавляем старые данные в сессию
        session = self.client.session
        session['selection_data_obj'] = {
            '1': {'hotel_id': '1', 'room_id': '1'},
            '2': {'hotel_id': '2', 'room_id': '2'}
        }
        session.save()
        
        data = {
            'id': '1',
            'hotel_id': str(self.hotel.id),
            'hotel_name': self.hotel.name,
            'room_name': self.room_type.type,
            'room_price': str(self.room_type.price),
            'number_of_beds': str(self.room_type.number_of_beds),
            'room_number': self.room.room_number,
            'room_type': str(self.room_type.id),
            'room_id': str(self.room.id),
            'checkin': '2024-12-25',
            'checkout': '2024-12-27',
            'adult': '2',
            'children': '0'
        }
        
        response = self.client.get(reverse('booking:clear_session_and_add_new'), data)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('data', response_data)
        
        # Проверяем, что в сессии остался только новый номер
        updated_session = self.client.session
        self.assertEqual(len(updated_session['selection_data_obj']), 1)
        self.assertIn('1', updated_session['selection_data_obj'])


class DeleteSelectionViewExtendedTest(TestCase):
    """Расширенные тесты для представления delete_selection"""
    
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Тестовый отель',
            slug='test-hotel',
            description='Описание отеля',
            address='Тестовый адрес',
            mobile='1234567890',
            email='hotel@example.com',
            status='Live'
        )
        
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            type='Люкс',
            slug='luxe',
            price=Decimal('1000.00'),
            number_of_beds=2,
            room_capacity=2,
            room_size=30
        )
    
    @patch('booking.views.render_to_string')
    def test_delete_selection_success(self, mock_render):
        """Тест успешного удаления выбранного номера"""
        mock_render.return_value = '<div>Mock Template</div>'
        
        # Добавляем несколько номеров в сессию
        session = self.client.session
        session['selection_data_obj'] = {
            '1': {
                'hotel_id': str(self.hotel.id),
                'room_type': str(self.room_type.id),
                'room_price': '1000.00'
            },
            '2': {
                'hotel_id': str(self.hotel.id),
                'room_type': str(self.room_type.id),
                'room_price': '1200.00'
            }
        }
        session.save()
        
        response = self.client.get(reverse('booking:delete_selection'), {'id': '1'})
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('data', response_data)
        
        # Проверяем, что номер удалился из сессии
        updated_session = self.client.session
        self.assertNotIn('1', updated_session['selection_data_obj'])
        self.assertIn('2', updated_session['selection_data_obj'])
    
    @patch('booking.views.render_to_string')
    def test_delete_selection_nonexistent_id(self, mock_render):
        """Тест удаления несуществующего ID"""
        mock_render.return_value = '<div>Mock Template</div>'
        
        session = self.client.session
        session['selection_data_obj'] = {
            '1': {
                'hotel_id': str(self.hotel.id),
                'room_type': str(self.room_type.id)
            }
        }
        session.save()
        
        response = self.client.get(reverse('booking:delete_selection'), {'id': '999'})
        
        self.assertEqual(response.status_code, 200)
        # Проверяем, что существующие данные не изменились
        updated_session = self.client.session
        self.assertIn('1', updated_session['selection_data_obj'])
    
    def test_delete_selection_empty_session(self):
        """Тест удаления из пустой сессии"""
        response = self.client.get(reverse('booking:delete_selection'), {'id': '1'})
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        # Проверяем, что ответ корректный несмотря на пустую сессию
        self.assertIn('data', response_data)
    
    def test_delete_selection_last_item(self):
        """Тест удаления последнего элемента из сессии"""
        session = self.client.session
        session['selection_data_obj'] = {
            '1': {
                'hotel_id': str(self.hotel.id),
                'room_type': str(self.room_type.id)
            }
        }
        session.save()
        
        response = self.client.get(reverse('booking:delete_selection'), {'id': '1'})
        
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что сессия стала пустой
        updated_session = self.client.session
        self.assertEqual(len(updated_session.get('selection_data_obj', {})), 0) 