# Интеграция с Робокассой

Этот модуль предоставляет интеграцию с платежной системой Робокасса (Казахстан) для проекта Django.

## Настройка

В файле `settings.py` добавлены следующие параметры:

```python
# Robokassa Settings
ROBOKASSA_MERCHANT_LOGIN = 'TEST_HMS'
ROBOKASSA_MERCHANT_PASSWORD_1 = 'your_merchant_password_1'  # Пароль #1 (реальный)
ROBOKASSA_MERCHANT_PASSWORD_2 = 'your_merchant_password_2'  # Пароль #2 (реальный)
ROBOKASSA_TEST_PASSWORD_1 = 'your_test_password_1'    # Тестовый пароль #1
ROBOKASSA_TEST_PASSWORD_2 = 'your_test_password_2'    # Тестовый пароль #2
ROBOKASSA_USE_TEST_MODE = True  # Использовать тестовый режим
```

## URL-маршруты

В приложении `hotel/urls.py` добавлены следующие URL-маршруты:

```python
# Robokassa Payment API
path('api/robokassa-payment/<booking_id>/', views.create_robokassa_payment, name='api_robokassa_payment'),
path('robokassa/result/', views.robokassa_result, name='robokassa_result'),
path('robokassa/success/<booking_id>/', views.robokassa_success, name='robokassa_success'),
path('robokassa/failed/<booking_id>/', views.robokassa_failed, name='robokassa_failed'),
```

## Настройка Result/Success/Fail URL в личном кабинете Робокассы

В личном кабинете Робокассы необходимо указать следующие URL:

- **Result Url**: `https://your-domain.com/hotel/robokassa/result/`
- **Success Url**: `https://your-domain.com/hotel/robokassa/success/{пустое поле}/`
- **Fail Url**: `https://your-domain.com/hotel/robokassa/failed/{пустое поле}/`

Для каждого URL установите метод отсылки данных **POST**.

## Использование в шаблонах

В шаблоне `checkout.html` добавлена кнопка для оплаты через Робокассу:

```html
<div class="payment-options margin-top-20">
  <button class="button" id="robokassa-button">{% trans "Pay with Robokassa" %}</button>
</div>
```

И JavaScript-код для обработки нажатия:

```javascript
document.getElementById('robokassa-button').addEventListener('click', function(e) {
  e.preventDefault();
  
  fetch('{% url "hotel:api_robokassa_payment" booking.booking_id %}', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': '{{ csrf_token }}'
    },
    body: JSON.stringify({})
  })
  .then(response => response.json())
  .then(data => {
    window.location.href = data.payment_url;
  })
  .catch(error => {
    console.error('Error:', error);
  });
});
```

## Тестирование

Для тестирования используйте:

1. Установите `ROBOKASSA_USE_TEST_MODE = True` в настройках
2. Для проведения тестового платежа используйте любую банковскую карту
3. Следуйте инструкциям на странице оплаты Робокассы
4. Успешный платеж перенаправит на страницу Success Url
5. Отмененный платеж перенаправит на страницу Fail Url

## Смена на боевой режим

Когда вы будете готовы к использованию в боевом режиме:

1. Измените `ROBOKASSA_USE_TEST_MODE = False` в настройках
2. Убедитесь, что указаны правильные пароли для боевого режима
3. Обновите URL-адреса в личном кабинете Робокассы, если изменился домен 