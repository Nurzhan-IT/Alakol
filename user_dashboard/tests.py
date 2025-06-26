from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from decimal import Decimal
from datetime import date, timedelta
import json
from unittest.mock import patch, MagicMock

from hotel.models import Booking, Notification, Bookmark, Hotel, Review, Room, RoomType
from userauths.models import Profile, User
from userauths.forms import ProfileUpdateForm, UserUpdateForm

User = get_user_model()


class UserDashboardViewsTest(TestCase):
    """Базовый класс для тестов user_dashboard"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        
        # Создаем пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )
        
        # Создаем второго пользователя для некоторых тестов
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Создаем отель
        self.hotel = Hotel.objects.create(
            user=self.user,
            name='Test Hotel',
            slug='test-hotel',
            description='Test Description',
            address='Test Address',
            mobile='1234567890',
            email='hotel@test.com',
            status='Live',
            image='default.jpg'  # Добавляем заглушку для изображения
        )
        
        # Создаем тип номера
        self.room_type = RoomType.objects.create(
            hotel=self.hotel,
            type='Standard',
            slug='standard',
            price=Decimal('1000.00'),
            number_of_beds=1,
            room_capacity=2,
            room_size=25
        )
        
        # Создаем номер
        self.room = Room.objects.create(
            hotel=self.hotel,
            room_type=self.room_type,
            room_number='101',
            is_available=True
        )
        
        # Создаем бронирование
        self.booking = Booking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room_type=self.room_type,
            check_in_date=date.today() + timedelta(days=1),
            check_out_date=date.today() + timedelta(days=3),
            total_days=2,
            num_adults=2,
            num_children=0,
            total=Decimal('2000.00'),
            before_discount=Decimal('2000.00'),
            saved=Decimal('0.00'),
            payment_status='paid',
            is_active=True
        )
        
        # Создаем уведомление
        self.notification = Notification.objects.create(
            user=self.user,
            booking=self.booking,
            type='booking_confirmed',
            seen=False
        )
        
        # Создаем закладку
        self.bookmark = Bookmark.objects.create(
            user=self.user,
            hotel=self.hotel
        )


class DashboardViewTest(UserDashboardViewsTest):
    """Тесты для dashboard view"""
    
    def test_dashboard_authenticated_user(self):
        """Тест dashboard для аутентифицированного пользователя"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('bookings', response.context)
        self.assertIn('total_spent', response.context)
        
        # Проверяем, что показываются только оплаченные бронирования
        bookings = response.context['bookings']
        self.assertEqual(bookings.count(), 1)
        self.assertEqual(bookings.first().payment_status, 'paid')
    
    def test_dashboard_unauthenticated_user(self):
        """Тест dashboard для неаутентифицированного пользователя"""
        response = self.client.get(reverse('dashboard:dashboard'))
        
        # Должен редиректить на страницу логина
        self.assertEqual(response.status_code, 302)


class BookingDetailViewTest(UserDashboardViewsTest):
    """Тесты для booking_detail view"""
    
    def test_booking_detail_success(self):
        """Тест успешного просмотра деталей бронирования"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(
            reverse('dashboard:booking_detail', args=[self.booking.booking_id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['booking'], self.booking)
    
    def test_booking_detail_not_found(self):
        """Тест с несуществующим ID бронирования"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(
            reverse('dashboard:booking_detail', args=['invalid-booking-id'])
        )
        
        self.assertEqual(response.status_code, 404)


class BookingsViewTest(UserDashboardViewsTest):
    """Тесты для bookings view"""
    
    def test_bookings_list_success(self):
        """Тест успешного отображения списка бронирований"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard:bookings'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('bookings', response.context)
        self.assertEqual(response.context['bookings'].count(), 1)


class NotificationsViewTest(UserDashboardViewsTest):
    """Тесты для notifications view"""
    
    def test_notifications_success(self):
        """Тест успешного отображения уведомлений"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard:notifications'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('notifications', response.context)
        self.assertEqual(response.context['notifications'].count(), 1)


