"""
Утилиты для работы с Redis кэшем в HMS проекте.
Включает функции для генерации ключей, инвалидации кэша и декораторы для кэширования.
"""

import hashlib
import json
from functools import wraps
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, date, timedelta

from django.core.cache import cache, caches
from django.conf import settings
from django.db import models
from django.utils.html import strip_tags
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

import logging

logger = logging.getLogger(__name__)


class CacheKeyGenerator:
    """Генератор ключей кэша для различных типов данных."""
    
    @staticmethod
    def hotel_list(featured: bool = None, status: str = None) -> str:
        """Генерирует ключ для списка отелей."""
        parts = ['hotels']
        if featured is not None:
            parts.append(f'featured_{featured}')
        if status:
            parts.append(f'status_{status}')
        return ':'.join(parts)
    
    @staticmethod
    def hotel_detail(hotel_slug: str) -> str:
        """Генерирует ключ для детальной информации об отеле."""
        return f'hotel_detail:{hotel_slug}'
    
    @staticmethod
    def hotel_reviews(hotel_id: int, active_only: bool = True) -> str:
        """Генерирует ключ для отзывов отеля."""
        active_str = 'active' if active_only else 'all'
        return f'hotel_reviews:{hotel_id}:{active_str}'
    
    @staticmethod
    def hotel_rooms(hotel_id: int, room_type_id: int = None) -> str:
        """Генерирует ключ для номеров отеля."""
        if room_type_id:
            return f'hotel_rooms:{hotel_id}:type_{room_type_id}'
        return f'hotel_rooms:{hotel_id}:all'
    
    @staticmethod
    def room_availability(hotel_id: int, checkin: str, checkout: str) -> str:
        """Генерирует ключ для доступности номеров."""
        return f'room_availability:{hotel_id}:{checkin}:{checkout}'
    
    @staticmethod
    def search_results(search_params: Dict) -> str:
        """Генерирует ключ для результатов поиска."""
        # Сортируем параметры для получения консистентного ключа
        sorted_params = sorted(search_params.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f'search_results:{params_hash}'
    
    @staticmethod
    def user_bookings(user_id: int, status: str = None) -> str:
        """Генерирует ключ для бронирований пользователя."""
        if status:
            return f'user_bookings:{user_id}:{status}'
        return f'user_bookings:{user_id}:all'
    
    @staticmethod
    def dynamic_pricing(room_type_id: int, date_range: str) -> str:
        """Генерирует ключ для динамических цен."""
        return f'dynamic_pricing:{room_type_id}:{date_range}'
    
    @staticmethod
    def hotel_features(hotel_id: int) -> str:
        """Генерирует ключ для удобств отеля."""
        return f'hotel_features:{hotel_id}'
    
    @staticmethod
    def hotel_gallery(hotel_id: int) -> str:
        """Генерирует ключ для галереи отеля."""
        return f'hotel_gallery:{hotel_id}'
    
    @staticmethod
    def room_unavailability(room_id: int, date_range: str = None) -> str:
        """Генерирует ключ для недоступности номера."""
        if date_range:
            return f"room_unavailability:{room_id}:{date_range}"
        return f"room_unavailability:{room_id}"
    
    @staticmethod
    def booking_availability_check(hotel_id: int, room_type_id: int, checkin: str, checkout: str) -> str:
        """Генерирует ключ для проверки доступности номеров."""
        return f"booking_check:{hotel_id}:{room_type_id}:{checkin}:{checkout}"
    
    @staticmethod
    def booking_session_data(session_key: str) -> str:
        """Генерирует ключ для кэширования данных сессии бронирования."""
        return f"booking_session:{session_key}"


class CacheInvalidator:
    """Управление инвалидацией кэша."""
    
    @staticmethod
    def invalidate_hotel_cache(hotel_id: int, hotel_slug: str = None):
        """Инвалидирует весь кэш, связанный с отелем."""
        logger.info(f"Invalidating cache for hotel {hotel_id}")
        
        # Инвалидируем детальную информацию об отеле
        if hotel_slug:
            cache.delete(CacheKeyGenerator.hotel_detail(hotel_slug))
        
        # Инвалидируем список отелей
        cache.delete(CacheKeyGenerator.hotel_list())
        cache.delete(CacheKeyGenerator.hotel_list(featured=True))
        cache.delete(CacheKeyGenerator.hotel_list(featured=False))
        cache.delete(CacheKeyGenerator.hotel_list(status="Live"))
        
        # Инвалидируем связанные данные
        cache.delete(CacheKeyGenerator.hotel_features(hotel_id))
        cache.delete(CacheKeyGenerator.hotel_gallery(hotel_id))
        cache.delete(CacheKeyGenerator.hotel_rooms(hotel_id))
        
        # Очищаем поисковые результаты (используем wildcard паттерн)
        try:
            redis_client = caches['default'].get_client()
            pattern = f"{settings.CACHES['default']['KEY_PREFIX']}:*:search_results:*"
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                logger.info(f"Deleted {len(keys)} search result cache keys")
        except Exception as e:
            logger.error(f"Error clearing search cache: {e}")
    
    @staticmethod
    def invalidate_booking_cache(user_id: int = None, hotel_id: int = None):
        """Инвалидирует кэш бронирований (отключено для данных реального времени)."""
        logger.info(f"Booking cache invalidation called for user {user_id}, hotel {hotel_id} - but caching is disabled for real-time data")
        
        # Кэширование пользовательских бронирований отключено для обеспечения данных реального времени
        # if user_id:
        #     cache.delete(CacheKeyGenerator.user_bookings(user_id))
        #     cache.delete(CacheKeyGenerator.user_bookings(user_id, 'paid'))
        #     cache.delete(CacheKeyGenerator.user_bookings(user_id, 'pending'))
        #     cache.delete(CacheKeyGenerator.user_bookings(user_id, 'cancelled'))
        
        if hotel_id:
            # Инвалидируем доступность номеров для всех дат
            try:
                cache_instance = caches['default']
                
                # Получаем Redis клиент с учетом различных версий django-redis
                try:
                    redis_client = cache_instance._cache.get_client()
                except AttributeError:
                    try:
                        redis_client = cache_instance.get_client()
                    except AttributeError:
                        logger.warning("Cannot get Redis client for room availability cache invalidation")
                        return
                
                pattern = f"{settings.CACHES['default']['KEY_PREFIX']}:*:room_availability:{hotel_id}:*"
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
                    logger.info(f"Deleted {len(keys)} room availability cache keys")
            except Exception as e:
                logger.error(f"Error clearing room availability cache: {e}")
    
    @staticmethod
    def invalidate_search_cache():
        """Инвалидирует весь поисковый кэш."""
        try:
            cache_instance = caches['default']
            
            # Получаем Redis клиент с учетом различных версий django-redis
            try:
                redis_client = cache_instance._cache.get_client()
            except AttributeError:
                try:
                    redis_client = cache_instance.get_client()
                except AttributeError:
                    logger.warning("Cannot get Redis client for search cache invalidation")
                    return
            
            pattern = f"{settings.CACHES['default']['KEY_PREFIX']}:*:search_results:*"
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                logger.info(f"Deleted {len(keys)} search cache keys")
        except Exception as e:
            logger.error(f"Error clearing search cache: {e}")
    
    @staticmethod
    def invalidate_room_unavailability_cache(room_id: int = None):
        """Инвалидирует кэш недоступности номеров."""
        try:
            cache_instance = caches['default']
            
            # Получаем Redis клиент
            try:
                redis_client = cache_instance._cache.get_client()
            except AttributeError:
                try:
                    redis_client = cache_instance.get_client()
                except AttributeError:
                    logger.warning("Cannot get Redis client for room unavailability cache invalidation")
                    return
            
            if room_id:
                pattern = f"{settings.CACHES['default']['KEY_PREFIX']}:*:room_unavailability:{room_id}:*"
            else:
                pattern = f"{settings.CACHES['default']['KEY_PREFIX']}:*:room_unavailability:*"
            
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                logger.info(f"Deleted {len(keys)} room unavailability cache keys")
        except Exception as e:
            logger.error(f"Error clearing room unavailability cache: {e}")
    
    @staticmethod
    def invalidate_booking_availability_cache(hotel_id: int = None, room_type_id: int = None):
        """Инвалидирует кэш проверок доступности бронирования."""
        try:
            cache_instance = caches['default']
            
            # Получаем Redis клиент
            try:
                redis_client = cache_instance._cache.get_client()
            except AttributeError:
                try:
                    redis_client = cache_instance.get_client()
                except AttributeError:
                    logger.warning("Cannot get Redis client for booking availability cache invalidation")
                    return
            
            if hotel_id and room_type_id:
                pattern = f"{settings.CACHES['default']['KEY_PREFIX']}:*:booking_check:{hotel_id}:{room_type_id}:*"
            elif hotel_id:
                pattern = f"{settings.CACHES['default']['KEY_PREFIX']}:*:booking_check:{hotel_id}:*"
            else:
                pattern = f"{settings.CACHES['default']['KEY_PREFIX']}:*:booking_check:*"
            
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                logger.info(f"Deleted {len(keys)} booking availability cache keys")
        except Exception as e:
            logger.error(f"Error clearing booking availability cache: {e}")


def cache_function(key_func, timeout=None, cache_alias='default'):
    """
    Декоратор для кэширования результатов функций.
    
    Args:
        key_func: Функция для генерации ключа кэша
        timeout: Время жизни кэша в секундах
        cache_alias: Алиас кэша для использования
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            if callable(key_func):
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = key_func
            
            # Пытаемся получить из кэша
            cached_result = caches[cache_alias].get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Выполняем функцию и кэшируем результат
            result = func(*args, **kwargs)
            
            # Определяем timeout
            actual_timeout = timeout
            if actual_timeout is None:
                actual_timeout = getattr(settings, 'CACHE_TTL', {}).get(
                    func.__name__, 
                    settings.CACHES[cache_alias]['TIMEOUT']
                )
            
            caches[cache_alias].set(cache_key, result, actual_timeout)
            logger.debug(f"Cache set for key: {cache_key}, timeout: {actual_timeout}")
            
            return result
        return wrapper
    return decorator


def cache_queryset(key_func, timeout=None, cache_alias='default'):
    """
    Декоратор для кэширования QuerySet результатов.
    Специально оптимизирован для Django QuerySet.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            if callable(key_func):
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = key_func
            
            # Пытаемся получить из кэша
            cached_result = caches[cache_alias].get(cache_key)
            if cached_result is not None:
                logger.debug(f"QuerySet cache hit for key: {cache_key}")
                return cached_result
            
            # Выполняем функцию и преобразуем QuerySet в список
            result = func(*args, **kwargs)
            
            # Если результат - QuerySet, преобразуем в список для кэширования
            if hasattr(result, '_result_cache'):
                result = list(result)
            
            # Определяем timeout
            actual_timeout = timeout
            if actual_timeout is None:
                actual_timeout = getattr(settings, 'CACHE_TTL', {}).get(
                    func.__name__, 
                    settings.CACHES[cache_alias]['TIMEOUT']
                )
            
            caches[cache_alias].set(cache_key, result, actual_timeout)
            logger.debug(f"QuerySet cache set for key: {cache_key}, timeout: {actual_timeout}")
            
            return result
        return wrapper
    return decorator


class CacheHelper:
    """Вспомогательный класс для работы с кэшем."""
    
    @staticmethod
    def get_or_set_complex(key: str, callback, timeout: int = None, cache_alias: str = 'default'):
        """
        Получает значение из кэша или устанавливает его через callback.
        Подходит для сложных вычислений.
        """
        cached_value = caches[cache_alias].get(key)
        if cached_value is not None:
            # Если из кэша пришел список, но callback возвращает QuerySet,
            # проверяем на тип данных для совместимости
            if isinstance(cached_value, list) and len(cached_value) > 0:
                # Для случаев, где ожидается единичный объект, берем первый элемент
                from django.db import models
                if hasattr(cached_value[0], '_meta') and isinstance(cached_value[0], models.Model):
                    # Если это список Django моделей, возвращаем как есть
                    return cached_value
            return cached_value
        
        # Выполняем callback для получения значения
        value = callback()
        
        # Преобразуем QuerySet в список для кэширования
        if hasattr(value, '_result_cache') or hasattr(value, 'query'):
            value = list(value)
        
        # Устанавливаем в кэш
        if timeout is None:
            timeout = settings.CACHES[cache_alias]['TIMEOUT']
        
        caches[cache_alias].set(key, value, timeout)
        return value
    
    @staticmethod
    def invalidate_pattern(pattern: str, cache_alias: str = 'default'):
        """Инвалидирует все ключи, соответствующие паттерну."""
        try:
            cache_instance = caches[cache_alias]
            
            # Получаем Redis клиент с учетом различных версий django-redis
            try:
                redis_client = cache_instance._cache.get_client()
            except AttributeError:
                try:
                    redis_client = cache_instance.get_client()
                except AttributeError:
                    logger.warning(f"Cannot get Redis client for pattern invalidation: {pattern}")
                    return 0
            
            full_pattern = f"{settings.CACHES[cache_alias]['KEY_PREFIX']}:*:{pattern}"
            keys = redis_client.keys(full_pattern)
            if keys:
                redis_client.delete(*keys)
                logger.info(f"Deleted {len(keys)} cache keys matching pattern: {pattern}")
                return len(keys)
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}")
        return 0
    
    @staticmethod
    def warm_up_cache():
        """Предварительный прогрев кэша основными данными."""
        logger.info("Starting cache warm-up process")
        
        # Импортируем модели локально чтобы избежать циклических импортов
        from hotel.models import Hotel, HotelFeatures, RoomType
        
        try:
            # Кэшируем список активных отелей
            hotels_queryset = Hotel.objects.filter(status="Live").prefetch_related(
                'hotelfeatures_set', 'roomtype_set'
            )[:20]  # Берем топ-20 отелей
            
            hotels_list = list(hotels_queryset)  # Преобразуем в список для кэширования
            
            cache.set(
                CacheKeyGenerator.hotel_list(status="Live"), 
                hotels_list, 
                settings.CACHE_TTL['hotels_list']
            )
            
            # Кэшируем детали каждого отеля
            for hotel in hotels_list:
                cache.set(
                    CacheKeyGenerator.hotel_detail(hotel.slug),
                    hotel,
                    settings.CACHE_TTL['hotel_detail']
                )
                
                # Кэшируем удобства отеля
                features = list(hotel.hotelfeatures_set.all())
                cache.set(
                    CacheKeyGenerator.hotel_features(hotel.id),
                    features,
                    settings.CACHE_TTL['features_and_amenities']
                )
            
            logger.info(f"Cache warm-up completed for {len(hotels_list)} hotels")
            
        except Exception as e:
            logger.error(f"Error during cache warm-up: {e}")


