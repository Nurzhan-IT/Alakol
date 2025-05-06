from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, date
from hotel.models import Booking
from hotel.services import handle_bookings_payment_status_processing_to_cancelled

class BookingTestCase(TestCase):
    def test_handle_expired_bookings(self):
        # Создаём просроченное бронирование
        booking = Booking.objects.create(
            payment_status='Processing',
            created_at=timezone.now() - timedelta(minutes=15),
            expires_at=timezone.now() - timedelta(minutes=5),
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=1),
            num_adults=1,
            total=100.00,
            before_discount=100.00,
            saved=0.00,
            total_days=1
        )
        # Выполняем очистку
        result = handle_bookings_payment_status_processing_to_cancelled()
        booking.refresh_from_db()
        self.assertEqual(booking.payment_status, 'Cancelled')
        self.assertEqual(result, 'Cancelled 1 expired bookings.')