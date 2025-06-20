# Документация по индексам базы данных PostgreSQL

## Обзор

Данная документация описывает все индексы, созданные для оптимизации производительности базы данных PostgreSQL системы бронирования отелей Alakol.

Индексы организованы по приложениям Django и включают:
- **Основные индексы** - для часто используемых полей фильтрации
- **Составные индексы** - для оптимизации сложных запросов с несколькими условиями
- **Функциональные индексы** - для полнотекстового поиска с использованием pg_trgm

## Структура миграций

```
hotel/migrations/0100_add_database_indexes.py
booking/migrations/0003_add_database_indexes.py
userauths/migrations/0013_add_database_indexes.py
legal/migrations/0003_add_database_indexes.py
```

---

## 🏨 HOTEL APP - Индексы

### Модель Hotel

#### Основные индексы:
- `idx_hotel_status` - Индекс по статусу отеля (Live, Draft, Disabled)
- `idx_hotel_featured` - Индекс по полю рекомендуемых отелей
- `idx_hotel_date` - Индекс по дате создания отеля
- `idx_hotel_views` - Индекс по количеству просмотров
- `idx_hotel_dates_range` - Составной индекс по датам работы отеля (start_date, end_date)

#### Составные индексы:
- `idx_hotel_status_featured` - Статус + рекомендуемые (для быстрой выборки активных рекомендуемых отелей)
- `idx_hotel_user_status` - Пользователь + статус (для панели управления владельцем отеля)

#### Полнотекстовый поиск:
- `idx_hotel_name_trgm` - GIN индекс для поиска по названию отеля
- `idx_hotel_address_trgm` - GIN индекс для поиска по адресу

**Применение:**
```sql
-- Быстрый поиск опубликованных отелей
SELECT * FROM hotel_hotel WHERE status = 'Live';

-- Поиск рекомендуемых активных отелей
SELECT * FROM hotel_hotel WHERE status = 'Live' AND featured = true;

-- Поиск отелей по названию
SELECT * FROM hotel_hotel WHERE name ILIKE '%алакол%';
```

### Модель RoomType

#### Основные индексы:
- `idx_roomtype_price` - Индекс по цене номера
- `idx_roomtype_date` - Индекс по дате создания типа номера
- `idx_roomtype_capacity` - Индекс по вместимости номера
- `idx_roomtype_beds` - Индекс по количеству кроватей

#### Составные индексы:
- `idx_roomtype_hotel_price` - Отель + цена (для поиска номеров по цене в конкретном отеле)
- `idx_roomtype_hotel_capacity` - Отель + вместимость (для поиска по количеству гостей)

#### Полнотекстовый поиск:
- `idx_roomtype_type_trgm` - GIN индекс для поиска по типу номера

### Модель Room

#### Основные индексы:
- `idx_room_available` - Индекс по доступности номера
- `idx_room_number` - Индекс по номеру комнаты
- `idx_room_date` - Индекс по дате создания номера

#### Составные индексы:
- `idx_room_hotel_available` - Отель + доступность
- `idx_room_type_available` - Тип номера + доступность
- `idx_room_hotel_type` - Отель + тип номера

### Модель Booking

#### Основные индексы:
- `idx_booking_payment_status` - Статус оплаты
- `idx_booking_dates` - Даты заезда и выезда
- `idx_booking_checked_in` - Статус заселения
- `idx_booking_checked_out` - Статус выселения
- `idx_booking_is_active` - Активность бронирования
- `idx_booking_date` - Дата создания бронирования
- `idx_booking_robokassa_inv_id` - ID инвойса Robokassa

#### Составные индексы:
- `idx_booking_user_status` - Пользователь + статус оплаты
- `idx_booking_hotel_dates` - Отель + даты бронирования
- `idx_booking_hotel_status` - Отель + статус оплаты
- `idx_booking_user_active` - Пользователь + активность
- `idx_booking_status_dates` - Статус + даты (для отчетов)

### Модель Coupon

