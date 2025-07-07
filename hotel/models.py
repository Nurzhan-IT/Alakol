from django.db import models
from django.template.defaultfilters import escape
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from userauths.models import User

import shortuuid
from taggit.managers import TaggableManager

from django import forms
from multiupload.fields import MultiFileField

from django.utils import timezone
from datetime import timedelta

ICON_TPYE = (
    ('Bootstap Icons', 'Bootstap Icons'),
    ('Fontawesome Icons', 'Fontawesome Icons'),
)

ICON_CHOICES = [
    ('---','---'),
    ('air-conditioner.svg','Кондиционер'),
    ('balcony.svg','Балкон'),
    ('bar.svg','Бар'),
    ('bathrobe.svg','Халат'),
    ('bathtub.svg','Ванна'),
    ('cleaning.svg','Уборка'),
    ('coffee.svg','Кофеварка'),
    ('concierge.svg','Консьерж'),
    ('fridge.svg','Холодильник'),
    ('garden.svg','Беседка'),
    ('gym.svg','Спортзал'),
    ('hairdryer.svg','Фен'),
    ('iron.svg','Утюг'),
    ('laundry.svg','Прачечная'),
    ('microwave.svg','Микроволновка'),
    ('minibar.svg','Мини-бар'),
    ('no-smoking.svg','Для некурящих'),
    ('ocean-view.svg','Вид на море'),
    ('parking.svg','Парковка'),
    ('pets.svg','Разрешены животные'),
    ('playground.svg','Детская площадка'),
    ('entertainment.svg','Развлечения'),
    ('beach.svg','Пляж'),
    ('pool.svg','Бассейн'),
    ('restaurant.svg','Ресторан'),
    ('safe.svg','Сейф'),
    ('shower.svg','Душ'),
    ('shuttle.svg','Трансфер'),
    ('slippers.svg','Тапочки'),
    ('spa.svg','Спа'),
    ('tv.svg','Телевизор'),
    ('wifi.svg','Wi-Fi'),

]

ROOM_TYPES = (
    ('King', 'Королевский'),
    ('Luxury', 'Люкс'),
    ('Normal', 'Обычный'),
    ('Economic', 'Эконом'),
)


SERVICES_TYPES = (
    ('Food', 'Питание'),
    ('Cleaning', 'Уборка'),
    ('Technical', 'Техническое обслуживание'),
)

HOTEL_STATUS = (
    ("Draft", "Черновик"),
    ("Disabled", "Отключен"),
    ("Rejected", "Отклонен"),
    ("In Review", "На проверке"),
    ("Live", "Опубликован"),
)

GENDER = (
    ("Male", "Мужской"),
    ("Female", "Женский"),
)


DISCOUNT_TYPE = (
    ("Percentage", "Процент"),
    ("Flat Rate", "Фиксированная сумма"),
)

PAYMENT_STATUS = (
    ("paid", "Оплачено"),
    ("pending", "Ожидает"),
    ("processing", "Обрабатывается"),
    ("cancelled", "Отменено"),
    ("initiated", 'Инициировано'),
    ("failed", 'Не удалось'),
    ("refunding", 'Возвращается'),
    ("refunded", 'Возвращено'),
    ("unpaid", 'Не оплачено'),
    ("expired", 'Истекло'),
)



NOTIFICATION_TYPE = (
    ("Booking Confirmed", "Бронирование подтверждено"),
    ("Booking Cancelled", "Бронирование отменено"),
)


RATING = (
    ( 1,  "★☆☆☆☆"),
    ( 2,  "★★☆☆☆"),
    ( 3,  "★★★☆☆"),
    ( 4,  "★★★★☆"),
    ( 5,  "★★★★★"),
)

ROOM_TYPE_FEATURES_DETAILED = [
    ('private_bathroom', 'В частном санузле'),
    ('view', 'Вид'),
    ('services_amenities', 'Услуги и удобства'),
]

MEAL_PLAN_TYPES = (
    ("not_included", _("Не включено")),
    ("full_board", _("Трехразовое питание")),
    ("half_board_lunch_dinner", _("Двухразовое (обед + ужин)")),
    ("half_board_breakfast_lunch", _("Двухразовое (завтрак + обед)")),
    ("breakfast_only", _("Только завтрак")),
    ("lunch_only", _("Только обед")),
    ("dinner_only", _("Только ужин")),
)

