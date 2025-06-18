import boto3
import logging
from botocore.exceptions import ClientError
from django.conf import settings
from django.template.loader import render_to_string
import locale
from datetime import datetime

logger = logging.getLogger(__name__)


class AWSSESEmailSender:
    """Класс для отправки email через AWS SES"""
    
    def __init__(self):
        self.ses_client = boto3.client(
            'ses',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    
    def send_email(self, to_email, subject, html_body, text_body=None, from_email=None):
        """
        Отправка email через AWS SES
        
        Args:
            to_email (str): Email получателя
            subject (str): Тема письма
            html_body (str): HTML содержимое письма
            text_body (str, optional): Текстовое содержимое письма
            from_email (str, optional): Email отправителя
            
        Returns:
            dict: Результат отправки
        """
        if not from_email:
            from_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            # Структура сообщения для SES
            message = {
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': html_body,
                        'Charset': 'UTF-8'
                    }
                }
            }
            
            # Добавляем текстовую версию если она предоставлена
            if text_body:
                message['Body']['Text'] = {
                    'Data': text_body,
                    'Charset': 'UTF-8'
                }
            
            # Отправляем email
            response = self.ses_client.send_email(
                Source=from_email,
                Destination={
                    'ToAddresses': [to_email]
                },
                Message=message
            )
            
            logger.info(f"Email успешно отправлен на {to_email}. MessageId: {response['MessageId']}")
            return {
                'success': True,
                'message_id': response['MessageId'],
                'to_email': to_email
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Ошибка при отправке email на {to_email}: {error_code} - {error_message}")
            return {
                'success': False,
                'error_code': error_code,
                'error_message': error_message,
                'to_email': to_email
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке email на {to_email}: {str(e)}")
            return {
                'success': False,
                'error_message': str(e),
                'to_email': to_email
            }
    
    def send_booking_confirmation_emails(self, booking):
        """
        Отправка email подтверждения бронирования пользователю и отелю
        
        Args:
            booking: Объект бронирования
            
        Returns:
            dict: Результаты отправки email
        """
        results = {
            'user_email': None,
            'hotel_email': None
        }
        
        try:
            # 1. Отправляем email пользователю
            if booking.email:
                user_subject = f"Спасибо за бронирование с eKol! - ID: #{booking.booking_id}"
                user_html_body = self._render_user_email_template(booking)
                user_text_body = self._render_user_email_text(booking)
                
                results['user_email'] = self.send_email(
                    to_email=booking.email,
                    subject=user_subject,
                    html_body=user_html_body,
                    text_body=user_text_body
                )
            
            # 2. Отправляем email отелю
            if booking.hotel and booking.hotel.email:
                hotel_subject = f"Новое подтверждение бронирования - ID: #{booking.booking_id}"
                hotel_html_body = self._render_hotel_email_template(booking)
                hotel_text_body = self._render_hotel_email_text(booking)
                
                results['hotel_email'] = self.send_email(
                    to_email=booking.hotel.email,
                    subject=hotel_subject,
                    html_body=hotel_html_body,
                    text_body=hotel_text_body
                )
        
        except Exception as e:
            logger.error(f"Ошибка при отправке email для бронирования {booking.booking_id}: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _format_date_russian(self, date_obj):
        """Форматирует дату на русском языке"""
        if not date_obj:
            return ""
        
        months_ru = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
            7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        
        weekdays_ru = {
            0: 'понедельник', 1: 'вторник', 2: 'среда', 3: 'четверг', 
            4: 'пятница', 5: 'суббота', 6: 'воскресенье'
        }
        
        if hasattr(date_obj, 'weekday'):
            weekday = weekdays_ru[date_obj.weekday()]
            month = months_ru[date_obj.month]
            return f"{date_obj.day} {month} {date_obj.year} г. ({weekday})"
        else:
            # Если это строка, пытаемся преобразовать
            try:
                from datetime import datetime
                if isinstance(date_obj, str):
                    date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
                    weekday = weekdays_ru[date_obj.weekday()]
                    month = months_ru[date_obj.month]
                    return f"{date_obj.day} {month} {date_obj.year} г. ({weekday})"
            except:
                return str(date_obj)
        
        return str(date_obj)
    
    def _render_user_email_template(self, booking):
        """Формирует HTML шаблон email для пользователя"""
        # Форматируем даты на русском языке
        check_in_date_ru = self._format_date_russian(booking.check_in_date)
        check_out_date_ru = self._format_date_russian(booking.check_out_date)
        
        # Получаем домен из настроек
        domain = getattr(settings, 'WEBSITE_ADDRESS', '').rstrip('/')
        invoice_url = f"{domain}/ru/invoice/{booking.booking_id}/"
        
        context = {
            'booking': booking,
            'user_name': booking.full_name,
            'booking_id': booking.booking_id,
            'hotel_name': booking.hotel.name if booking.hotel else 'Отель',
            'room_type': booking.room_type.type if booking.room_type else 'Номер',
            'check_in_date': check_in_date_ru,
            'check_out_date': check_out_date_ru,
            'total_amount': booking.total,
            'invoice_url': invoice_url,
            'domain': domain,
        }
        
        html_template = """
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
                .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 20px; margin-bottom: 30px; }
                .content { line-height: 1.6; color: #34495e; }
                .booking-details { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; }
                .highlight { color: #e74c3c; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Спасибо за выбор eKol!</h1>
                </div>
                <div class="content">
                    <p>Уважаемый(ая) <strong>{{ user_name }}</strong>,</p>
                    <p>Благодарим вас за использование платформы eKol для бронирования! Ваша оплата успешно обработана.</p>
                    
                    <div class="booking-details">
                        <h3>Детали бронирования:</h3>
                        <p><strong>ID бронирования:</strong> <span class="highlight">{{ booking_id }}</span></p>
                        <p><strong>Отель:</strong> {{ hotel_name }}</p>
                        <p><strong>Тип номера:</strong> {{ room_type }}</p>
                        <p><strong>Дата заезда:</strong> {{ check_in_date }}</p>
                        <p><strong>Дата выезда:</strong> {{ check_out_date }}</p>
                        <p><strong>Общая сумма:</strong> {{ total_amount }} ₸</p>
                    </div>
                    
                    <div class="invoice-section" style="background-color: #e8f4fd; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #3498db;">
                        <h3 style="color: #2980b9; margin-top: 0;">📄 Важно! Документы для заселения</h3>
                        <p><strong>Для успешного заселения в отель вам необходимо:</strong></p>
                        <ol style="margin: 10px 0; padding-left: 20px;">
                            <li>Скачать или распечатать чек бронирования</li>
                            <li>Предоставить чек при заселении в отель</li>
                            <li>Иметь при себе документ, удостоверяющий личность</li>
                        </ol>
                        
                        <div style="text-align: center; margin: 15px 0;">
                            <a href="{{ invoice_url }}" style="display: inline-block; background-color: #3498db; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                                🧾 Скачать чек бронирования
                            </a>
                        </div>
                        
                        <p style="font-size: 14px; color: #7f8c8d; margin-top: 15px;">
                            <strong>Multilingual invoices / Көп тілді шоттар:</strong><br>
                            🇷🇺 Русский: <a href="{{ domain }}/ru/invoice/{{ booking_id }}/" style="color: #3498db;">{{ domain }}/ru/invoice/{{ booking_id }}/</a><br>
                            🇰🇿 Қазақша: <a href="{{ domain }}/kk/invoice/{{ booking_id }}/" style="color: #3498db;">{{ domain }}/kk/invoice/{{ booking_id }}/</a><br>
                            🇬🇧 English: <a href="{{ domain }}/en/invoice/{{ booking_id }}/" style="color: #3498db;">{{ domain }}/en/invoice/{{ booking_id }}/</a>
                        </p>
                    </div>
                    
                    <p>Если у вас есть вопросы, пожалуйста, обращайтесь в службу поддержки eKol.</p>
                    <p>Желаем вам приятного отдыха!</p>
                </div>
                <div class="footer">
                    <p>С уважением,<br>Команда eKol</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        from django.template import Template, Context
        template = Template(html_template)
        return template.render(Context(context))
    
    def _render_user_email_text(self, booking):
        """Формирует текстовую версию email для пользователя"""
        # Форматируем даты на русском языке
        check_in_date_ru = self._format_date_russian(booking.check_in_date)
        check_out_date_ru = self._format_date_russian(booking.check_out_date)
        
        # Получаем домен из настроек
        domain = getattr(settings, 'WEBSITE_ADDRESS', '').rstrip('/')
        
        return f"""
Уважаемый(ая) {booking.full_name},

Спасибо за выбор eKol для бронирования! Ваша оплата успешно обработана.

Детали бронирования:
- ID бронирования: {booking.booking_id}
- Отель: {booking.hotel.name if booking.hotel else 'Отель'}
- Тип номера: {booking.room_type.type if booking.room_type else 'Номер'}
- Дата заезда: {check_in_date_ru}
- Дата выезда: {check_out_date_ru}
- Общая сумма: {booking.total} ₸

📄 ВАЖНО! ДОКУМЕНТЫ ДЛЯ ЗАСЕЛЕНИЯ

Для успешного заселения в отель вам необходимо:
1. Скачать или распечатать чек бронирования
2. Предоставить чек при заселении в отель
3. Иметь при себе документ, удостоверяющий личность

🧾 ССЫЛКА НА ЧЕК БРОНИРОВАНИЯ:
{domain}/ru/invoice/{booking.booking_id}/

Multilingual invoices / Көп тілді шоттар:
🇷🇺 Русский: {domain}/ru/invoice/{booking.booking_id}/
🇰🇿 Қазақша: {domain}/kk/invoice/{booking.booking_id}/
🇬🇧 English: {domain}/en/invoice/{booking.booking_id}/

Если у вас есть вопросы, пожалуйста, обращайтесь в службу поддержки eKol.

Желаем вам приятного отдыха!

С уважением,
Команда eKol
        """
    
    def _render_hotel_email_template(self, booking):
        """Формирует HTML шаблон email для отеля"""
        # Форматируем даты на русском языке
        check_in_date_ru = self._format_date_russian(booking.check_in_date)
        check_out_date_ru = self._format_date_russian(booking.check_out_date)
        
        context = {
            'booking': booking,
            'booking_id': booking.booking_id,
            'guest_name': booking.full_name,
            'room_type': booking.room_type.type if booking.room_type else 'Номер',
            'check_in_date': check_in_date_ru,
            'check_out_date': check_out_date_ru,
            'total_amount': booking.total,
            'guest_email': booking.email,
            'guest_phone': booking.phone,
        }
        
        html_template = """
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }
                .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; color: #2c3e50; border-bottom: 2px solid #27ae60; padding-bottom: 20px; margin-bottom: 30px; }
                .content { line-height: 1.6; color: #34495e; }
                .booking-details { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; }
                .highlight { color: #e74c3c; font-weight: bold; }
                .status { background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; text-align: center; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Новое подтверждение бронирования</h1>
                </div>
                <div class="content">
                    <div class="status">
                        <strong>Бронирование оплачено и подтверждено!</strong>
                    </div>
                    
                    <p>В вашем отеле было оплачено новое бронирование через платформу eKol.</p>
                    
                    <div class="booking-details">
                        <h3>Детали бронирования:</h3>
                        <p><strong>ID бронирования:</strong> <span class="highlight">{{ booking_id }}</span></p>
                        <p><strong>Гость:</strong> {{ guest_name }}</p>
                        <p><strong>Email гостя:</strong> {{ guest_email }}</p>
                        <p><strong>Телефон гостя:</strong> {{ guest_phone }}</p>
                        <p><strong>Тип номера:</strong> {{ room_type }}</p>
                        <p><strong>Дата заезда:</strong> {{ check_in_date }}</p>
                        <p><strong>Дата выезда:</strong> {{ check_out_date }}</p>
                        <p><strong>Общая сумма:</strong> {{ total_amount }} ₸</p>
                    </div>
                    
                    <p>Пожалуйста, подготовьте номер к прибытию гостя.</p>
                </div>
                <div class="footer">
                    <p>С уважением,<br>Команда eKol</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        from django.template import Template, Context
        template = Template(html_template)
        return template.render(Context(context))
    
    def _render_hotel_email_text(self, booking):
        """Формирует текстовую версию email для отеля"""
        # Форматируем даты на русском языке
        check_in_date_ru = self._format_date_russian(booking.check_in_date)
        check_out_date_ru = self._format_date_russian(booking.check_out_date)
        
        return f"""
Новое подтверждение бронирования

БРОНИРОВАНИЕ ОПЛАЧЕНО И ПОДТВЕРЖДЕНО!

В вашем отеле было оплачено новое бронирование через платформу eKol.

Детали бронирования:
- ID бронирования: {booking.booking_id}
- Гость: {booking.full_name}
- Email гостя: {booking.email}
- Телефон гостя: {booking.phone}
- Тип номера: {booking.room_type.type if booking.room_type else 'Номер'}
- Дата заезда: {check_in_date_ru}
- Дата выезда: {check_out_date_ru}
- Общая сумма: {booking.total} ₸

Пожалуйста, подготовьте номер к прибытию гостя.

С уважением,
Команда eKol
        """ 