#### Основные индексы:
- `idx_coupon_code` - Код купона
- `idx_coupon_active` - Активность купона
- `idx_coupon_public` - Публичность купона
- `idx_coupon_valid_dates` - Даты действия купона
- `idx_coupon_date` - Дата создания
- `idx_coupon_type` - Тип скидки

#### Составные индексы:
- `idx_coupon_active_dates` - Активность + период действия
- `idx_coupon_public_active` - Публичность + активность

### Другие модели

#### RoomServices:
- `idx_roomservices_date` - Дата услуги
- `idx_roomservices_service_type` - Тип услуги
- `idx_roomservices_price` - Цена услуги
- `idx_roomservices_booking_date` - Бронирование + дата
- `idx_roomservices_room_date` - Номер + дата
- `idx_roomservices_type_date` - Тип + дата

#### Notification:
- `idx_notification_type` - Тип уведомления
- `idx_notification_seen` - Статус прочтения
- `idx_notification_date` - Дата уведомления
- `idx_notification_user_seen` - Пользователь + статус прочтения
- `idx_notification_user_type` - Пользователь + тип
- `idx_notification_booking_type` - Бронирование + тип

#### Review:
- `idx_review_active` - Активные отзывы
- `idx_review_rating` - Рейтинг
- `idx_review_date` - Дата отзыва
- `idx_review_hotel_active` - Отель + активность
- `idx_review_hotel_rating` - Отель + рейтинг
- `idx_review_user_hotel` - Пользователь + отель
- `idx_review_active_rating` - Активность + рейтинг

---

## 📅 BOOKING APP - Индексы

### Модель RoomUnavailability

#### Основные индексы:
- `idx_room_unavailability_reason` - Причина недоступности
- `idx_room_unavailability_created_at` - Дата создания записи
- `idx_room_unavailability_updated_at` - Дата обновления записи

#### Составные индексы:
- `idx_room_unavailability_room_dates` - Номер + период недоступности
- `idx_room_unavailability_dates_only` - Только даты (для поиска пересечений)

#### Специальные индексы:
- `idx_room_unavailability_overlap` - Частичный индекс для проверки пересечений дат

**Применение:**
```sql
-- Проверка недоступности номера на даты
SELECT * FROM booking_roomunavailability 
WHERE room_id = 1 
AND start_date <= '2024-12-31' 
AND end_date >= '2024-12-01';
```

---

## 👤 USERAUTHS APP - Индексы

### Модель User

#### Основные индексы:
- `idx_user_email_lower` - Email в нижнем регистре (для case-insensitive поиска)
- `idx_user_username` - Имя пользователя
- `idx_user_phone` - Телефон
- `idx_user_gender` - Пол
- `idx_user_is_active` - Активность пользователя
- `idx_user_date_joined` - Дата регистрации
- `idx_user_last_login` - Последний вход

#### Составные индексы:
- `idx_user_active_email` - Активность + email
- `idx_user_gender_active` - Пол + активность

#### Полнотекстовый поиск:
- `idx_user_fullname_trgm` - GIN индекс для поиска по полному имени

### Модель Profile

#### Основные индексы:
- `idx_profile_verified` - Статус верификации
- `idx_profile_date` - Дата создания профиля
- `idx_profile_country` - Страна
- `idx_profile_city` - Город
- `idx_profile_gender` - Пол
- `idx_profile_wallet` - Баланс кошелька

#### Составные индексы:
- `idx_profile_verified_country` - Верификация + страна
- `idx_profile_country_city` - Страна + город

#### Полнотекстовый поиск:
- `idx_profile_fullname_trgm` - GIN индекс для поиска по имени в профиле

### Модель UserConsent

#### Основные индексы:
- `idx_userconsent_consent_type` - Тип согласия
- `idx_userconsent_given_at` - Дата предоставления согласия
- `idx_userconsent_is_active` - Активность согласия
- `idx_userconsent_withdrawn_at` - Дата отзыва согласия
- `idx_userconsent_document_version` - Версия документа

#### Составные индексы:
- `idx_userconsent_user_type` - Пользователь + тип согласия
- `idx_userconsent_active_type` - Активность + тип
- `idx_userconsent_user_active` - Пользователь + активность
- `idx_userconsent_type_version` - Тип + версия документа