MEAL_INCLUDED_IN_PRICE = (
    ("yes", "Да"),
    ("no", "Нет"),
)


class Hotel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    name = models.CharField(max_length=100, blank=True, verbose_name='Название')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    image = models.FileField(upload_to="hotel_gallery", verbose_name='Изображение')
    address = models.CharField(max_length=200, verbose_name='Адрес')
    mobile = models.CharField(max_length=20, verbose_name='Мобильный телефон')
    email = models.CharField(max_length=20, verbose_name='Электронная почта')
    status = models.CharField(choices=HOTEL_STATUS, max_length=10, default="published", null=True, blank=True, verbose_name='Статус')

    check_in_time = models.TimeField(null=True, blank=True, verbose_name='Время заезда')
    check_out_time = models.TimeField(null=True, blank=True, verbose_name='Время выезда')
    
    # Даты начала и окончания работы отеля
    start_date = models.DateField(null=True, blank=True, help_text="Дата начала работы отеля", verbose_name='Дата начала работы отеля')
    end_date = models.DateField(null=True, blank=True, help_text="Дата окончания работы отеля", verbose_name='Дата окончания работы отеля')

    # Поля для питания
    meal_plan_type = models.CharField(
        max_length=50, 
        choices=MEAL_PLAN_TYPES, 
        default="not_included", 
        verbose_name='Тип комплексного питания'
    )
    meal_included_in_price = models.CharField(
        max_length=3,
        choices=MEAL_INCLUDED_IN_PRICE,
        default="no",
        verbose_name='Включено ли питание в стоимость номера?'
    )

    # tags = TaggableManager(blank=True)
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    featured = models.BooleanField(default=False)
    hid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz", verbose_name='ID отеля')
    slug = models.SlugField(null=True, blank=True, verbose_name='Слаг')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.name
    
    def is_active_for_dates(self, check_in_date, check_out_date):
        """
        Проверяет, доступен ли отель для работы в указанный период дат
        
        Args:
            check_in_date (date): Дата заезда
            check_out_date (date): Дата выезда
            
        Returns:
            bool: True если отель доступен для указанных дат, иначе False
        """
        # Если даты работы отеля не указаны, считаем что отель доступен всегда
        if not self.start_date and not self.end_date:
            return True
            
        # Если указана только дата начала работы
        if self.start_date and not self.end_date:
            return check_in_date >= self.start_date
            
        # Если указана только дата окончания работы
        if not self.start_date and self.end_date:
            return check_out_date <= self.end_date
            
        # Если указаны обе даты
        return check_in_date >= self.start_date and check_out_date <= self.end_date
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.name) + "-" + str(uniqueid.lower())
            
        super(Hotel, self).save(*args, **kwargs) 

    def thumbnail(self):
        return mark_safe('<img src="%s" width="50" height="50" style="object-fit:cover; border-radius: 6px;" />' % (self.image.url))
    
    thumbnail.short_description = 'Миниатюра'

    def hotel_gallery(self):
        return HotelGallery.objects.filter(hotel=self)

    def hotel_features(self):
        return HotelFeatures.objects.filter(hotel=self)

    def hotel_faqs(self):
        return HotelFAQs.objects.filter(hotel=self)

    def hotel_room_types(self):
        return RoomType.objects.filter(hotel=self)
    
    def hotel_meal_plans(self):
        return HotelMealPlan.objects.filter(hotel=self)
    
    def average_rating(self):
        average_rating = Review.objects.filter(hotel=self, active=True).aggregate(avg_rating=models.Avg("rating"))
        return average_rating['avg_rating']
    
    def rating_count(self):
        rating_count = Review.objects.filter(hotel=self, active=True).count()
        return rating_count
    


