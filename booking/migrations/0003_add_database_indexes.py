# Generated manually for database optimization
# This migration adds optimized indexes for PostgreSQL for booking app

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_alter_roomunavailability_created_at_and_more'),
    ]

    operations = [
        # RoomUnavailability дополнительные индексы (основной уже есть в модели)
        migrations.RunSQL(
            sql=[
                # Дополнительные индексы для RoomUnavailability
                "CREATE INDEX IF NOT EXISTS idx_room_unavailability_reason ON booking_roomunavailability(reason);",
                "CREATE INDEX IF NOT EXISTS idx_room_unavailability_created_at ON booking_roomunavailability(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_room_unavailability_updated_at ON booking_roomunavailability(updated_at);",
                
                # Составные индексы
                "CREATE INDEX IF NOT EXISTS idx_room_unavailability_room_dates ON booking_roomunavailability(room_id, start_date, end_date);",
                "CREATE INDEX IF NOT EXISTS idx_room_unavailability_dates_only ON booking_roomunavailability(start_date, end_date);",
                
                # Индекс для проверки пересечений дат
                "CREATE INDEX IF NOT EXISTS idx_room_unavailability_overlap ON booking_roomunavailability(room_id, start_date) WHERE end_date IS NOT NULL;",
            ],
            reverse_sql=[
                "DROP INDEX IF EXISTS idx_room_unavailability_reason;",
                "DROP INDEX IF EXISTS idx_room_unavailability_created_at;",
                "DROP INDEX IF EXISTS idx_room_unavailability_updated_at;",
                "DROP INDEX IF EXISTS idx_room_unavailability_room_dates;",
                "DROP INDEX IF EXISTS idx_room_unavailability_dates_only;",
                "DROP INDEX IF EXISTS idx_room_unavailability_overlap;",
            ]
        ),
    ] 