#!/usr/bin/env python3
"""
Скрипт для добавления оптимизированных индексов PostgreSQL 
для всех моделей системы бронирования отелей Alakol.

Этот скрипт применяет миграции для создания индексов в следующих приложениях:
- hotel: основные модели отелей, номеров, бронирований
- booking: недоступность номеров  
- userauths: пользователи и аутентификация
- legal: юридические документы

Использование:
    python add_database_indexes.py

Требования:
    - PostgreSQL расширение pg_trgm для полнотекстового поиска
    - Django ORM для выполнения миграций
"""

import os
import django
import sys
from django.core.management import execute_from_command_line


def main():
    """Основная функция для применения миграций индексов"""
    
    print("🔄 Применение миграций для создания индексов PostgreSQL...")
    print("=" * 60)
    
    # Настройка Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_prj.settings')
    django.setup()
    
    # Список миграций для применения
    migrations_to_apply = [
        ('hotel', '0096_add_pg_trgm_extension'),  # Сначала расширение
        ('hotel', '0100_add_database_indexes'),
        ('booking', '0003_add_database_indexes'), 
        ('userauths', '0013_add_database_indexes'),
        ('legal', '0003_add_database_indexes'),
    ]
    
    print("📋 Будут применены следующие миграции:")
    for app, migration in migrations_to_apply:
        print(f"   • {app}: {migration}")
    
    print("\n🚀 Начинаем применение миграций...\n")
    
    try:
        # Применяем миграции
        for app, migration in migrations_to_apply:
            print(f"⏳ Применяем миграцию {app}.{migration}...")
            execute_from_command_line([
                'manage.py', 
                'migrate',
                app,
                migration,
                '--verbosity=1'
            ])
            print(f"✅ Миграция {app}.{migration} применена успешно\n")
        
        print("🎉 Все миграции индексов применены успешно!")
        print("=" * 60)
        
        # Выводим информацию о созданных индексах
        print_created_indexes_info()
        
    except Exception as e:
        print(f"❌ Ошибка при применении миграций: {e}")
        sys.exit(1)


def print_created_indexes_info():
    """Выводит информацию о созданных индексах"""
    
    print("\n📊 СОЗДАННЫЕ ИНДЕКСЫ ПО ПРИЛОЖЕНИЯМ:")
    print("=" * 60)
    
    # Информация об индексах для каждого приложения
    indexes_info = {
        'HOTEL APP': {
            'Основные индексы': [
                'idx_hotel_status - Статус отеля (опубликован/черновик)',
                'idx_hotel_featured - Рекомендуемые отели',
                'idx_hotel_views - Количество просмотров',
                'idx_roomtype_price - Цена номеров',
                'idx_room_available - Доступность номеров',
                'idx_booking_payment_status - Статус оплаты',
                'idx_coupon_active - Активные купоны',
                'idx_review_active - Активные отзывы',
            ],
            'Составные индексы': [
                'idx_hotel_status_featured - Статус + рекомендуемые',
                'idx_booking_hotel_dates - Отель + даты бронирования',
                'idx_room_hotel_available - Отель + доступность номеров',
                'idx_review_hotel_active - Отель + активные отзывы',
            ],
            'Текстовый поиск': [
                'idx_hotel_name_trgm - Поиск по названию отеля',
                'idx_hotel_address_trgm - Поиск по адресу',
                'idx_roomtype_type_trgm - Поиск по типу номера',
            ]
        },
        'BOOKING APP': {
            'Основные индексы': [
                'idx_room_unavailability_reason - Причина недоступности',
                'idx_room_unavailability_created_at - Дата создания',
            ],
            'Составные индексы': [
                'idx_room_unavailability_room_dates - Номер + даты',
                'idx_room_unavailability_overlap - Проверка пересечений',
            ]
        },
        'USERAUTHS APP': {
            'Основные индексы': [
                'idx_user_email_lower - Email в нижнем регистре',
                'idx_user_is_active - Активные пользователи',
                'idx_profile_verified - Верифицированные профили',
                'idx_userconsent_consent_type - Типы согласий',
            ],
            'Составные индексы': [
                'idx_user_active_email - Активность + email',
                'idx_userconsent_user_type - Пользователь + тип согласия',
            ],
            'Текстовый поиск': [
                'idx_user_fullname_trgm - Поиск по имени пользователя',
                'idx_profile_fullname_trgm - Поиск по имени в профиле',
            ]
        },
        'LEGAL APP': {
            'Основные индексы': [
                'idx_legaldocument_document_type - Тип документа',
                'idx_legaldocument_is_active - Активные документы',
                'idx_documentview_viewed_at - Время просмотра',
            ],
            'Составные индексы': [
                'idx_legaldocument_type_active - Тип + активность',
                'idx_documentview_user_type - Пользователь + тип документа',
            ],
            'Текстовый поиск': [
                'idx_legaldocument_content_trgm - Поиск по содержанию',
            ]
        }
    }
    
    for app_name, categories in indexes_info.items():
        print(f"\n🔹 {app_name}")
        print("-" * 40)
        
        for category, indexes in categories.items():
            print(f"\n  {category}:")
            for index in indexes:
                print(f"    • {index}")
    
    print("\n" + "=" * 60)
    print("💡 РЕКОМЕНДАЦИИ ПО ПРОИЗВОДИТЕЛЬНОСТИ:")
    print("=" * 60)
    
    recommendations = [
        "1. Регулярно обновляйте статистику таблиц: ANALYZE;",
        "2. Мониторьте использование индексов через pg_stat_user_indexes",
        "3. Для больших таблиц рассмотрите партицирование по датам",
        "4. Используйте EXPLAIN ANALYZE для оптимизации медленных запросов",
        "5. Настройте PostgreSQL параметры для кэширования индексов",
        "6. Регулярно проверяйте фрагментацию индексов командой REINDEX",
    ]
    
    for rec in recommendations:
        print(f"  {rec}")
    
    print("\n🔧 ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ PostgreSQL:")
    print("-" * 40)
    print("  • shared_buffers = 25% от RAM")
    print("  • effective_cache_size = 75% от RAM") 
    print("  • work_mem = RAM / max_connections / 4")
    print("  • maintenance_work_mem = RAM / 16")
    print("  • checkpoint_completion_target = 0.9")
    
    print("\n✨ Индексы успешно созданы и готовы к использованию!")


if __name__ == '__main__':
    main() 