class HotelGallery(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name='Отель')
    image = models.FileField(upload_to="hotel_gallery", verbose_name='Изображение')
    hgid = models.CharField(max_length=20, blank=True, verbose_name='ID галереи')

    def save(self, *args, **kwargs):
        # Генерация уникального hgid, если оно отсутствует
        if not self.hgid:
            self.hgid = shortuuid.uuid()[:10]

        while HotelGallery.objects.filter(hgid=self.hgid).exists():
            self.hgid = shortuuid.uuid()[:10]  # Regenerate if it already exists
    
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.hotel)
    
    def thumbnail(self):
        """Возвращает HTML для отображения миниатюры изображения"""
        if self.image:
            # Экранируем название отеля для безопасности
            hotel_name_escaped = escape(self.hotel.name) if self.hotel.name else 'Отель'
            return mark_safe(f'''
                <div class="hotel-gallery-thumbnail" 
                     data-image-url="{self.image.url}" 
                     data-hotel-name="{hotel_name_escaped}"
                     style="cursor: pointer;">
                    <img src="{self.image.url}" 
                         style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd; cursor: pointer; transition: transform 0.2s ease;" 
                         title="Нажмите, чтобы открыть в модальном окне">
                </div>
            ''')
        return "Нет изображения"
    thumbnail.short_description = 'Миниатюра'

    class Meta:
        verbose_name_plural = "Галерея отеля"

class HotelFeatures(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name='Отель')
    # icon_type = models.CharField(max_length=100, null=True, blank=True, choices=ICON_TPYE)
    icon = models.CharField(max_length=100, null=True, blank=True, verbose_name='Иконка')
    name = models.CharField(max_length=35, verbose_name='Название')
    hfid = models.CharField(max_length=20, blank=True, verbose_name='ID особенности')

    def save(self, *args, **kwargs):
        # Генерация уникального hfid, если оно отсутствует
        if not self.hfid:
            self.hfid = shortuuid.uuid()[:10]

        while HotelFeatures.objects.filter(hfid=self.hfid).exists():
            self.hfid = shortuuid.uuid()[:10]  # Regenerate if it already exists
    
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.hotel)
    
    class Meta:
        verbose_name_plural = "Удобства отеля"
    
class HotelFAQs(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name='Отель')
    question = models.CharField(max_length=1000, verbose_name='Вопрос')
    answer = models.TextField(null=True, blank=True, verbose_name='Ответ')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    hfid = models.CharField(max_length=20, blank=True, verbose_name='ID FAQ')

    def save(self, *args, **kwargs):
        # Генерация уникального hfid, если оно отсутствует
        if not self.hfid:
            self.hfid = shortuuid.uuid()[:10]

        while HotelFAQs.objects.filter(hfid=self.hfid).exists():
            self.hfid = shortuuid.uuid()[:10]  # Regenerate if it already exists
    
        super().save(*args, **kwargs)


    def __str__(self):
        return str(self.hotel)
    
    class Meta:
        verbose_name_plural = "Вопрос/Ответ"

class HotelMealPlan(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name='Отель')
    price_per_day = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='Цена за день')
    age_min = models.PositiveIntegerField(default=0, verbose_name='Минимальный возраст')
    age_max = models.PositiveIntegerField(null=True, blank=True, verbose_name='Максимальный возраст')
    hmpid = models.CharField(max_length=20, blank=True, verbose_name='ID плана питания')

    def save(self, *args, **kwargs):
        # Генерация уникального hmpid, если оно отсутствует
        if not self.hmpid:
            self.hmpid = shortuuid.uuid()[:10]

        while HotelMealPlan.objects.filter(hmpid=self.hmpid).exists():
            self.hmpid = shortuuid.uuid()[:10]  # Regenerate if it already exists
    
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.hotel.name} - {self.price_per_day} тенге"
    
    class Meta:
        verbose_name = 'План питания отеля'
        verbose_name_plural = "Планы питания отеля"
        ordering = ['price_per_day']

