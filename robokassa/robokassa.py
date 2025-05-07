import decimal
import hashlib
from urllib import parse
from urllib.parse import urlparse
from django.conf import settings
import datetime

# Получение настроек из settings.py
MERCHANT_LOGIN = getattr(settings, 'ROBOKASSA_MERCHANT_LOGIN')
MERCHANT_PASSWORD_1 = getattr(settings, 'ROBOKASSA_MERCHANT_PASSWORD_1')
MERCHANT_PASSWORD_2 = getattr(settings, 'ROBOKASSA_MERCHANT_PASSWORD_2')
TEST_PASSWORD_1 = getattr(settings, 'ROBOKASSA_TEST_PASSWORD_1')
TEST_PASSWORD_2 = getattr(settings, 'ROBOKASSA_TEST_PASSWORD_2')
PAYMENT_URL = "https://auth.robokassa.kz/Merchant/Index.aspx"

# Переключатель тестового/реального режима
USE_TEST_MODE = getattr(settings, 'ROBOKASSA_USE_TEST_MODE')

def calculate_signature(*args) -> str:
    """Create signature MD5."""
    return hashlib.sha256(':'.join(str(arg) for arg in args).encode()).hexdigest()

def parse_response(query_string: str) -> dict:
    """Parse URL query parameters into dictionary."""
    params = {}
    for item in query_string.split('&'):
        if '=' in item:
            key, value = item.split('=', 1)
            params[key] = value
    return params

def check_signature_result(
    order_number: int,
    received_sum: decimal.Decimal,
    received_signature: str,
    password: str
) -> bool:
    """Verify signature for result."""
    signature = calculate_signature(received_sum, order_number, password)
    return signature.lower() == received_signature.lower()

def generate_payment_link(
    cost: decimal.Decimal,
    number: int,
    description: str,
    email: str = None,
    culture: str = "ru",
) -> str:
    """Generate URL for payment redirection."""
    # Выбор пароля в зависимости от режима
    password = TEST_PASSWORD_1 if USE_TEST_MODE else MERCHANT_PASSWORD_1
    is_test = 1 if USE_TEST_MODE else 0

    signature = calculate_signature(
        MERCHANT_LOGIN,
        cost,
        number,
        password
    )


    expiration_date = datetime.datetime.now() + datetime.timedelta(minutes=9, seconds=50)
    # Форматируем дату в формате для Robokassa (YYYY-MM-DDThh:mm:ss)
    expiration_date_formatted = expiration_date.strftime("%Y-%m-%dT%H:%M:%S")

    data = {
        'MerchantLogin': MERCHANT_LOGIN,
        'OutSum': cost,
        'InvId': number,
        'Description': description,
        'SignatureValue': signature,
        'IsTest': is_test,
        'Culture': culture,
        'ExpirationDate': expiration_date_formatted,
    }
    
    # Добавляем email, если он предоставлен
    if email:
        data['Email'] = email
    
    payment_link = f'{PAYMENT_URL}?{parse.urlencode(data)}'
    return payment_link

def result_payment(request_data: dict) -> str:
    """Handle ResultURL notification."""
    cost = decimal.Decimal(request_data.get('OutSum', '0'))
    number = int(request_data.get('InvId', '0'))
    signature = request_data.get('SignatureValue', '')
    
    # Выбор пароля в зависимости от режима
    password = TEST_PASSWORD_2 if USE_TEST_MODE else MERCHANT_PASSWORD_2
    
    if check_signature_result(number, cost, signature, password):
        return f'OK{number}'
    return "bad sign"

def check_success_payment(request_data: dict) -> bool:
    """Verify SuccessURL parameters."""
    cost = decimal.Decimal(request_data.get('OutSum', '0'))
    number = int(request_data.get('InvId', '0'))
    signature = request_data.get('SignatureValue', '')
    
    # Выбор пароля в зависимости от режима
    password = TEST_PASSWORD_1 if USE_TEST_MODE else MERCHANT_PASSWORD_1
    
    return check_signature_result(number, cost, signature, password) 