import os
import django
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_prj.settings')

django.setup()

from hotel.services import handle_bookings_payment_status_processing_to_cancelled

if __name__ == '__main__':
    while True:
        try:
            handle_bookings_payment_status_processing_to_cancelled()
        except Exception as e:
            print(f"Error running handle_bookings_payment_status_processing_to_cancelled: {str(e)}")
        time.sleep(30)