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
        """Кэширует периоды недоступности номера."""
        cache_key = CacheKeyGenerator.room_unavailability(
            room_id, f"{start_date}_{end_date}"
        )
        timeout = settings.CACHE_TTL.get('room_unavailability', 300)
        cache.set(cache_key, unavailability_periods, timeout)
        logger.debug(f"Кэшированы периоды недоступности номера {room_id}: {cache_key}")
    
    @staticmethod
    def get_cached_room_unavailability(room_id: int, start_date: str, 
                                     end_date: str) -> List[Dict]:
        """Получает кэшированные периоды недоступности номера."""
        cache_key = CacheKeyGenerator.room_unavailability(
            room_id, f"{start_date}_{end_date}"
        )
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Найдены кэшированные периоды недоступности: {cache_key}")
        return cached_data
    
    @staticmethod
    def cache_booking_availability_check(hotel_id: int, room_type_id: int, 
                                       checkin: str, checkout: str, 
                                       availability_data: Dict) -> None:
        """Кэширует результат проверки доступности номеров."""
        cache_key = CacheKeyGenerator.booking_availability_check(
            hotel_id, room_type_id, checkin, checkout
        )
        timeout = settings.CACHE_TTL.get('booking_availability_check', 120)
        cache.set(cache_key, availability_data, timeout)
        logger.debug(f"Кэширован результат проверки доступности: {cache_key}")
    
    @staticmethod
    def get_cached_booking_availability_check(hotel_id: int, room_type_id: int, 
                                            checkin: str, checkout: str) -> Dict:
        """Получает кэшированный результат проверки доступности."""
        cache_key = CacheKeyGenerator.booking_availability_check(
            hotel_id, room_type_id, checkin, checkout
        )
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Найден кэшированный результат проверки доступности: {cache_key}")
        return cached_data
    
    @staticmethod
    def cache_booking_session_data(session_key: str, data: Dict) -> None:
        """Кэширует данные сессии бронирования."""
        cache_key = CacheKeyGenerator.booking_session_data(session_key)
        timeout = settings.CACHE_TTL.get('booking_session_data', 1800)
        cache.set(cache_key, data, timeout)
        logger.debug(f"Кэшированы данные сессии бронирования: {cache_key}")
    
    @staticmethod
    def get_cached_booking_session_data(session_key: str) -> Dict:
        """Получает кэшированные данные сессии бронирования."""
        cache_key = CacheKeyGenerator.booking_session_data(session_key)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Найдены кэшированные данные сессии: {cache_key}")
        return cached_data
    
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
            
            # Определяем timeout
            actual_timeout = timeout or settings.CACHE_TTL.get(
                'booking_availability_check', 120
            )
            
            cache.set(cache_key, result, actual_timeout)
            logger.debug(f"Cache set для функции бронирования: {cache_key}")
            
            return result
        return wrapper
    return decorator 