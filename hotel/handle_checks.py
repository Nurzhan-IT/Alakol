import os
import django
import sys
import time
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('booking_cleanup.log')
    ]
)
logger = logging.getLogger('booking_cleanup')

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_prj.settings')
django.setup()

# Импортируем функции после настройки Django
from hotel.services import handle_bookings_payment_status_processing_to_unpaid, get_bookings_with_related_data

def run_periodic_tasks():
    """
    Запускает периодические задачи по обслуживанию базы данных.
    Использует оптимизированные запросы для предотвращения проблемы N+1.
    """
    logger.info("Starting periodic task execution")
    
    # Отмена просроченных бронирований
    try:
        result = handle_bookings_payment_status_processing_to_unpaid()
        logger.info(result)
    except Exception as e:
        logger.error(f"Error running handle_bookings_payment_status_processing_to_unpaid: {str(e)}")
    
    # Здесь можно добавить другие периодические задачи
    # Например, получение и обработка бронирований со связанными данными
    # для формирования отчетов или других целей
    
    logger.info("Finished periodic task execution")

if __name__ == '__main__':
    logger.info("Starting booking cleanup service")
    
    # Интервал выполнения в секундах
    INTERVAL = 30
    
    try:
        while True:
            start_time = time.time()
            run_periodic_tasks()
            
            # Рассчитываем время до следующего запуска
            execution_time = time.time() - start_time
            sleep_time = max(1, INTERVAL - execution_time)
            
            logger.debug(f"Task execution took {execution_time:.2f} seconds. Sleeping for {sleep_time:.2f} seconds.")
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.critical(f"Service stopped due to error: {str(e)}")
        raise