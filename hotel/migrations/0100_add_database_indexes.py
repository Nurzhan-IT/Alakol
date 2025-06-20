# Generated manually for database optimization
# This migration adds optimized indexes for PostgreSQL

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0096_add_pg_trgm_extension'),
    ]

    operations = [
        # Hotel model indexes
        migrations.RunSQL(
            sql=[
                # Hotel основные индексы
                "CREATE INDEX IF NOT EXISTS idx_hotel_status ON hotel_hotel(status);",
                "CREATE INDEX IF NOT EXISTS idx_hotel_featured ON hotel_hotel(featured);",
                "CREATE INDEX IF NOT EXISTS idx_hotel_date ON hotel_hotel(date);",
                "CREATE INDEX IF NOT EXISTS idx_hotel_views ON hotel_hotel(views);",
                "CREATE INDEX IF NOT EXISTS idx_hotel_dates_range ON hotel_hotel(start_date, end_date);",
                
                # Составные индексы для Hotel
                "CREATE INDEX IF NOT EXISTS idx_hotel_status_featured ON hotel_hotel(status, featured);",
                "CREATE INDEX IF NOT EXISTS idx_hotel_user_status ON hotel_hotel(user_id, status);",
                
                # RoomType indexes
                "CREATE INDEX IF NOT EXISTS idx_roomtype_price ON hotel_roomtype(price);",
                "CREATE INDEX IF NOT EXISTS idx_roomtype_date ON hotel_roomtype(date);",
                "CREATE INDEX IF NOT EXISTS idx_roomtype_capacity ON hotel_roomtype(room_capacity);",
                "CREATE INDEX IF NOT EXISTS idx_roomtype_beds ON hotel_roomtype(number_of_beds);",
                
                # Составные индексы для RoomType
                "CREATE INDEX IF NOT EXISTS idx_roomtype_hotel_price ON hotel_roomtype(hotel_id, price);",
                "CREATE INDEX IF NOT EXISTS idx_roomtype_hotel_capacity ON hotel_roomtype(hotel_id, room_capacity);",
                
                # Room indexes
                "CREATE INDEX IF NOT EXISTS idx_room_available ON hotel_room(is_available);",
                "CREATE INDEX IF NOT EXISTS idx_room_number ON hotel_room(room_number);",
                "CREATE INDEX IF NOT EXISTS idx_room_date ON hotel_room(date);",
                
                # Составные индексы для Room
                "CREATE INDEX IF NOT EXISTS idx_room_hotel_available ON hotel_room(hotel_id, is_available);",
                "CREATE INDEX IF NOT EXISTS idx_room_type_available ON hotel_room(room_type_id, is_available);",
                "CREATE INDEX IF NOT EXISTS idx_room_hotel_type ON hotel_room(hotel_id, room_type_id);",
                
                # Booking indexes (дополнительные к уже существующим)
                "CREATE INDEX IF NOT EXISTS idx_booking_payment_status ON hotel_booking(payment_status);",
                "CREATE INDEX IF NOT EXISTS idx_booking_dates ON hotel_booking(check_in_date, check_out_date);",
                "CREATE INDEX IF NOT EXISTS idx_booking_checked_in ON hotel_booking(checked_in);",
                "CREATE INDEX IF NOT EXISTS idx_booking_checked_out ON hotel_booking(checked_out);",
                "CREATE INDEX IF NOT EXISTS idx_booking_is_active ON hotel_booking(is_active);",
                "CREATE INDEX IF NOT EXISTS idx_booking_date ON hotel_booking(date);",
                "CREATE INDEX IF NOT EXISTS idx_booking_robokassa_inv_id ON hotel_booking(robokassa_inv_id);",
                
                # Составные индексы для Booking
                "CREATE INDEX IF NOT EXISTS idx_booking_user_status ON hotel_booking(user_id, payment_status);",
                "CREATE INDEX IF NOT EXISTS idx_booking_hotel_dates ON hotel_booking(hotel_id, check_in_date, check_out_date);",
                "CREATE INDEX IF NOT EXISTS idx_booking_hotel_status ON hotel_booking(hotel_id, payment_status);",
                "CREATE INDEX IF NOT EXISTS idx_booking_user_active ON hotel_booking(user_id, is_active);",
                "CREATE INDEX IF NOT EXISTS idx_booking_status_dates ON hotel_booking(payment_status, check_in_date, check_out_date);",
                
                # Coupon indexes
                "CREATE INDEX IF NOT EXISTS idx_coupon_code ON hotel_coupon(code);",
                "CREATE INDEX IF NOT EXISTS idx_coupon_active ON hotel_coupon(active);",
                "CREATE INDEX IF NOT EXISTS idx_coupon_public ON hotel_coupon(make_public);",
                "CREATE INDEX IF NOT EXISTS idx_coupon_valid_dates ON hotel_coupon(valid_from, valid_to);",
                "CREATE INDEX IF NOT EXISTS idx_coupon_date ON hotel_coupon(date);",
                "CREATE INDEX IF NOT EXISTS idx_coupon_type ON hotel_coupon(type);",
                
                # Составные индексы для Coupon
                "CREATE INDEX IF NOT EXISTS idx_coupon_active_dates ON hotel_coupon(active, valid_from, valid_to);",
                "CREATE INDEX IF NOT EXISTS idx_coupon_public_active ON hotel_coupon(make_public, active);",
                
                # RoomServices indexes
                "CREATE INDEX IF NOT EXISTS idx_roomservices_date ON hotel_roomservices(date);",
                "CREATE INDEX IF NOT EXISTS idx_roomservices_service_type ON hotel_roomservices(service_type);",
                "CREATE INDEX IF NOT EXISTS idx_roomservices_price ON hotel_roomservices(price);",
                
                # Составные индексы для RoomServices
                "CREATE INDEX IF NOT EXISTS idx_roomservices_booking_date ON hotel_roomservices(booking_id, date);",
                "CREATE INDEX IF NOT EXISTS idx_roomservices_room_date ON hotel_roomservices(room_id, date);",
                "CREATE INDEX IF NOT EXISTS idx_roomservices_type_date ON hotel_roomservices(service_type, date);",
                
                # Notification indexes
                "CREATE INDEX IF NOT EXISTS idx_notification_type ON hotel_notification(type);",
                "CREATE INDEX IF NOT EXISTS idx_notification_seen ON hotel_notification(seen);",
                "CREATE INDEX IF NOT EXISTS idx_notification_date ON hotel_notification(date);",
                
                # Составные индексы для Notification
                "CREATE INDEX IF NOT EXISTS idx_notification_user_seen ON hotel_notification(user_id, seen);",
                "CREATE INDEX IF NOT EXISTS idx_notification_user_type ON hotel_notification(user_id, type);",
                "CREATE INDEX IF NOT EXISTS idx_notification_booking_type ON hotel_notification(booking_id, type);",
                
                # Bookmark indexes
                "CREATE INDEX IF NOT EXISTS idx_bookmark_date ON hotel_bookmark(date);",
                
                # Составной индекс для Bookmark
                "CREATE INDEX IF NOT EXISTS idx_bookmark_user_hotel ON hotel_bookmark(user_id, hotel_id);",
                
                # Review indexes
                "CREATE INDEX IF NOT EXISTS idx_review_active ON hotel_review(active);",
                "CREATE INDEX IF NOT EXISTS idx_review_rating ON hotel_review(rating);",
                "CREATE INDEX IF NOT EXISTS idx_review_date ON hotel_review(date);",
                
                # Составные индексы для Review
                "CREATE INDEX IF NOT EXISTS idx_review_hotel_active ON hotel_review(hotel_id, active);",
                "CREATE INDEX IF NOT EXISTS idx_review_hotel_rating ON hotel_review(hotel_id, rating);",
                "CREATE INDEX IF NOT EXISTS idx_review_user_hotel ON hotel_review(user_id, hotel_id);",
                "CREATE INDEX IF NOT EXISTS idx_review_active_rating ON hotel_review(active, rating);",
                
                # RoomTypeFeaturesDetailed indexes
                "CREATE INDEX IF NOT EXISTS idx_roomtype_features_detailed_type ON hotel_roomtypefeaturesdetailed(type_of_amenity);",
                
                # HotelFAQs indexes
                "CREATE INDEX IF NOT EXISTS idx_hotel_faqs_date ON hotel_hotelfaqs(date);",
                
                # Дополнительные функциональные индексы для текстового поиска
                "CREATE INDEX IF NOT EXISTS idx_hotel_name_trgm ON hotel_hotel USING gin(name gin_trgm_ops);",
                "CREATE INDEX IF NOT EXISTS idx_hotel_address_trgm ON hotel_hotel USING gin(address gin_trgm_ops);",
                "CREATE INDEX IF NOT EXISTS idx_roomtype_type_trgm ON hotel_roomtype USING gin(type gin_trgm_ops);",
                
            ],
            reverse_sql=[
                # Удаление индексов при откате миграции
                "DROP INDEX IF EXISTS idx_hotel_status;",
                "DROP INDEX IF EXISTS idx_hotel_featured;",
                "DROP INDEX IF EXISTS idx_hotel_date;",
                "DROP INDEX IF EXISTS idx_hotel_views;",
                "DROP INDEX IF EXISTS idx_hotel_dates_range;",
                "DROP INDEX IF EXISTS idx_hotel_status_featured;",
                "DROP INDEX IF EXISTS idx_hotel_user_status;",
                "DROP INDEX IF EXISTS idx_roomtype_price;",
                "DROP INDEX IF EXISTS idx_roomtype_date;",
                "DROP INDEX IF EXISTS idx_roomtype_capacity;",
                "DROP INDEX IF EXISTS idx_roomtype_beds;",
                "DROP INDEX IF EXISTS idx_roomtype_hotel_price;",
                "DROP INDEX IF EXISTS idx_roomtype_hotel_capacity;",
                "DROP INDEX IF EXISTS idx_room_available;",
                "DROP INDEX IF EXISTS idx_room_number;",
                "DROP INDEX IF EXISTS idx_room_date;",
                "DROP INDEX IF EXISTS idx_room_hotel_available;",
                "DROP INDEX IF EXISTS idx_room_type_available;",
                "DROP INDEX IF EXISTS idx_room_hotel_type;",
                "DROP INDEX IF EXISTS idx_booking_payment_status;",
                "DROP INDEX IF EXISTS idx_booking_dates;",
                "DROP INDEX IF EXISTS idx_booking_checked_in;",
                "DROP INDEX IF EXISTS idx_booking_checked_out;",
                "DROP INDEX IF EXISTS idx_booking_is_active;",
                "DROP INDEX IF EXISTS idx_booking_date;",
                "DROP INDEX IF EXISTS idx_booking_robokassa_inv_id;",
                "DROP INDEX IF EXISTS idx_booking_user_status;",
                "DROP INDEX IF EXISTS idx_booking_hotel_dates;",
                "DROP INDEX IF EXISTS idx_booking_hotel_status;",
                "DROP INDEX IF EXISTS idx_booking_user_active;",
                "DROP INDEX IF EXISTS idx_booking_status_dates;",
                "DROP INDEX IF EXISTS idx_coupon_code;",
                "DROP INDEX IF EXISTS idx_coupon_active;",
                "DROP INDEX IF EXISTS idx_coupon_public;",
                "DROP INDEX IF EXISTS idx_coupon_valid_dates;",
                "DROP INDEX IF EXISTS idx_coupon_date;",
                "DROP INDEX IF EXISTS idx_coupon_type;",
                "DROP INDEX IF EXISTS idx_coupon_active_dates;",
                "DROP INDEX IF EXISTS idx_coupon_public_active;",
                "DROP INDEX IF EXISTS idx_roomservices_date;",
                "DROP INDEX IF EXISTS idx_roomservices_service_type;",
                "DROP INDEX IF EXISTS idx_roomservices_price;",
                "DROP INDEX IF EXISTS idx_roomservices_booking_date;",
                "DROP INDEX IF EXISTS idx_roomservices_room_date;",
                "DROP INDEX IF EXISTS idx_roomservices_type_date;",
                "DROP INDEX IF EXISTS idx_notification_type;",
                "DROP INDEX IF EXISTS idx_notification_seen;",
                "DROP INDEX IF EXISTS idx_notification_date;",
                "DROP INDEX IF EXISTS idx_notification_user_seen;",
                "DROP INDEX IF EXISTS idx_notification_user_type;",
                "DROP INDEX IF EXISTS idx_notification_booking_type;",
                "DROP INDEX IF EXISTS idx_bookmark_date;",
                "DROP INDEX IF EXISTS idx_bookmark_user_hotel;",
                "DROP INDEX IF EXISTS idx_review_active;",
                "DROP INDEX IF EXISTS idx_review_rating;",
                "DROP INDEX IF EXISTS idx_review_date;",
                "DROP INDEX IF EXISTS idx_review_hotel_active;",
                "DROP INDEX IF EXISTS idx_review_hotel_rating;",
                "DROP INDEX IF EXISTS idx_review_user_hotel;",
                "DROP INDEX IF EXISTS idx_review_active_rating;",
                "DROP INDEX IF EXISTS idx_roomtype_features_detailed_type;",
                "DROP INDEX IF EXISTS idx_hotel_faqs_date;",
                "DROP INDEX IF EXISTS idx_hotel_name_trgm;",
                "DROP INDEX IF EXISTS idx_hotel_address_trgm;",
                "DROP INDEX IF EXISTS idx_roomtype_type_trgm;",
            ]
        ),
    ] 