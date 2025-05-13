from django.utils import timezone
from hotel.models import Booking

def handle_bookings_payment_status_processing_to_cancelled():
    try:
        expired_bookings = Booking.objects.filter(
            payment_status='Processing',
            expires_at__lt=timezone.now()
        )
        count = expired_bookings.update(payment_status='Cancelled')
        if count > 0:
            print(f"Cancelled {count} expired bookings.") 
        return f"Cancelled {count} expired bookings."  
    except Exception as e:
        print(f"Error cleaning expired bookings: {str(e)}")
        return f"Error: {str(e)}"  