import time
import logging
import signal
import sys
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.utils import timezone
from hotel.services import handle_bookings_payment_status_processing_to_unpaid

logger = logging.getLogger('booking_processor')

class Command(BaseCommand):
    help = 'Запускает обработчик бронирований - обновляет статусы просроченных бронирований'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_running = True
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval', 
            type=int, 
            default=30,
            help='Интервал обработки в секундах (по умолчанию: 30)'
        )
        parser.add_argument(
            '--max-errors', 
            type=int, 
            default=10,
            help='Максимальное количество ошибок подряд перед остановкой (по умолчанию: 10)'
        )
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        logger.info(f"Получен сигнал {signum}, останавливаем обработчик...")
        self.is_running = False
    
    def handle(self, *args, **options):
        interval = options['interval']
        max_errors = options['max_errors']
        error_count = 0
        
        # Регистрируем обработчики сигналов
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        logger.info(f"Запускаем обработчик бронирований с интервалом {interval}с")
        
        while self.is_running:
            try:
                start_time = time.time()
                
                # Основная логика обработки
                result = handle_bookings_payment_status_processing_to_unpaid()
                
                # Рассчитываем время выполнения
                execution_time = time.time() - start_time
                
                # Сохраняем метрики в кеш для мониторинга
                cache.set('booking_processor_last_run', timezone.now().isoformat(), 300)
                cache.set('booking_processor_last_execution_time', execution_time, 300)
                cache.set('booking_processor_last_result', result, 300)
                cache.set('booking_processor_error_count', 0, 300)
                
                # Сбрасываем счетчик ошибок при успешном выполнении
                error_count = 0
                
                logger.debug(f"Выполнение заняло {execution_time:.2f}с: {result}")
                
                # Рассчитываем время до следующего запуска
                sleep_time = max(1, interval - execution_time)
                
                # Спим с проверкой флага остановки
                for _ in range(int(sleep_time)):
                    if not self.is_running:
                        break
                    time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Обработчик остановлен пользователем")
                break
                
            except Exception as e:
                error_count += 1
                logger.error(f"Ошибка в обработчике бронирований ({error_count}/{max_errors}): {str(e)}")
                
                # Сохраняем информацию об ошибке в кеш
                cache.set('booking_processor_last_error', str(e), 300)
                cache.set('booking_processor_error_count', error_count, 300)
                
                # Если превышен лимит ошибок, останавливаемся
                if error_count >= max_errors:
                    logger.critical(f"Превышен лимит ошибок ({max_errors}), останавливаем обработчик")
                    break
                
                # Увеличиваем время ожидания при ошибках
                error_sleep = min(60, 5 * error_count)
                logger.info(f"Ожидание {error_sleep}с перед следующей попыткой...")
                time.sleep(error_sleep)
        
        logger.info("Обработчик бронирований остановлен")
        
        # Очищаем метрики при остановке
        cache.delete('booking_processor_last_run')
        cache.delete('booking_processor_last_execution_time')
        cache.delete('booking_processor_last_result')
        cache.delete('booking_processor_last_error')
        cache.delete('booking_processor_error_count') 