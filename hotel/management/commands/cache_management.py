"""
Management команда для управления Redis кэшем в HMS проекте.
Позволяет очищать, прогревать и мониторить состояние кэша.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache, caches
from django.conf import settings
from django.db import connection

from hotel.cache_utils import CacheHelper, CacheInvalidator
from hotel.models import Hotel, Booking, Review

import logging
import json

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Управление Redis кэшем HMS системы'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['clear', 'warm_up', 'stats', 'clear_pattern', 'test'],
            help='Действие для выполнения с кэшем'
        )
        
        parser.add_argument(
            '--pattern',
            type=str,
            help='Паттерн для очистки кэша (используется с clear_pattern)'
        )
        
        parser.add_argument(
            '--cache-alias',
            type=str,
            default='default',
            help='Алиас кэша для использования (default: default)'
        )

    def handle(self, *args, **options):
        action = options['action']
        cache_alias = options['cache_alias']
        
        try:
            if action == 'clear':
                self.clear_cache(cache_alias)
            elif action == 'warm_up':
                self.warm_up_cache()
            elif action == 'stats':
                self.show_cache_stats(cache_alias)
            elif action == 'clear_pattern':
                pattern = options.get('pattern')
                if not pattern:
                    raise CommandError('Параметр --pattern обязателен для действия clear_pattern')
                self.clear_cache_pattern(pattern, cache_alias)
            elif action == 'test':
                self.test_cache_performance()
            else:
                raise CommandError(f'Неизвестное действие: {action}')
                
        except Exception as e:
            logger.error(f"Ошибка выполнения команды кэширования: {e}")
            raise CommandError(f'Ошибка: {e}')

    def clear_cache(self, cache_alias='default'):
        """Очищает весь кэш."""
        self.stdout.write('Очистка кэша...')
        
        try:
            cache_instance = caches[cache_alias]
            cache_instance.clear()
            
            self.stdout.write(
                self.style.SUCCESS(f'Кэш {cache_alias} успешно очищен')
            )
            
            # Также очищаем остальные кэши
            for alias in settings.CACHES.keys():
                if alias != cache_alias:
                    try:
                        caches[alias].clear()
                        self.stdout.write(f'Кэш {alias} очищен')
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Не удалось очистить кэш {alias}: {e}')
                        )
                        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка очистки кэша: {e}')
            )

    def warm_up_cache(self):
        """Прогревает кэш основными данными."""
        self.stdout.write('Прогрев кэша...')
        
        try:
            # Используем утилиту прогрева из cache_utils
            CacheHelper.warm_up_cache()
            
            # Дополнительно кэшируем часто используемые данные
            self.stdout.write('Кэширование дополнительных данных...')
            
            # Кэшируем активные отели
            hotels_queryset = Hotel.objects.filter(status="Live")[:50]
            hotels_list = list(hotels_queryset)  # Преобразуем в список
            cache.set('top_hotels', hotels_list, settings.CACHE_TTL['hotels_list'])
            
            # Кэшируем статистику
            from django.db import models
            stats = {
                'total_hotels': Hotel.objects.filter(status="Live").count(),
                'total_bookings': Booking.objects.filter(is_active=True).count(),
                'average_rating': Review.objects.filter(active=True).aggregate(
                    avg_rating=models.Avg('rating')
                )['avg_rating'] or 0
            }
            cache.set('site_stats', stats, settings.CACHE_TTL['static_content'])
            
            self.stdout.write(
                self.style.SUCCESS('Прогрев кэша завершен успешно')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка прогрева кэша: {e}')
            )

    def show_cache_stats(self, cache_alias='default'):
        """Показывает статистику кэша."""
        self.stdout.write(f'Статистика кэша {cache_alias}:')
        
        try:
            cache_instance = caches[cache_alias]
            
            # Получаем информацию о Redis подключении
            redis_client = None
            info = None
            
            try:
                # Для django-redis
                redis_client = cache_instance._cache.get_client()
                info = redis_client.info()
            except AttributeError:
                try:
                    # Альтернативный способ получения клиента
                    redis_client = cache_instance.get_client()
                    info = redis_client.info()
                except AttributeError:
                    # Если не удается получить клиент, показываем базовую информацию
                    self.stdout.write("Подключение к кэшу: Активно")
                    self.stdout.write("Тип кэша: " + cache_instance.__class__.__name__)
                    return
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Не удается получить детальную статистику: {e}")
                )
                self.stdout.write("Подключение к кэшу: Активно")
                self.stdout.write("Тип кэша: " + cache_instance.__class__.__name__)
                return
            
            if not info:
                self.stdout.write("Статистика недоступна")
                return
            
            self.stdout.write(f"Redis версия: {info.get('redis_version', 'N/A')}")
            self.stdout.write(f"Используемая память: {info.get('used_memory_human', 'N/A')}")
            self.stdout.write(f"Максимальная память: {info.get('maxmemory_human', 'N/A')}")
            self.stdout.write(f"Активные подключения: {info.get('connected_clients', 'N/A')}")
            self.stdout.write(f"Общее количество команд: {info.get('total_commands_processed', 'N/A')}")
            self.stdout.write(f"Keyspace hits: {info.get('keyspace_hits', 'N/A')}")
            self.stdout.write(f"Keyspace misses: {info.get('keyspace_misses', 'N/A')}")
            
            # Вычисляем hit rate
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            if total > 0:
                hit_rate = (hits / total) * 100
                self.stdout.write(f"Hit rate: {hit_rate:.2f}%")
            
            # Показываем количество ключей в каждой базе данных
            for db_key in info.keys():
                if db_key.startswith('db'):
                    db_info = info[db_key]
                    self.stdout.write(f"{db_key}: {db_info}")
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка получения статистики: {e}')
            )

    def clear_cache_pattern(self, pattern, cache_alias='default'):
        """Очищает кэш по паттерну."""
        self.stdout.write(f'Очистка кэша по паттерну: {pattern}')
        
        try:
            deleted_count = CacheHelper.invalidate_pattern(pattern, cache_alias)
            
            self.stdout.write(
                self.style.SUCCESS(f'Удалено {deleted_count} ключей по паттерну "{pattern}"')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка очистки по паттерну: {e}')
            )

    def test_cache_performance(self):
        """Тестирует производительность кэша."""
        self.stdout.write('Тестирование производительности кэша...')
        
        import time
        import random
        
        try:
            # Тест записи
            self.stdout.write('Тест записи в кэш...')
            start_time = time.time()
            
            for i in range(100):
                key = f'test_key_{i}'
                value = f'test_value_{i}_{random.randint(1, 1000)}'
                cache.set(key, value, 300)
            
            write_time = time.time() - start_time
            self.stdout.write(f'Время записи 100 ключей: {write_time:.3f} сек')
            
            # Тест чтения
            self.stdout.write('Тест чтения из кэша...')
            start_time = time.time()
            
            for i in range(100):
                key = f'test_key_{i}'
                value = cache.get(key)
            
            read_time = time.time() - start_time
            self.stdout.write(f'Время чтения 100 ключей: {read_time:.3f} сек')
            
            # Тест сложных объектов
            self.stdout.write('Тест сложных объектов...')
            complex_data = {
                'hotels': [
                    {
                        'id': i,
                        'name': f'Hotel {i}',
                        'rooms': [{'id': j, 'type': f'Type {j}'} for j in range(10)]
                    } for i in range(10)
                ]
            }
            
            start_time = time.time()
            cache.set('complex_test', complex_data, 300)
            cached_data = cache.get('complex_test')
            complex_time = time.time() - start_time
            
            self.stdout.write(f'Время кэширования сложного объекта: {complex_time:.3f} сек')
            
            # Очищаем тестовые данные
            for i in range(100):
                cache.delete(f'test_key_{i}')
            cache.delete('complex_test')
            
            self.stdout.write(
                self.style.SUCCESS('Тестирование производительности завершено')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка тестирования: {e}')
            ) 