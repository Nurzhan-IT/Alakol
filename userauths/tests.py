from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.auth.models import AnonymousUser
from unittest.mock import patch, MagicMock
import json

from userauths.models import User, Profile, UserConsent
from userauths.forms import UserRegisterForm
from userauths.utils import save_user_consent, save_registration_consents

User = get_user_model()


class UserAuthsViewsTest(TestCase):
    """Базовый класс для тестов userauths"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )
        
        # Данные для регистрации
        self.valid_registration_data = {
            'full_name': 'New User',
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'terms_consent': 'on',
            'privacy_consent': 'on',
            'personal_data_consent': 'on',
            'marketing_consent': 'on'
        }
        
        # Данные для логина
        self.valid_login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }


class RegisterViewTest(UserAuthsViewsTest):
    """Тесты для RegisterView"""
    
    def test_register_get_anonymous_user(self):
        """Тест GET запроса для анонимного пользователя"""
        response = self.client.get(reverse('userauths:sign-up'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], UserRegisterForm)
    
    def test_register_get_authenticated_user(self):
        """Тест GET запроса для аутентифицированного пользователя"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('userauths:sign-up'))
        
        # Должен редиректить на главную
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('hotel:index'))
        
        # Проверяем предупреждающее сообщение
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        # В тестах USE_I18N=False, поэтому переводы не работают
        self.assertIn('you are already logged in', str(messages[0]))
    
    @patch('userauths.views.save_registration_consents')
    def test_register_post_valid_data(self, mock_save_consents):
        """Тест успешной регистрации с валидными данными"""
        mock_save_consents.return_value = []
        
        response = self.client.post(
            reverse('userauths:sign-up'),
            self.valid_registration_data
        )
        
        # Должен редиректить после успешной регистрации
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('hotel:index'))
        
        # Проверяем, что пользователь создан
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.full_name, 'New User')
        
        # Проверяем, что профиль создан и обновлен
        profile = user.profile
        self.assertEqual(profile.full_name, 'New User')
        
        # Проверяем, что функция сохранения согласий была вызвана
        mock_save_consents.assert_called_once()
    
    def test_register_post_invalid_data(self):
        """Тест регистрации с невалидными данными"""
        invalid_data = self.valid_registration_data.copy()
        invalid_data['email'] = 'invalid-email'  # Невалидный email
        invalid_data['password2'] = 'different-password'  # Пароли не совпадают
        
        response = self.client.post(reverse('userauths:sign-up'), invalid_data)
        
        # Должен остаться на странице регистрации
        self.assertEqual(response.status_code, 200)
        # В тестах USE_I18N=False, поэтому переводы не работают
        self.assertFormError(response.context['form'], 'email', ['Enter a valid email address.'])
    
    def test_register_duplicate_email(self):
        """Тест регистрации с уже существующим email"""
        invalid_data = self.valid_registration_data.copy()
        invalid_data['email'] = 'test@example.com'  # Уже существующий email
        
        response = self.client.post(reverse('userauths:sign-up'), invalid_data)
        
        self.assertEqual(response.status_code, 200)
    
    def test_register_email_case_insensitive(self):
        """Тест что email сохраняется в нижнем регистре"""
        data = self.valid_registration_data.copy()
        data['email'] = 'NEWUSER@EXAMPLE.COM'
        
        with patch('userauths.views.save_registration_consents'):
            response = self.client.post(reverse('userauths:sign-up'), data)
        
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что email сохранился в нижнем регистре
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')