# Регистрируем сигналы для автоматической инвалидации кэша
def register_cache_signals():
    """Регистрирует сигналы Django для автоматической инвалидации кэша."""
    
    @receiver(post_save, sender='hotel.Hotel')
    def invalidate_hotel_cache_on_save(sender, instance, **kwargs):
        CacheInvalidator.invalidate_hotel_cache(instance.id, instance.slug)
    
    @receiver(post_delete, sender='hotel.Hotel')
    def invalidate_hotel_cache_on_delete(sender, instance, **kwargs):
        CacheInvalidator.invalidate_hotel_cache(instance.id, instance.slug)
    
    @receiver(post_save, sender='hotel.Booking')
    def invalidate_booking_cache_on_save(sender, instance, **kwargs):
        CacheInvalidator.invalidate_booking_cache(
            user_id=instance.user_id if instance.user else None,
            hotel_id=instance.hotel_id if instance.hotel else None
        )
    
    @receiver(post_delete, sender='hotel.Booking')
    def invalidate_booking_cache_on_delete(sender, instance, **kwargs):
        CacheInvalidator.invalidate_booking_cache(
            user_id=instance.user_id if instance.user else None,
            hotel_id=instance.hotel_id if instance.hotel else None
        )
    
    @receiver([post_save, post_delete], sender='hotel.Review')
    def invalidate_review_cache_on_change(sender, instance, **kwargs):
        if instance.hotel:
            cache_key = CacheKeyGenerator.hotel_reviews(instance.hotel.id)
            cache.delete(cache_key)
            # Также инвалидируем детали отеля, так как там может быть средняя оценка
            CacheInvalidator.invalidate_hotel_cache(instance.hotel.id, instance.hotel.slug)
    
    @receiver([post_save, post_delete], sender='booking.RoomUnavailability')
    def invalidate_room_unavailability_cache_on_change(sender, instance, **kwargs):
        if instance.room:
            # Инвалидируем кэш недоступности для конкретного номера
            CacheInvalidator.invalidate_room_unavailability_cache(instance.room.id)
            # Также инвалидируем кэш доступности бронирования для отеля
            if instance.room.hotel:
                CacheInvalidator.invalidate_booking_availability_cache(
                    hotel_id=instance.room.hotel.id,
                    room_type_id=instance.room.room_type.id if instance.room.room_type else None
                ) 