from django.core.management.base import BaseCommand
from django.db import transaction
from hotel.models import Booking, Room
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Преобразует данные о номерах в бронированиях из ManyToManyField в текстовое поле'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет сделано, но не вносить изменений'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Размер батча для обработки (по умолчанию: 100)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        
        self.stdout.write(self.style.SUCCESS('Начинаю преобразование данных о номерах в бронированиях...'))
        
        # Получаем все бронирования, где поле room пустое или None
        bookings = Booking.objects.filter(room__isnull=True) | Booking.objects.filter(room='')
        total_bookings = bookings.count()
        
        self.stdout.write(f'Найдено {total_bookings} бронирований для обработки')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Режим dry-run: изменения не будут сохранены'))
        
        processed = 0
        updated = 0
        
        # Обрабатываем в батчах
        for offset in range(0, total_bookings, batch_size):
            batch = bookings[offset:offset + batch_size]
            
            with transaction.atomic():
                for booking in batch:
                    processed += 1
                    
                    # Здесь раньше были связанные номера через ManyToManyField
                    # Теперь нужно восстановить информацию из selection_data или использовать room_type
                    room_texts = []
                    
                    if booking.selection_data:
                        for item_id, item in booking.selection_data.items():
                            # Сначала пытаемся получить название из room_name в selection_data
                            room_type_name = item.get('room_name', '')
                            room_number = item.get('room_number', 'N/A')
                            
                            # Если room_name пустое или "Basic", пытаемся получить из room_type
                            if not room_type_name or room_type_name == 'Basic':
                                room_type_id = item.get('room_type')
                                if room_type_id:
                                    try:
                                        from hotel.models import RoomType
                                        room_type_obj = RoomType.objects.get(id=room_type_id)
                                        room_type_name = room_type_obj.type
                                    except RoomType.DoesNotExist:
                                        room_type_name = 'Неизвестный тип'
                            
                            # Форматируем в нужном виде: "Тип номера - №номер"
                            formatted_room = f"{room_type_name} - №{room_number}"
                            room_texts.append(formatted_room)
                    
                    elif booking.room_type:
                        # Если нет selection_data, используем room_type из бронирования
                        room_type_name = booking.room_type.type
                        room_texts.append(f"{room_type_name} - №N/A")
                    
                    if room_texts:
                        new_room_text = '\n'.join(room_texts)
                        
                        if not dry_run:
                            booking.room = new_room_text
                            booking.save(update_fields=['room'])
                            updated += 1
                        else:
                            self.stdout.write(f'Бронирование {booking.booking_id}: {new_room_text}')
                    
                    # Показываем прогресс каждые 50 записей
                    if processed % 50 == 0:
                        self.stdout.write(f'Обработано {processed}/{total_bookings} бронирований')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Преобразование завершено. Обработано: {processed}, Обновлено: {updated}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Dry-run завершен. Было бы обработано: {processed} бронирований'
                )
            ) 