class WalletViewTest(UserDashboardViewsTest):
    """Тесты для wallet view"""
    
    def test_wallet_success(self):
        """Тест успешного отображения кошелька"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard:wallet'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('bookings', response.context)
        self.assertIn('total_spent', response.context)


class BookmarkViewTest(UserDashboardViewsTest):
    """Тесты для bookmark view"""
    
    def test_bookmark_data_logic(self):
        """Тест логики получения данных закладок"""
        # Проверяем, что закладка создается правильно
        from hotel.models import Bookmark
        bookmarks = Bookmark.objects.filter(user=self.user)
        self.assertEqual(bookmarks.count(), 1)
        self.assertEqual(bookmarks.first().hotel, self.hotel)


class DeleteBookmarkViewTest(UserDashboardViewsTest):
    """Тесты для delete_bookmark view"""
    
    def test_delete_bookmark_success(self):
        """Тест успешного удаления закладки"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(
            reverse('dashboard:delete_bookmark', args=[self.bookmark.bid])
        )
        
        # Должен редиректить обратно к закладкам
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard:bookmark'))
        
        # Закладка должна быть удалена
        self.assertFalse(Bookmark.objects.filter(bid=self.bookmark.bid).exists())


class AddToBookmarkViewTest(UserDashboardViewsTest):
    """Тесты для add_to_bookmark AJAX view"""
    
    def test_add_bookmark_authenticated_user(self):
        """Тест добавления в закладки для аутентифицированного пользователя"""
        # Удаляем существующую закладку
        self.bookmark.delete()
        
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(
            reverse('dashboard:add_to_bookmark'),
            {'id': self.hotel.id}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['data'], 'Hotel Bookmarked')
        self.assertEqual(data['icon'], 'success')
    
    def test_add_bookmark_unauthenticated_user(self):
        """Тест добавления в закладки для неаутентифицированного пользователя"""
        response = self.client.get(
            reverse('dashboard:add_to_bookmark'),
            {'id': self.hotel.id}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['data'], 'Login To Bookmark Hotel')
        self.assertEqual(data['icon'], 'warning')


class ProfileViewTest(UserDashboardViewsTest):
    """Тесты для profile view"""
    
    def test_profile_get_success(self):
        """Тест успешного отображения профиля"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard:profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('profile', response.context)
        self.assertIn('u_form', response.context)
        self.assertIn('p_form', response.context)
    
    def test_profile_post_success(self):
        """Тест успешного обновления профиля"""
        self.client.login(email='test@example.com', password='testpass123')
        
        data = {
            'email': 'updated@example.com',
            'full_name': 'Updated Name',
            'phone': '+1234567890',
            'gender': 'male',
            'country': 'Kazakhstan',
            'city': 'Almaty',
            'address': 'Test Address 123'
        }
        
        response = self.client.post(reverse('dashboard:profile'), data)
        
        # Должен редиректить после успешного обновления
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard:profile'))


class NotificationMarkAsSeenViewTest(UserDashboardViewsTest):
    """Тесты для notification_mark_as_seen AJAX view"""
    
    def test_mark_notification_as_seen_success(self):
        """Тест успешного отмечания уведомления как прочитанного"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(
            reverse('dashboard:notification_mark_as_seen'),
            {'id': self.notification.id}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['data'], 'Marked As Seen')


class AddReviewViewTest(UserDashboardViewsTest):
    """Тесты для add_review AJAX view"""
    
    def test_add_review_success(self):
        """Тест успешного добавления отзыва"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(
            reverse('dashboard:add_review'),
            {
                'id': self.hotel.id,
                'rating': 5,
                'review': 'Great hotel!'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['data'], 'Review Submitted, Thank You')
        self.assertEqual(data['icon'], 'success')


class PasswordChangedViewTest(UserDashboardViewsTest):
    """Тесты для password_changed view"""
    
    def test_password_changed_success(self):
        """Тест успешного отображения страницы смены пароля"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('dashboard:password_changed'))
        
        self.assertEqual(response.status_code, 200)
