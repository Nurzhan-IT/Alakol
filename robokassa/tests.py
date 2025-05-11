import decimal
import datetime
from unittest import mock
from django.test import TestCase, override_settings
from django.conf import settings

from .robokassa import (
    calculate_signature,
    parse_response,
    check_signature_result,
    generate_payment_link,
    result_payment,
    check_success_payment,
    PAYMENT_URL,
    MERCHANT_LOGIN,
    TEST_PASSWORD_1,
    TEST_PASSWORD_2
)


class RobokassaTestCase(TestCase):
    """Тесты для модуля robokassa.py"""

    def test_calculate_signature(self):
        """Тест функции calculate_signature"""
        # Проверка подписи из нескольких строковых аргументов
        signature = calculate_signature('test', 'login', '100.00', '123')
        self.assertEqual(len(signature), 64)  # SHA256 хеш должен быть 64 символа в длину
        
        # Проверка на известном примере (реальное значение SHA256)
        expected = "f484ff496c3422ec82d90a01ae9cab09e7c06a6af70423102168bacd1f286ca4"
        actual = calculate_signature('test', '100', '1', 'password')
        self.assertEqual(actual, expected)

    def test_parse_response(self):
        """Тест функции parse_response"""
        # Тестирование разбора простого запроса
        query_string = "OutSum=100.00&InvId=123&SignatureValue=abc123"
        result = parse_response(query_string)
        
        self.assertEqual(result["OutSum"], "100.00")
        self.assertEqual(result["InvId"], "123")
        self.assertEqual(result["SignatureValue"], "abc123")
        
        # Тестирование пустой строки
        empty_result = parse_response("")
        self.assertEqual(empty_result, {})
        
        # Тестирование некорректного формата
        incorrect_result = parse_response("key1:value1&key2:value2")
        self.assertEqual(incorrect_result, {})

    def test_check_signature_result(self):
        """Тест функции check_signature_result"""
        # Правильная подпись
        order_number = 123
        received_sum = decimal.Decimal('100.00')
        # Обратите внимание: порядок аргументов в calculate_signature отличается от порядка в check_signature_result
        correct_signature = calculate_signature(received_sum, order_number, "password")
        
        self.assertTrue(check_signature_result(
            order_number, 
            received_sum, 
            correct_signature, 
            "password"
        ))
        
        # Неправильная подпись
        wrong_signature = "wrong_signature"
        self.assertFalse(check_signature_result(
            order_number,
            received_sum,
            wrong_signature,
            "password"
        ))
        
        # Регистр подписи не должен влиять на результат проверки
        upper_signature = correct_signature.upper()
        self.assertTrue(check_signature_result(
            order_number,
            received_sum,
            upper_signature,
            "password"
        ))

    @mock.patch('robokassa.robokassa.datetime')
    def test_generate_payment_link(self, mock_datetime):
        """Тест функции generate_payment_link"""
        # Настраиваем фиксированное время для теста
        mock_now = datetime.datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        mock_datetime.timedelta.side_effect = datetime.timedelta
        
        # Базовые параметры для теста
        cost = decimal.Decimal('100.00')
        number = 123
        description = "Тестовый платеж"
        
        # Тест базового URL без email
        url = generate_payment_link(cost, number, description)
        
        # Проверяем, что URL начинается с правильного адреса
        self.assertTrue(url.startswith(PAYMENT_URL))
        
        # Проверяем наличие всех обязательных параметров
        self.assertIn(f'MerchantLogin={MERCHANT_LOGIN}', url)
        self.assertIn('OutSum=100.00', url)
        self.assertIn('InvId=123', url)
        self.assertIn('Description=', url)
        self.assertIn('IsTest=1', url)
        self.assertIn('Culture=ru', url)
        
        # Проверяем ExpirationDate (текущее время + 9 минут 50 секунд)
        expiration_date = (mock_now + datetime.timedelta(minutes=9, seconds=50)).strftime("%Y-%m-%dT%H:%M:%S")
        self.assertIn(f'ExpirationDate={expiration_date.replace(":", "%3A")}', url)
        
        # Проверяем, что email отсутствует
        self.assertNotIn('Email=', url)
        
        # Тест с указанием email
        email = "test@example.com"
        url_with_email = generate_payment_link(cost, number, description, email)
        self.assertIn('Email=test%40example.com', url_with_email)
        
        # Тест с другой культурой
        url_en = generate_payment_link(cost, number, description, culture='en')
        self.assertIn('Culture=en', url_en)

    def test_result_payment(self):
        """Тест функции result_payment"""
        # Готовим тестовые данные
        cost = decimal.Decimal('100.00')
        number = 123
        
        # Создаем подпись, соответствующую реализации result_payment
        # В result_payment используется check_signature_result(number, cost, signature, password)
        # но в check_signature_result сигнатура создается как calculate_signature(received_sum, order_number, password)
        correct_signature = calculate_signature(cost, number, TEST_PASSWORD_2)
        
        # Тест с правильной подписью
        request_data = {
            'OutSum': str(cost),
            'InvId': str(number),
            'SignatureValue': correct_signature
        }
        
        result = result_payment(request_data)
        self.assertEqual(result, f'OK{number}')
        
        # Тест с неправильной подписью
        request_data_wrong = {
            'OutSum': str(cost),
            'InvId': str(number),
            'SignatureValue': 'wrong_signature'
        }
        
        result_wrong = result_payment(request_data_wrong)
        self.assertEqual(result_wrong, 'bad sign')

    def test_check_success_payment(self):
        """Тест функции check_success_payment"""
        # Готовим тестовые данные
        cost = decimal.Decimal('100.00')
        number = 123
        
        # Создаем подпись, соответствующую реализации check_success_payment
        # В check_success_payment используется check_signature_result(number, cost, signature, password)
        # но в check_signature_result сигнатура создается как calculate_signature(received_sum, order_number, password)
        correct_signature = calculate_signature(cost, number, TEST_PASSWORD_1)
        
        # Тест с правильной подписью
        request_data = {
            'OutSum': str(cost),
            'InvId': str(number),
            'SignatureValue': correct_signature
        }
        
        result = check_success_payment(request_data)
        self.assertTrue(result)
        
        # Тест с неправильной подписью
        request_data_wrong = {
            'OutSum': str(cost),
            'InvId': str(number),
            'SignatureValue': 'wrong_signature'
        }
        
        result_wrong = check_success_payment(request_data_wrong)
        self.assertFalse(result_wrong)