class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name='Отель')
    type = models.CharField(max_length=120, verbose_name='Тип')
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='Цена')
    dynamic_pricing = models.JSONField(null=True, blank=True, default=dict, verbose_name='Динамические цены')  # Используем default=dict для инициализации пустым словарем
    number_of_beds = models.PositiveIntegerField(default=0, verbose_name='Количество кроватей')
    room_capacity = models.PositiveIntegerField(default=0, verbose_name='Вместимость')
    room_size = models.IntegerField(default=0, verbose_name="Размер комнаты (м²)")
    rtid = models.CharField(max_length=20, blank=True, verbose_name='ID типа номера')
    slug = models.SlugField(null=True, blank=True, unique=True, verbose_name='Слаг')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Тип комнаты'
        verbose_name_plural = 'Типы комнат'

    def __str__(self):
        return f"{self.type} - {self.hotel.name} - {self.price}"

    def rooms_count(self):
        return Room.objects.filter(room_type=self).count()
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.type) + "-" + str(uniqueid.lower())

        # Генерация уникального rtid, если оно отсутствует
        if not self.rtid:
            self.rtid = shortuuid.uuid()[:10]

        while RoomType.objects.filter(rtid=self.rtid).exists():
            self.rtid = shortuuid.uuid()[:10]  # Regenerate if it already exists
    
        super(RoomType, self).save(*args, **kwargs)
         
    def get_price_for_date(self, date):
        """
        Возвращает цену для указанной даты. Если нет динамической цены, возвращает базовую цену.
        """
        if self.dynamic_pricing and isinstance(self.dynamic_pricing, dict):
            date_str = date.strftime("%Y-%m-%d")
            return self.dynamic_pricing.get(date_str, self.price)
        return self.price



class RoomTypeDescription(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name='Отель')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='roomtype_description', verbose_name='Тип номера')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')

    def __str__(self):
        return str(self.hotel)
    class Meta:
        verbose_name_plural = "Описание типа номера"
        constraints = [
            models.UniqueConstraint(fields=['room_type'], name='unique_room_type_description')
        ]

class RoomTypeGallery(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name='Отель')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='roomtype_gallery', verbose_name='Тип номера')
    image = models.ImageField(upload_to='room_type_images/', verbose_name='Изображение')

    def __str__(self):
        return str(self.room_type)
    
    def thumbnail(self):
        """Возвращает HTML для отображения миниатюры изображения"""
        if self.image:
            # Экранируем название типа номера для безопасности
            room_type_name_escaped = escape(self.room_type.type) if self.room_type.type else 'Тип номера'
            return mark_safe(f'''
                <div class="roomtype-gallery-thumbnail" 
                     data-image-url="{self.image.url}" 
                     data-room-type-name="{room_type_name_escaped}"
                     style="cursor: pointer;">
                    <img src="{self.image.url}" 
                         style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd; cursor: pointer; transition: transform 0.2s ease;" 
                         title="Нажмите, чтобы открыть в модальном окне">
                </div>
            ''')
        return "Нет изображения"
    thumbnail.short_description = 'Миниатюра'
    
    class Meta:
        verbose_name_plural = "Галерея типа номера"

class RoomTypeFeatures(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name='Отель')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='roomtype_features', verbose_name='Тип номера')
    icon = models.CharField(max_length=100, null=True, blank=True, verbose_name='Иконка')
    name = models.CharField(max_length=100, verbose_name='Название')
    hfid = models.CharField(max_length=20, blank=True, verbose_name='ID особенности')

    def save(self, *args, **kwargs):
        # Генерация уникального hfid, если оно отсутствует
        if not self.hfid:
            self.hfid = shortuuid.uuid()[:10]

        while RoomTypeFeatures.objects.filter(hfid=self.hfid).exists():
            self.hfid = shortuuid.uuid()[:10]  # Regenerate if it already exists
    
        super().save(*args, **kwargs)


    def __str__(self):
        return str(self.hotel)
    
    class Meta:
        verbose_name_plural = "Удобства типа номера"