class LoginViewTempTest(UserAuthsViewsTest):
    """Тесты для loginViewTemp"""
    
    def test_login_temp_get_anonymous_user(self):
        """Тест GET запроса для анонимного пользователя"""
        response = self.client.get(reverse('userauths:sign-in'))
        
        self.assertEqual(response.status_code, 200)
    
    def test_login_temp_get_authenticated_user(self):
        """Тест GET запроса для аутентифицированного пользователя"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('userauths:sign-in'))
        
        # Должен редиректить на главную
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('hotel:index'))
    
    def test_login_temp_post_valid_credentials(self):
        """Тест успешного логина с валидными данными"""
        response = self.client.post(
            reverse('userauths:sign-in'),
            self.valid_login_data
        )
        
        # Должен редиректить на главную
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('hotel:index'))
    
    def test_login_temp_post_with_next_parameter(self):
        """Тест логина с параметром next"""
        response = self.client.post(
            reverse('userauths:sign-in') + '?next=/dashboard/',
            self.valid_login_data
        )
        
        # Должен редиректить на указанную страницу
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/dashboard/')
    
    def test_login_temp_post_invalid_password(self):
        """Тест логина с неверным паролем"""
        invalid_data = self.valid_login_data.copy()
        invalid_data['password'] = 'wrongpassword'
        
        response = self.client.post(
            reverse('userauths:sign-in'),
            invalid_data
        )
        
        # Должен остаться на странице логина
        self.assertEqual(response.status_code, 200)
    
    def test_login_temp_post_nonexistent_user(self):
        """Тест логина с несуществующим email"""
        invalid_data = {
            'email': 'nonexistent@example.com',
            'password': 'anypassword'
        }
        
        response = self.client.post(
            reverse('userauths:sign-in'),
            invalid_data
        )
        
        # Должен остаться на странице логина
        self.assertEqual(response.status_code, 200)


class LogoutViewTest(UserAuthsViewsTest):
    """Тесты для LogoutView"""
    
    def test_logout_authenticated_user(self):
        """Тест логаута для аутентифицированного пользователя"""
        # Сначала логинимся
        self.client.login(email='test@example.com', password='testpass123')
        
        # Выполняем логаут
        response = self.client.get(reverse('userauths:sign-out'))
        
        # Должен редиректить на страницу логина
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('userauths:sign-in'))
    
    def test_logout_anonymous_user(self):
        """Тест логаута для анонимного пользователя"""
        response = self.client.get(reverse('userauths:sign-out'))
        
        # Должен редиректить на страницу логина
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('userauths:sign-in'))


class UserConsentUtilsTest(UserAuthsViewsTest):
    """Тесты для утилит работы с согласиями"""
    
    def test_save_user_consent(self):
        """Тест сохранения согласия пользователя"""
        request = RequestFactory().get('/', HTTP_USER_AGENT='Test User Agent')

        consent = save_user_consent(
            user=self.user,
            consent_type='terms_of_use',
            request=request,
            document_version='1.0'
        )
        
        self.assertEqual(consent.user, self.user)
        self.assertEqual(consent.consent_type, 'terms_of_use')
        self.assertEqual(consent.document_version, '1.0')
        self.assertEqual(consent.user_agent, 'Test User Agent')
        self.assertTrue(consent.is_active)
    
    def test_save_registration_consents(self):
        """Тест сохранения согласий при регистрации"""
        request = RequestFactory().get('/', HTTP_USER_AGENT='Test User Agent')

        consent_data = {
            'terms_consent': 'on',
            'privacy_consent': 'on',
            'personal_data_consent': 'on',
            'marketing_consent': None  # Не дано согласие
        }
        
        consents = save_registration_consents(self.user, request, consent_data)
        
        # Должны быть сохранены только 3 согласия
        self.assertEqual(len(consents), 3)
        
        consent_types = [c.consent_type for c in consents]
        self.assertIn('terms_of_use', consent_types)
        self.assertIn('privacy_policy', consent_types)
        self.assertIn('personal_data', consent_types)
        self.assertNotIn('marketing', consent_types)


class UserAuthsIntegrationTest(UserAuthsViewsTest):
    """Интеграционные тесты для userauths"""
    
    def test_full_user_journey(self):
        """Тест полного пути пользователя: регистрация -> логин -> логаут"""
        # 1. Регистрация
        with patch('userauths.views.save_registration_consents'):
            response = self.client.post(
                reverse('userauths:sign-up'),
                self.valid_registration_data
            )
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что пользователь создан
        user = User.objects.get(email='newuser@example.com')
        self.assertTrue(user.is_active)
        
        # 2. Логаут
        response = self.client.get(reverse('userauths:sign-out'))
        self.assertEqual(response.status_code, 302)
        
        # 3. Повторный логин
        login_data = {
            'email': 'newuser@example.com',
            'password': 'complexpass123'
        }
        response = self.client.post(reverse('userauths:sign-in'), login_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('hotel:index'))
