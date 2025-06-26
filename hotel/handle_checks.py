#!/usr/bin/env python3
"""
Оптимизированный сервис для обработки бронирований.

УСТАРЕЛ: Этот файл заменен на management команду.
Используйте вместо него: python manage.py run_booking_processor

Этот файл оставлен для обратной совместимости.
"""

import os
import django
import sys
import time
import logging
import signal
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/booking_processor_legacy.log')
    ]
)
logger = logging.getLogger('booking_processor_legacy')

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_prj.production_settings')
django.setup()

# Импортируем функции после настройки Django
from hotel.services import handle_bookings_payment_status_processing_to_unpaid

class BookingProcessorLegacy:
    """Легаси версия обработчика бронирований"""
    
    def __init__(self, interval=30):
        self.interval = interval
        self.is_running = True
        self.error_count = 0
        self.max_errors = 10
        
        # Регистрируем обработчики сигналов
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        logger.info(f"Получен сигнал {signum}, останавливаем обработчик...")
        self.is_running = False
    
    def run_periodic_tasks(self):
        """
        Запускает периодические задачи по обслуживанию базы данных.
        Использует оптимизированные запросы для предотвращения проблемы N+1.
        """
        try:
            start_time = time.time()
            
            # Отмена просроченных бронирований
            result = handle_bookings_payment_status_processing_to_unpaid()
            
            execution_time = time.time() - start_time
            logger.debug(f"Выполнение заняло {execution_time:.2f}с: {result}")
            
            # Сбрасываем счетчик ошибок при успешном выполнении
            self.error_count = 0
            
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Ошибка в обработчике бронирований ({self.error_count}/{self.max_errors}): {str(e)}")
            
            if self.error_count >= self.max_errors:
                logger.critical(f"Превышен лимит ошибок ({self.max_errors}), останавливаем обработчик")
                self.is_running = False
            
            raise
    
    def start(self):
        """Запуск основного цикла обработки"""
        logger.warning("⚠️  УСТАРЕЛ: Используйте 'python manage.py run_booking_processor' вместо этого скрипта")
        logger.info(f"Запускаем обработчик бронирований с интервалом {self.interval}с")
        
        while self.is_running:
            try:
                start_time = time.time()
                self.run_periodic_tasks()
                
                # Рассчитываем время до следующего запуска
                execution_time = time.time() - start_time
                sleep_time = max(1, self.interval - execution_time)
                
                # Спим с проверкой флага остановки
                for _ in range(int(sleep_time)):
                    if not self.is_running:
                        break
                    time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Обработчик остановлен пользователем")
                break
            except Exception as e:
                if self.is_running:  # Только если не останавливаемся
                    # Увеличиваем время ожидания при ошибках
                    error_sleep = min(60, 5 * self.error_count)
                    logger.info(f"Ожидание {error_sleep}с перед следующей попыткой...")
                    time.sleep(error_sleep)
        
        logger.info("Обработчик бронирований остановлен")

def main():
    """Главная функция запуска"""
    # Создаем директорию для логов если её нет
    os.makedirs('logs', exist_ok=True)
    
    processor = BookingProcessorLegacy(interval=30)
    processor.start()

if __name__ == '__main__':
    main()