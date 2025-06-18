from django.core.management.base import BaseCommand
from django.conf import settings
from hotel.models import Booking, Hotel
from hotel.aws_ses import AWSSESEmailSender
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Тестирует отправку email через AWS SES'

    def add_arguments(self, parser):
        parser.add_argument(
            '--booking-id',
            type=str,
            help='ID бронирования для тестирования email',
        )
        parser.add_argument(
            '--test-email',
            type=str,
            help='Email для тестовой отправки',
        )
        parser.add_argument(
            '--test-basic',
            action='store_true',
            help='Выполнить базовый тест отправки email',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_NOT_MODIFIED('Тестирование AWS SES...'))
        
        # Проверяем настройки AWS SES
        if not all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_REGION]):
            self.stdout.write(
                self.style.ERROR(
                    'AWS SES не настроен. Проверьте переменные окружения: '
                    'AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION'
                )
            )
            return
        
        try:
            ses_sender = AWSSESEmailSender()
            
            # Базовый тест
            if options['test_basic']:
                self.test_basic_email(ses_sender, options['test_email'])
            
            # Тест с конкретным бронированием
            elif options['booking_id']:
                self.test_booking_email(ses_sender, options['booking_id'])
            
            # Тест с последним бронированием
            else:
                self.test_latest_booking_email(ses_sender)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при тестировании AWS SES: {str(e)}')
            )
            logger.error(f'Ошибка при тестировании AWS SES: {str(e)}')

    def test_basic_email(self, ses_sender, test_email):
        """Базовый тест отправки email"""
        if not test_email:
            self.stdout.write(
                self.style.ERROR('Укажите --test-email для базового теста')
            )
            return
        
        self.stdout.write(f'Отправка тестового email на {test_email}...')
        
        subject = "Тест AWS SES из eKol"
        html_body = """
        <html>
        <body>
            <h1>Тест AWS SES</h1>
            <p>Это тестовое сообщение из системы eKol.</p>
            <p>Если вы получили это сообщение, AWS SES настроен корректно!</p>
        </body>
        </html>
        """
        text_body = "Тест AWS SES\n\nЭто тестовое сообщение из системы eKol.\nЕсли вы получили это сообщение, AWS SES настроен корректно!"
        
        result = ses_sender.send_email(
            to_email=test_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Email успешно отправлен! MessageId: {result["message_id"]}'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f'Ошибка отправки email: {result.get("error_message", "Unknown error")}'
                )
            )

    def test_booking_email(self, ses_sender, booking_id):
        """Тест отправки email для конкретного бронирования"""
        try:
            booking = Booking.objects.get(booking_id=booking_id)
            self.stdout.write(f'Тестирование email для бронирования {booking_id}...')
            
            results = ses_sender.send_booking_confirmation_emails(booking)
            
            # Проверяем результат отправки пользователю
            if results.get('user_email'):
                if results['user_email']['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Email пользователю отправлен успешно! '
                            f'MessageId: {results["user_email"]["message_id"]}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Ошибка отправки email пользователю: '
                            f'{results["user_email"].get("error_message", "Unknown error")}'
                        )
                    )
            
            # Проверяем результат отправки отелю
            if results.get('hotel_email'):
                if results['hotel_email']['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Email отелю отправлен успешно! '
                            f'MessageId: {results["hotel_email"]["message_id"]}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Ошибка отправки email отелю: '
                            f'{results["hotel_email"].get("error_message", "Unknown error")}'
                        )
                    )
            
        except Booking.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Бронирование с ID {booking_id} не найдено')
            )

    def test_latest_booking_email(self, ses_sender):
        """Тест отправки email для последнего бронирования"""
        try:
            booking = Booking.objects.filter(payment_status='paid').last()
            if not booking:
                self.stdout.write(
                    self.style.WARNING('Не найдено оплаченных бронирований для теста')
                )
                return
            
            self.stdout.write(f'Тестирование email для последнего бронирования {booking.booking_id}...')
            
            results = ses_sender.send_booking_confirmation_emails(booking)
            
            # Проверяем результат отправки пользователю
            if results.get('user_email'):
                if results['user_email']['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Email пользователю отправлен успешно! '
                            f'MessageId: {results["user_email"]["message_id"]}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Ошибка отправки email пользователю: '
                            f'{results["user_email"].get("error_message", "Unknown error")}'
                        )
                    )
            
            # Проверяем результат отправки отелю
            if results.get('hotel_email'):
                if results['hotel_email']['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Email отелю отправлен успешно! '
                            f'MessageId: {results["hotel_email"]["message_id"]}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Ошибка отправки email отелю: '
                            f'{results["hotel_email"].get("error_message", "Unknown error")}'
                        )
                    )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при получении последнего бронирования: {str(e)}')
            ) 