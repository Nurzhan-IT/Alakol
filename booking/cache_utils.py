from django.core.cache import cache, caches
from django.conf import settings
from hotel.cache_utils import CacheKeyGenerator, CacheInvalidator
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BookingCacheHelper:
    """Помощник для кэширования в приложении бронирования."""
    
    @staticmethod
    def cache_room_unavailability(room_id: int, start_date: str, end_date: str, 
                                 unavailability_periods: List[Dict]) -> None:
        """Кэширование периодов недоступности номера отключено (данные реального времени)."""
        logger.debug(f"Кэширование недоступности номера {room_id} отключено для данных реального времени")
        pass
    
    @staticmethod
    def get_cached_room_unavailability(room_id: int, start_date: str, 
                                     end_date: str) -> List[Dict]:
        """Получение кэшированных периодов недоступности номера отключено (данные реального времени)."""
        logger.debug(f"Получение кэшированных данных недоступности номера {room_id} отключено")
        return None
    
    @staticmethod
    def cache_booking_availability_check(hotel_id: int, room_type_id: int, 
                                       checkin: str, checkout: str, 
                                       availability_data: Dict) -> None:
        """Кэширование результата проверки доступности номеров отключено (данные реального времени)."""
        logger.debug(f"Кэширование проверки доступности для отеля {hotel_id} отключено для данных реального времени")
        pass
    
    @staticmethod
    def get_cached_booking_availability_check(hotel_id: int, room_type_id: int, 
                                            checkin: str, checkout: str) -> Dict:
        """Получение кэшированного результата проверки доступности отключено (данные реального времени)."""
        logger.debug(f"Получение кэшированных данных доступности для отеля {hotel_id} отключено")
        return None
    
    @staticmethod
    def cache_booking_session_data(session_key: str, data: Dict) -> None:
        """Кэширование данных сессии бронирования отключено (данные реального времени)."""
        logger.debug(f"Кэширование данных сессии бронирования {session_key} отключено для данных реального времени")
        pass
    
    @staticmethod
    def get_cached_booking_session_data(session_key: str) -> Dict:
        """Получение кэшированных данных сессии бронирования отключено (данные реального времени)."""
        logger.debug(f"Получение кэшированных данных сессии {session_key} отключено")
        return None
    
    @staticmethod
    def invalidate_booking_related_cache(hotel_id: int = None, room_id: int = None, 
                                       room_type_id: int = None) -> None:
        """Инвалидирует весь кэш, связанный с бронированием."""
        if room_id:
            CacheInvalidator.invalidate_room_unavailability_cache(room_id)
        
        if hotel_id:
            CacheInvalidator.invalidate_booking_availability_cache(
                hotel_id, room_type_id
            )
            # Также инвалидируем общие данные о доступности номеров
            CacheInvalidator.invalidate_booking_cache(hotel_id=hotel_id)
        
        logger.info(f"Инвалидирован кэш бронирования для отеля {hotel_id}, "
                   f"номера {room_id}, типа номера {room_type_id}")


def cache_booking_function(key_func, timeout=None):
    """
    Декоратор для кэширования функций бронирования.
    
    Args:
        key_func: Функция для генерации ключа кэша
        timeout: Время жизни кэша в секундах
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            if callable(key_func):
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = key_func
            
            # Пытаемся получить из кэша
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit для функции бронирования: {cache_key}")
                return cached_result
            
            # Выполняем функцию и кэшируем результат
            result = func(*args, **kwargs)
            
            # Кэширование для данных реального времени отключено
            actual_timeout = 0  # Не кэшируем
            
            cache.set(cache_key, result, actual_timeout)
            logger.debug(f"Cache set для функции бронирования: {cache_key}")
            
            return result
        return wrapper
    return decorator 