---

## ⚖️ LEGAL APP - Индексы

### Модель LegalDocument

#### Основные индексы:
- `idx_legaldocument_document_type` - Тип документа
- `idx_legaldocument_version` - Версия документа
- `idx_legaldocument_is_active` - Активность документа
- `idx_legaldocument_language` - Язык документа
- `idx_legaldocument_effective_date` - Дата вступления в силу
- `idx_legaldocument_created_at` - Дата создания

#### Составные индексы:
- `idx_legaldocument_type_active` - Тип + активность
- `idx_legaldocument_type_language` - Тип + язык
- `idx_legaldocument_active_language` - Активность + язык
- `idx_legaldocument_type_version_lang` - Тип + версия + язык

#### Полнотекстовый поиск:
- `idx_legaldocument_content_trgm` - GIN индекс для поиска по содержанию документа

### Модель DocumentView

#### Основные индексы:
- `idx_documentview_document_type` - Тип просматриваемого документа
- `idx_documentview_viewed_at` - Время просмотра

#### Составные индексы:
- `idx_documentview_user_type` - Пользователь + тип документа
- `idx_documentview_type_date` - Тип + дата просмотра
- `idx_documentview_user_date` - Пользователь + дата просмотра

---

## 🚀 Применение миграций

### Автоматическое применение:
```bash
python add_database_indexes.py
```

### Ручное применение:
```bash
python manage.py migrate hotel 0100_add_database_indexes
python manage.py migrate booking 0003_add_database_indexes
python manage.py migrate userauths 0013_add_database_indexes
python manage.py migrate legal 0003_add_database_indexes
```

### Проверка применения:
```sql
-- Проверка существующих индексов
SELECT schemaname, tablename, indexname, indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;
```

---

## 📊 Мониторинг индексов

### Статистика использования индексов:
```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Размер индексов:
```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Неиспользуемые индексы:
```sql
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
AND idx_scan = 0
AND indexname NOT LIKE '%_pkey';
```

---

## ⚡ Рекомендации по производительности

### Регулярное обслуживание:
1. **Обновление статистики:**
   ```sql
   ANALYZE;
   ```

2. **Переиндексация (при необходимости):**
   ```sql
   REINDEX INDEX CONCURRENTLY idx_hotel_status;
   ```

3. **Мониторинг фрагментации:**
   ```sql
   SELECT 
       schemaname, 
       tablename, 
       attname, 
       n_distinct, 
       correlation 
   FROM pg_stats 
   WHERE schemaname = 'public'
   ORDER BY abs(correlation) DESC;
   ```

### Настройки PostgreSQL:
```postgresql
# postgresql.conf
shared_buffers = 256MB          # 25% от RAM
effective_cache_size = 1GB      # 75% от RAM  
work_mem = 4MB                  # RAM / max_connections / 4
maintenance_work_mem = 64MB     # RAM / 16
checkpoint_completion_target = 0.9
wal_buffers = 16MB
```

### Оптимизация запросов:
- Используйте `EXPLAIN ANALYZE` для анализа планов выполнения
- Избегайте `SELECT *` в пользу конкретных полей
- Используйте `LIMIT` для ограничения результатов
- Применяйте пагинацию для больших наборов данных

---

## 🔧 Откат миграций

При необходимости отката индексов:

```bash
python manage.py migrate hotel 0099_auto_20241030_1715
python manage.py migrate booking 0002_alter_roomunavailability_created_at_and_more
python manage.py migrate userauths 0012_userconsent
python manage.py migrate legal 0002_remove_ip_address_from_documentview
```

---

## 📝 Примечания

- Все индексы созданы с `IF NOT EXISTS` для безопасного повторного применения
- Использовано расширение `pg_trgm` для полнотекстового поиска
- Составные индексы учитывают селективность полей
- Частичные индексы применены где это оправдано условиями

**Дата создания:** 2024-12-12  
**Версия:** 1.0  
**Автор:** AI Assistant 