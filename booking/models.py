from django.db import models
from django.core.exceptions import ValidationError
from hotel.models import Room, Booking

class RoomUnavailability(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='Номер')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    reason = models.CharField(max_length=255, blank=True, verbose_name='Причина')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Недоступность номера'
        verbose_name_plural = 'Недоступность номеров'
        indexes = [
            models.Index(fields=['room', 'start_date', 'end_date']),
        ]

    def clean(self):
        # Проверяем, что дата окончания не раньше даты начала
        if self.end_date < self.start_date:
            raise ValidationError('Дата окончания не может быть раньше даты начала')

        # Проверяем пересечение с существующими бронированиями
        # Поскольку поле room в Booking теперь TextField, проверяем по отелю и типу номера
        overlapping_bookings = Booking.objects.filter(
            hotel=self.room.hotel,
            room_type=self.room.room_type,
            is_active=True,
            check_in_date__lt=self.end_date,
            check_out_date__gt=self.start_date,
            payment_status__in=["paid", "processing", "pending"]
        ).exclude(
            checked_out=True  # Исключаем уже выписанных гостей
        )
        
        # Дополнительно проверяем selection_data для более точного определения конкретного номера
        conflicting_bookings = []
        for booking in overlapping_bookings:
            # Проверяем, упоминается ли наш номер в selection_data
            if booking.selection_data and isinstance(booking.selection_data, dict):
                room_mentioned = False
                # Проверяем различные возможные структуры данных
                if 'rooms' in booking.selection_data:
                    for room_data in booking.selection_data['rooms']:
                        if isinstance(room_data, dict) and 'id' in room_data:
                            if int(room_data['id']) == self.room.id:
                                room_mentioned = True
                                break
                        elif isinstance(room_data, (int, str)) and str(room_data).isdigit():
                            if int(room_data) == self.room.id:
                                room_mentioned = True
                                break
                elif 'room_ids' in booking.selection_data:
                    if isinstance(booking.selection_data['room_ids'], list):
                        if self.room.id in booking.selection_data['room_ids']:
                            room_mentioned = True
                
                if room_mentioned:
                    conflicting_bookings.append(booking)
            else:
                # Если нет selection_data, считаем что есть конфликт (консервативный подход)
                conflicting_bookings.append(booking)
        
        if conflicting_bookings:
            booking_dates = []
            for booking in conflicting_bookings:
                booking_dates.append(
                    f"Booking ID - {booking.booking_id}: {booking.check_in_date} - {booking.check_out_date};"
                )
            raise ValidationError(
                'Выбранные даты пересекаются со следующими бронированиями:\n' + 
                '\n'.join(booking_dates)
            )

        # Проверяем пересечение с другими записями недоступности
        overlapping_unavailability = RoomUnavailability.objects.filter(
            room=self.room,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date
        )
        
        # Исключаем текущую запись при обновлении
        if self.pk:
            overlapping_unavailability = overlapping_unavailability.exclude(pk=self.pk)
            
        if overlapping_unavailability.exists():
            unavailability_dates = []
            for unavailability in overlapping_unavailability:
                unavailability_dates.append(
                    f"Период недоступности: {unavailability.start_date} - {unavailability.end_date}"
                )
            raise ValidationError(
                'Выбранные даты пересекаются со следующими периодами недоступности номера:\n' + 
                '\n'.join(unavailability_dates)
            )
        

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.room} - {self.start_date} до {self.end_date}"