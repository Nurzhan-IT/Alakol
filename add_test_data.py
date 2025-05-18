import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_prj.settings')
django.setup()

from hotel.models import RoomType
from datetime import datetime, timedelta

def add_test_dynamic_pricing():
    # Получаем все типы комнат
    room_types = RoomType.objects.all()
    
    if not room_types:
        print("Типы комнат не найдены")
        return
    
    # Текущая дата и даты для диапазонов
    today = datetime.now().date()
    
    # Создаем тестовые диапазоны дат и цены
    date_ranges = []
    for i in range(5):
        start_date = today + timedelta(days=i*7)
        end_date = start_date + timedelta(days=6)
        date_ranges.append((start_date, end_date))
    
    # Заполняем динамические цены для каждого типа комнаты
    for i, room_type in enumerate(room_types):
        if not room_type.dynamic_pricing:
            room_type.dynamic_pricing = {}
        
        # Базовая цена для этого типа комнаты
        base_price = float(room_type.price) if room_type.price else 10000
        
        # Заполняем цены для каждого дня в каждом диапазоне
        for range_index, (start_date, end_date) in enumerate(date_ranges):
            # Увеличиваем цену для каждого следующего диапазона
            price_multiplier = 1 + (range_index * 0.1)
            current_date = start_date
            
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                # Добавляем немного случайности в цену для разнообразия
                day_price = int(base_price * price_multiplier * (1 + (i * 0.2)))
                room_type.dynamic_pricing[date_str] = day_price
                current_date += timedelta(days=1)
        
        # Сохраняем изменения
        room_type.save()
        print(f"Обновлен тип комнаты: {room_type.type}, добавлено динамических цен: {len(room_type.dynamic_pricing)}")

if __name__ == "__main__":
    add_test_dynamic_pricing()
    print("Тестовые данные успешно добавлены!") 