class RoomTypeFeaturesDetailed(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name='Отель')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='roomtype_features_detailed', verbose_name='Тип номера')
    type_of_amenity = models.CharField(max_length=100, null=True, choices=ROOM_TYPE_FEATURES_DETAILED, verbose_name='Тип удобства')
    text = models.CharField(max_length=100, verbose_name='Текст')
    hfid = models.CharField(max_length=20, blank=True, verbose_name='ID особенности')

    def save(self, *args, **kwargs):
        # Генерация уникального hfid, если оно отсутствует
        if not self.hfid:
            self.hfid = shortuuid.uuid()[:10]

        while RoomTypeFeaturesDetailed.objects.filter(hfid=self.hfid).exists():
            self.hfid = shortuuid.uuid()[:10]  # Regenerate if it already exists
    
        super().save(*args, **kwargs)


    def __str__(self):
        return str(self.hotel)
    
    class Meta:
        verbose_name_plural = "Удобства типа номера подробно"

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name='Отель')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, verbose_name='Тип номера')
    room_number = models.CharField(max_length=10, verbose_name='Номер комнаты')
    is_available = models.BooleanField(default=True, verbose_name='Доступен')
    rid = models.CharField(max_length=20, blank=True, verbose_name='ID номера')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def save(self, *args, **kwargs):
        # Генерация уникального rid, если оно отсутствует
        if not self.rid:
            self.rid = shortuuid.uuid()[:10]

        while Room.objects.filter(rid=self.rid).exists():
            self.rid = shortuuid.uuid()[:10]  # Regenerate if it already exists
    
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.hotel.name} - {self.room_type.type} -  Room {self.room_number}"

    def price(self):
        return self.room_type.price
    
    def number_of_beds(self):
        return self.room_type.number_of_beds
    
    def room_capacity(self):
        return self.room_type.room_capacity
    


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="initiated", verbose_name='Статус оплаты')

    full_name = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Полное имя')
    email = models.EmailField(null=True, blank=True, verbose_name='Электронная почта')
    country_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='Код страны')
    phone = models.CharField(max_length=1000, null=True, blank=True, verbose_name='Телефон')
    
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, verbose_name='Отель')
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True, verbose_name='Тип номера')
    room = models.ManyToManyField(Room, verbose_name='Номера')
    selection_data = models.JSONField(null=True, blank=True, help_text="Данные о выбранных номерах из selection_data_obj", verbose_name='Данные выбора')
    before_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='До скидки')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='Итого')
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='Сэкономлено')
    prepayment = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='Предоплата (10%)', help_text='10% от общей суммы')
    payment_for_hotel = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='К оплате отелю (90%)', help_text='90% от общей суммы')
    check_in_date = models.DateField(verbose_name='Дата заезда')
    check_out_date = models.DateField(verbose_name='Дата выезда')
    total_days = models.PositiveIntegerField(default=0, verbose_name='Кол-во дней')
    num_adults = models.PositiveIntegerField(default=1, verbose_name='Взрослые')
    num_children = models.PositiveIntegerField(default=0, verbose_name='Дети')
    checked_in = models.BooleanField(default=False, verbose_name='Заселен')
    checked_out = models.BooleanField(default=False, verbose_name='Выселен')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    checked_in_tracker = models.BooleanField(default=False, help_text="DO NOT CHECK THIS BOX", verbose_name='Трекер заселения')
    checked_out_tracker = models.BooleanField(default=False, help_text="DO NOT CHECK THIS BOX", verbose_name='Трекер выселения')
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Дата создания')
    coupons = models.ManyToManyField("hotel.Coupon", blank=True, verbose_name='Купоны')
    booking_id = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz", verbose_name='ID бронирования')
    robokassa_inv_id = models.IntegerField(null=True, blank=True, help_text="InvId from Robokassa payment system", verbose_name='ID инвойса Robokassa')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True, blank=True, verbose_name='Создано в')
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name='Истекает в')
    
    # Поле для сохранения legal agreements при бронировании
    legal_agreements = models.JSONField(null=True, blank=True, help_text="Согласия с юридическими документами при оплате", verbose_name='Юридические согласия')

    def save(self, *args, **kwargs):
        # Устанавливаем expires_at при создании записи
        if not self.pk and not self.expires_at:  # Проверяем, что это новая запись
            self.expires_at = self.created_at + timedelta(minutes=10) if self.created_at else timezone.now() + timedelta(minutes=10)
        
        # Автоматически рассчитываем предоплату (10%) и платеж отелю (90%)
        if self.total:
            from decimal import Decimal
            # Приводим total к Decimal для корректных вычислений
            total_decimal = Decimal(str(self.total))
            self.prepayment = total_decimal * Decimal('0.10')
            self.payment_for_hotel = total_decimal * Decimal('0.90')
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id}"
    
    def rooms(self):
        return self.room.all().count()
    
    rooms.short_description = 'Количество номеров'
    
    class Meta:
        indexes = [
            models.Index(fields=['expires_at']),
        ]
    
# class ActivityLog(models.Model):
#     booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
#     guest_out = models.DateTimeField()
#     guest_in = models.DateTimeField()
#     description = models.TextField(null=True, blank=True)
#     date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

#     def __str__(self):
#         return str(self.booking)
    
# class StaffOnDuty(models.Model):
#     booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
#     staff_id = models.CharField(null=True, blank=True, max_length=100)
#     date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

#     def __str__(self):
#         return str(self.staff_id)
    

class Coupon(models.Model):
    code = models.CharField(max_length=1000, verbose_name='Код')
    type = models.CharField(max_length=100, choices=DISCOUNT_TYPE, default="Percentage", verbose_name='Тип')
    discount = models.IntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Скидка')
    redemption = models.IntegerField(default=0, verbose_name='Количество использований')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    active = models.BooleanField(default=True, verbose_name='Активен')
    make_public = models.BooleanField(default=False, verbose_name='Сделать публичным')
    valid_from = models.DateField(verbose_name='Действителен с')
    valid_to = models.DateField(verbose_name='Действителен до')
    cid = ShortUUIDField(length=10, max_length=25, alphabet="abcdefghijklmnopqrstuvxyz", verbose_name='ID купона')

    
    def __str__(self):
        return self.code
    
    class Meta:
        ordering =['-id']


class CouponUsers(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, verbose_name='Купон')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, verbose_name='Бронирование')
    
    full_name = models.CharField(max_length=1000, verbose_name='Полное имя')
    email = models.CharField(max_length=1000, verbose_name='Электронная почта')
    mobile = models.CharField(max_length=1000, verbose_name='Мобильный телефон')

    def __str__(self):
        return str(self.coupon.code)
    
    class Meta:
        ordering =['-id']


class RoomServices(models.Model):
    booking = models.ForeignKey(Booking, null=True, on_delete=models.CASCADE, verbose_name='Бронирование')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='Номер')
    date = models.DateField(auto_now_add=True, verbose_name='Дата')
    service_type = models.CharField(max_length=20, choices=SERVICES_TYPES, verbose_name='Тип услуги')
    price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, verbose_name='Цена')

    def str(self):
        return str(self.booking) + " " + str(self.room) + " " + str(self.service_type)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user", verbose_name='Пользователь')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Бронирование')
    type = models.CharField(max_length=100, default="new_order", choices=NOTIFICATION_TYPE, verbose_name='Тип')
    seen = models.BooleanField(default=False, verbose_name='Просмотрено')
    nid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz", verbose_name='ID уведомления')
    date = models.DateField(auto_now_add=True, verbose_name='Дата')
    
    def __str__(self):
        if self.user:
            return str(self.user.username)
        elif self.booking:
            return f"Уведомление {self.type} для бронирования {self.booking.booking_id}"
        else:
            return f"Уведомление {self.nid}"
    
    class Meta:
        ordering = ['-date']


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Пользователь')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Отель')
    bid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz", verbose_name='ID закладки')
    date = models.DateField(auto_now_add=True, verbose_name='Дата')
    
    def __str__(self):
        if self.user:
            return str(self.user.username)
        elif self.hotel:
            return f"Закладка на отель {self.hotel.name}"
        else:
            return f"Закладка {self.bid}"
    
    class Meta:
        ordering = ['-date']



class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Пользователь')
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, blank=True, null=True, related_name="reviews", verbose_name='Отель')
    review = models.TextField(null=True, blank=True, verbose_name='Отзыв')
    reply = models.CharField(null=True, blank=True, max_length=1000, verbose_name='Ответ')
    rating = models.IntegerField(choices=RATING, default=None, verbose_name='Рейтинг')
    active = models.BooleanField(default=False, verbose_name='Активен')
    helpful = models.ManyToManyField(User, blank=True, related_name="helpful", verbose_name='Полезно')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name_plural = "Reviews & Rating"
        ordering = ["-date"]
        
    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.rating}"
        elif self.hotel:
            return f"Отзыв на отель {self.hotel.name} - {self.rating}"
        else:
            return f"Отзыв #{self.id} - {self.rating}"
        
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name_plural = "Reviews & Rating"
        ordering = ["-date"]
        
    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.rating}"
        elif self.hotel:
            return f"Отзыв на отель {self.hotel.name} - {self.rating}"
        else:
            return f"Отзыв #{self.id} - {self.rating}"
        