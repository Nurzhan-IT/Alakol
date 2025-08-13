from django import forms
from django.contrib import admin
from hotel.models import  ICON_CHOICES,Hotel, Room, Booking, RoomServices, HotelGallery, RoomTypeGallery,RoomTypeFeatures, HotelFeatures, HotelFAQs, RoomType, Coupon, CouponUsers, Notification, Bookmark, Review, RoomTypeFeaturesDetailed, HotelMealPlan

from django.utils.html import mark_safe

from modeltranslation.admin import TranslationAdmin

from .widgets import IconSelectWidget, SimpleTextEditorWidget, RoomTypeSelectWidget, DDMMDateInput

from django.shortcuts import render
from django.urls import reverse
from django.utils.html import format_html
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test

from django import forms
from django.core.exceptions import ValidationError
import json
from django.core.serializers.json import DjangoJSONEncoder

from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from import_export.admin import ExportMixin

class MultipleFileInput(forms.ClearableFileInput):
    """
    Виджет для множественной загрузки файлов
    """
    allow_multiple_selected = True
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is None:
            attrs = {}
        attrs.update({
            'multiple': True,
            'accept': 'image/*',
            'class': 'form-control'
        })
        self.attrs = attrs

class MultipleFileField(forms.FileField):
    """
    Поле для множественной загрузки файлов
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class HotelGalleryForm(forms.ModelForm):
    """
    Кастомная форма для HotelGallery с возможностью множественной загрузки
    """
    multiple_images = MultipleFileField(
        required=False,
        label='Загрузить несколько изображений',
        help_text='Выберите несколько изображений для загрузки (поддерживаются JPG, PNG, WEBP)'
    )
    
    class Meta:
        model = HotelGallery
        fields = ['hotel', 'image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем стандартное поле image, если используется множественная загрузка
        if 'multiple_images' in self.fields:
            self.fields['image'].required = False
            # Добавляем подсказку для обычного поля image
            self.fields['image'].help_text = 'Загрузите одно изображение или используйте поле выше для нескольких'
            
    def clean_multiple_images(self):
        """
        Валидация множественных файлов
        """
        files = self.cleaned_data.get('multiple_images')
        if files:
            # Проверяем каждый файл
            for file in files:
                if file:
                    # Проверяем размер файла (максимум 5MB)
                    if file.size > 5 * 1024 * 1024:
                        raise forms.ValidationError(f'Файл {file.name} слишком большой. Максимальный размер 5MB.')
                    
                    # Проверяем тип файла
                    if not file.content_type.startswith('image/'):
                        raise forms.ValidationError(f'Файл {file.name} не является изображением.')
        
        return files

class HotelGalleryFormSet(forms.models.BaseInlineFormSet):
    """
    Кастомный формсет для обработки множественной загрузки
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_delete = True
        
    def clean(self):
        """
        Кастомная валидация для формсета
        """
        super().clean()
        
        # Проверяем общее количество изображений
        total_images = 0
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                if form.cleaned_data.get('image'):
                    total_images += 1
                if form.cleaned_data.get('multiple_images'):
                    total_images += len(form.cleaned_data.get('multiple_images'))
        
        # Ограничиваем общее количество изображений (например, максимум 10 для одного отеля)
        if total_images > 10:
            raise forms.ValidationError('Максимальное количество изображений для одного отеля - 10.')
        
    def save(self, commit=True):
        """
        Переопределяем сохранение для обработки множественных файлов
        """
        instances = super().save(commit=False)
        
        # Обрабатываем множественную загрузку файлов из форм
        for form in self.forms:
            if hasattr(form, 'cleaned_data') and form.cleaned_data:
                multiple_files = form.cleaned_data.get('multiple_images')
                if multiple_files and not form.cleaned_data.get('DELETE', False):
                    for file in multiple_files:
                        if file:
                            gallery_instance = HotelGallery(
                                hotel=self.instance,
                                image=file
                            )
                            if commit:
                                gallery_instance.save()
                            instances.append(gallery_instance)
        
        if commit:
            for instance in instances:
                instance.save()
            self.save_m2m()
        
        return instances

class RussianModelAdminMixin:
    """
    Миксин для переопределения verbose_name моделей в breadcrumb без изменения Meta класса
    """
    
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        # Переопределяем verbose_name для breadcrumb
        self._setup_russian_verbose_names()
    
    def _setup_russian_verbose_names(self):
        """Устанавливает русские названия для модели"""
        model_translations = {
            'Hotel': ('Отель', 'Отели'),
            'Room': ('Номер', 'Номера'), 
            'RoomType': ('Тип номера', 'Типы номеров'),
            'Booking': ('Бронирование', 'Бронирования'),
            'RoomServices': ('Услуга номера', 'Услуги номеров'),
            'Coupon': ('Купон', 'Купоны'),
            'Notification': ('Уведомление', 'Уведомления'),
            'Bookmark': ('Закладка', 'Закладки'),
            'Review': ('Отзыв', 'Отзывы'),
            'User': ('Пользователь', 'Пользователи'),
            'Profile': ('Профиль', 'Профили'),
            'RoomUnavailability': ('Недоступность номера', 'Недоступность номеров'),
        }
        
        model_name = self.model.__name__
        if model_name in model_translations:
            verbose_name, verbose_name_plural = model_translations[model_name]
            # Создаем копию _meta для избежания изменения оригинальной модели
            self.model._meta.verbose_name = verbose_name
            self.model._meta.verbose_name_plural = verbose_name_plural
    
    def get_model_perms(self, request):
        """Переопределяем разрешения с русскими названиями"""
        perms = super().get_model_perms(request)
        return perms

# Проверка принадлежности пользователя к группе Manager
def is_manager(user):
    return user.groups.filter(name='Manager').exists() and not user.is_superuser

# Действия для массового удаления с проверкой связанных бронирований
def delete_roomtypes_with_check(modeladmin, request, queryset):
    """
    Кастомное действие для массового удаления типов номеров с проверкой связанных записей бронирования
    """
    from hotel.models import Booking
    from django.contrib import messages
    
    roomtypes_with_bookings = []
    roomtypes_to_delete = []
    
    for roomtype in queryset:
        if Booking.objects.filter(room_type=roomtype).exists():
            roomtypes_with_bookings.append(roomtype.type)
        else:
            roomtypes_to_delete.append(roomtype)
    
    if roomtypes_with_bookings:
        messages.error(request, 
            f'Невозможно удалить следующие типы номеров так как с ними связаны записи бронирования: {", ".join(roomtypes_with_bookings)}. '
            f'Для удаления необходимо связаться с поддержкой сайта support@ekol.kz')
    
    if roomtypes_to_delete:
        deleted_count = len(roomtypes_to_delete)
        for roomtype in roomtypes_to_delete:
            roomtype.delete()
        messages.success(request, f'Успешно удалено {deleted_count} типов номеров')

delete_roomtypes_with_check.short_description = 'Удалить выбранные типы номеров'

def delete_hotels_with_check(modeladmin, request, queryset):
    """
    Кастомное действие для массового удаления отелей с проверкой связанных записей бронирования
    """
    from hotel.models import Booking
    from django.contrib import messages
    
    hotels_with_bookings = []
    hotels_to_delete = []
    
    for hotel in queryset:
        if Booking.objects.filter(hotel=hotel).exists():
            hotels_with_bookings.append(hotel.name)
        else:
            hotels_to_delete.append(hotel)
    
    if hotels_with_bookings:
        messages.error(request, 
            f'Невозможно удалить следующие отели так как с ними связаны записи бронирования: {", ".join(hotels_with_bookings)}. '
            f'Для удаления необходимо связаться с поддержкой сайта support@ekol.kz')
    
    if hotels_to_delete:
        deleted_count = len(hotels_to_delete)
        for hotel in hotels_to_delete:
            hotel.delete()
        messages.success(request, f'Успешно удалено {deleted_count} отелей')

delete_hotels_with_check.short_description = 'Удалить выбранные отели'

class BaseExportAdmin(ExportMixin, admin.ModelAdmin):
    pass

class HotelAdminForm(forms.ModelForm):
    # Поля для переводов названий
    name_ru = forms.CharField(max_length=100, label='Название (RU)', required=False)
    name_kk = forms.CharField(max_length=100, label='Название (KK)', required=False)
    name_en = forms.CharField(max_length=100, label='Название (EN)', required=False)
    
    # Поля для переводов описаний
    description_ru = forms.CharField(widget=SimpleTextEditorWidget(), label='Описание (RU)', required=False)
    description_kk = forms.CharField(widget=SimpleTextEditorWidget(), label='Описание (KK)', required=False)
    description_en = forms.CharField(widget=SimpleTextEditorWidget(), label='Описание (EN)', required=False)
    
    # Добавляем поле для множественной загрузки изображений
    multiple_hotel_images = MultipleFileField(
        required=False,
        label='Загрузить несколько изображений в галерею',
        help_text='Выберите несколько изображений для загрузки в галерею отеля (поддерживаются JPG, PNG, WEBP)'
    )
    
    class Meta:
        model = Hotel
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        # Извлекаем request из kwargs, если он передан
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Скрываем поле для пользователей группы Manager
        if self.request and hasattr(self.request, 'user') and self.request.user.groups.filter(name='Manager').exists() and not self.request.user.is_superuser:
            if 'multiple_hotel_images' in self.fields:
                self.fields['multiple_hotel_images'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Проверяем, что хотя бы одно из полей названий заполнено
        name_ru = cleaned_data.get('name_ru')
        name_kk = cleaned_data.get('name_kk')
        name_en = cleaned_data.get('name_en')
        
        if not any([name_ru, name_kk, name_en]):
            raise forms.ValidationError('Необходимо заполнить хотя бы одно из полей названий (RU, KK, EN)')
        
        return cleaned_data
                
    def clean_multiple_hotel_images(self):
        """
        Валидация множественных файлов
        """
        files = self.cleaned_data.get('multiple_hotel_images')
        if files:
            # Проверяем каждый файл
            for file in files:
                if file:
                    # Проверяем размер файла (максимум 5MB)
                    if file.size > 5 * 1024 * 1024:
                        raise forms.ValidationError(f'Файл {file.name} слишком большой. Максимальный размер 5MB.')
                    
                    # Проверяем тип файла
                    if not file.content_type.startswith('image/'):
                        raise forms.ValidationError(f'Файл {file.name} не является изображением.')
        
        return files

class HotelFeaturesForm(forms.ModelForm):
    # Поля для переводов названий
    name_ru = forms.CharField(max_length=35, label='Название (RU)', required=False)
    name_kk = forms.CharField(max_length=35, label='Название (KK)', required=False)
    name_en = forms.CharField(max_length=35, label='Название (EN)', required=False)
    
    class Meta:
        model = HotelFeatures
        fields = '__all__'
        widgets = {
            'icon': IconSelectWidget(choices=ICON_CHOICES)  # Используем кастомный виджет
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Базовое поле name делаем необязательным, чтобы скрытие не давало ошибку
        if 'name' in self.fields:
            self.fields['name'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if not any([
            cleaned_data.get('name_ru'),
            cleaned_data.get('name_kk'),
            cleaned_data.get('name_en')
        ]):
            raise forms.ValidationError('Заполните хотя бы одно поле названия (RU, KK, EN)')
        return cleaned_data


class RoomTypeFeaturesForm(forms.ModelForm):
    # Поля для переводов названий
    name_ru = forms.CharField(max_length=100, label='Название (RU)', required=False)
    name_kk = forms.CharField(max_length=100, label='Название (KK)', required=False)
    name_en = forms.CharField(max_length=100, label='Название (EN)', required=False)
    
    class Meta:
        model = RoomTypeFeatures
        fields = '__all__'
        widgets = {
            'icon': IconSelectWidget(choices=ICON_CHOICES)  # Используем кастомный виджет для поля icon
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Базовое поле name делаем необязательным, чтобы скрытие не давало ошибку
        if 'name' in self.fields:
            self.fields['name'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if not any([
            cleaned_data.get('name_ru'),
            cleaned_data.get('name_kk'),
            cleaned_data.get('name_en')
        ]):
            raise forms.ValidationError('Заполните хотя бы одно поле названия (RU, KK, EN)')
        return cleaned_data

class RoomTypeFeaturesDetailedForm(forms.ModelForm):
    text_ru = forms.CharField(max_length=100, label='Текст (RU)')
    text_kk = forms.CharField(max_length=100, label='Текст (KK)')
    text_en = forms.CharField(max_length=100, label='Текст (EN)')
    
    class Meta:
        model = RoomTypeFeaturesDetailed
        fields = '__all__'

class RoomTypeForm(forms.ModelForm):
    # Поля для переводов названий
    type_ru = forms.CharField(max_length=120, label='Тип (RU)', required=False)
    type_kk = forms.CharField(max_length=120, label='Тип (KK)', required=False)
    type_en = forms.CharField(max_length=120, label='Тип (EN)', required=False)
    
    # Поля для переводов описаний
    description_ru = forms.CharField(widget=SimpleTextEditorWidget(attrs={'rows': 15}), required=False, label='Описание (RU)')
    description_kk = forms.CharField(widget=SimpleTextEditorWidget(), required=False, label='Описание (KK)')
    description_en = forms.CharField(widget=SimpleTextEditorWidget(), required=False, label='Описание (EN)')
    
    class Meta:
        model = RoomType
        fields = '__all__'
        
    class Media:
        css = {
            'all': ('css/custom_admin.css', 'css/simple_editor.css'),  # Подключаем кастомный CSS и стили редактора
        }
        js = ('js/simple_editor.js',)

    def clean(self):
        cleaned_data = super().clean()
        if not any([
            cleaned_data.get('type_ru'),
            cleaned_data.get('type_kk'),
            cleaned_data.get('type_en')
        ]):
            raise forms.ValidationError('Заполните хотя бы одно поле типа (RU, KK, EN)')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Базовое поле type делаем необязательным, чтобы скрытие не давало ошибку
        if 'type' in self.fields:
            self.fields['type'].required = False

    
class PriceOnDateForm(forms.ModelForm):
    dynamic_pricing_input = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
        help_text="Введите цены по датам в формате JSON: {'YYYY-MM-DD': price}. Например: {'2025-05-15': 150.00}",
        label='Динамические цены'
    )

    class Meta:
        model = RoomType
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если есть данные в dynamic_pricing, преобразуем их в JSON-строку
        if self.instance and self.instance.dynamic_pricing:
            self.fields['dynamic_pricing_input'].initial = json.dumps(
                self.instance.dynamic_pricing, 
                ensure_ascii=False,  # Для корректного отображения кириллицы
                cls=DjangoJSONEncoder
            )
        # Скроем поле dynamic_pricing_input, так как будем управлять им через UI
        self.fields['dynamic_pricing_input'].widget = forms.HiddenInput()

    def clean_dynamic_pricing_input(self):
        data = self.cleaned_data.get('dynamic_pricing_input')
        if data:
            try:
                # Проверяем, что входные данные - валидный JSON
                pricing = json.loads(data)
                if not isinstance(pricing, dict):
                    raise ValidationError("Динамические цены должны быть словарем.")
                
                # Проверка формата дат и значений
                for date_str, price in pricing.items():
                    try:
                        datetime.strptime(date_str, "%Y-%m-%d")
                        if not isinstance(price, (int, float)) or price < 0:
                            raise ValidationError(f"Цена для {date_str} должна быть положительным числом.")
                    except ValueError:
                        raise ValidationError(f"Неверный формат даты: {date_str}. Используйте YYYY-MM-DD.")
                print(f"Cleaned dynamic pricing data: {pricing}")
                return pricing
            except json.JSONDecodeError:
                raise ValidationError("Неверный формат JSON.")
        return {}

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Явно присваиваем значение для dynamic_pricing из поля dynamic_pricing_input
        print(f"Saving form. dynamic_pricing_input in cleaned_data: {'dynamic_pricing_input' in self.cleaned_data}")
        if 'dynamic_pricing_input' in self.cleaned_data:
            pricing_data = self.cleaned_data['dynamic_pricing_input']
            print(f"Setting dynamic_pricing to: {pricing_data}")
            instance.dynamic_pricing = pricing_data
        
        if commit:
            instance.save()
        
        return instance



class RoomTypeGalleryForm(forms.ModelForm):
    """
    Кастомная форма для RoomTypeGallery с возможностью множественной загрузки
    """
    multiple_images = MultipleFileField(
        required=False,
        label='Загрузить несколько изображений',
        help_text='Выберите несколько изображений для загрузки в галерею типа номера (поддерживаются JPG, PNG, WEBP)'
    )
    
    class Meta:
        model = RoomTypeGallery
        fields = ['hotel', 'room_type', 'image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем стандартное поле image, если используется множественная загрузка
        if 'multiple_images' in self.fields and 'image' in self.fields:
            self.fields['image'].required = False
            # Добавляем подсказку для обычного поля image
            self.fields['image'].help_text = 'Загрузите одно изображение или используйте поле выше для нескольких'
            
    def clean_multiple_images(self):
        """
        Валидация множественных файлов
        """
        files = self.cleaned_data.get('multiple_images')
        if files:
            # Проверяем каждый файл
            for file in files:
                if file:
                    # Проверяем размер файла (максимум 5MB)
                    if file.size > 5 * 1024 * 1024:
                        raise forms.ValidationError(f'Файл {file.name} слишком большой. Максимальный размер 5MB.')
                    
                    # Проверяем тип файла
                    if not file.content_type.startswith('image/'):
                        raise forms.ValidationError(f'Файл {file.name} не является изображением.')
        
        return files

        
class HotelGallery_Tab(admin.TabularInline):
    model = HotelGallery
    extra = 0
    fields = ['thumbnail']
    readonly_fields = ['thumbnail', 'hgid']
    template = 'admin/hotel/hotel_gallery_inline.html'
    can_delete = True
    
    class Media:
        js = ('admin/js/hotel_gallery_multiple.js',)
        css = {
            'all': ('admin/css/hotel_gallery_multiple.css',)
        }

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            for form in formset.form.base_fields.values():
                if 'hgid' in formset.form.base_fields:
                    formset.form.base_fields['hgid'].widget = forms.HiddenInput()

        return formset
    
    def save_formset(self, request, form, formset, change):
        """
        Обработка множественной загрузки файлов
        """
        print(f"DEBUG: save_formset вызван для formset {formset}")
        print(f"DEBUG: save_formset - request.FILES: {list(request.FILES.keys())}")
        print(f"DEBUG: save_formset - request.POST: {list(request.POST.keys())}")
        
        instances = formset.save(commit=False)
        
        # Обработка множественных файлов из request.FILES
        if 'multiple_hotel_images' in request.FILES:
            # Получаем отель из основной формы
            hotel = form.instance
            
            # Получаем все файлы с именем multiple_hotel_images
            files = request.FILES.getlist('multiple_hotel_images')
            
            # Проверяем общее количество изображений (текущие + новые)
            current_images_count = HotelGallery.objects.filter(hotel=hotel).count()
            new_valid_files = [f for f in files if f and f.size > 0]
            total_after_upload = current_images_count + len(new_valid_files)
            
            if total_after_upload > 10:
                from django.contrib import messages
                messages.error(request, f'Превышено максимальное количество изображений для отеля. Максимум: 10, текущее количество: {current_images_count}, попытка загрузить: {len(new_valid_files)}')
            else:
                print(f"DEBUG: save_formset - Обработка {len(files)} файлов")  # Временно для отладки
                
                for file in files:
                    if file and file.size > 0:  # Проверяем что файл не пустой
                        try:
                            gallery_instance = HotelGallery(hotel=hotel, image=file)
                            gallery_instance.save()
                            print(f"DEBUG: save_formset - Сохранен файл {file.name}")  # Временно для отладки
                        except Exception as e:
                            print(f"DEBUG: save_formset - Ошибка сохранения файла {file.name}: {e}")  # Временно для отладки
                
                # Добавляем сообщение об успешном сохранении
                from django.contrib import messages
                total_files = len([f for f in files if f and f.size > 0])
                if total_files > 0:
                    messages.success(request, f'Успешно загружено {total_files} изображений в галерею отеля.')
        else:
            print("DEBUG: save_formset - Файлы multiple_hotel_images не найдены в request.FILES")
        
        # Сохраняем остальные instances
        for instance in instances:
            instance.save()
        formset.save_m2m()
    
    def save_model(self, request, obj, form, change):
        """
        Обработка множественной загрузки файлов при сохранении модели
        """
        # Отладочный вывод
        print(f"DEBUG: save_model вызван для объекта {obj}")
        print(f"DEBUG: request.FILES содержит: {list(request.FILES.keys())}")
        print(f"DEBUG: request.POST содержит: {list(request.POST.keys())}")
        
        # Сначала сохраняем модель
        super().save_model(request, obj, form, change)
        
        # Затем обрабатываем множественные файлы из cleaned_data формы
        if hasattr(form, 'cleaned_data') and 'multiple_hotel_images' in form.cleaned_data:
            files = form.cleaned_data['multiple_hotel_images']
            
            if files:
                # Проверяем общее количество изображений (текущие + новые)
                current_images_count = HotelGallery.objects.filter(hotel=obj).count()
                new_valid_files = [f for f in files if f and f.size > 0]
                total_after_upload = current_images_count + len(new_valid_files)
                
                if total_after_upload > 10:
                    from django.contrib import messages
                    messages.error(request, f'Превышено максимальное количество изображений для отеля. Максимум: 10, текущее количество: {current_images_count}, попытка загрузить: {len(new_valid_files)}')
                else:
                    print(f"DEBUG: save_model - Обработка {len(files)} файлов из cleaned_data")  # Временно для отладки
                    
                    for file in files:
                        if file and file.size > 0:  # Проверяем что файл не пустой
                            try:
                                gallery_instance = HotelGallery(hotel=obj, image=file)
                                gallery_instance.save()
                                print(f"DEBUG: save_model - Сохранен файл {file.name}")  # Временно для отладки
                            except Exception as e:
                                print(f"DEBUG: save_model - Ошибка сохранения файла {file.name}: {e}")  # Временно для отладки
                                
                    # Добавляем сообщение об успешном сохранении
                    from django.contrib import messages
                    total_files = len([f for f in files if f and f.size > 0])
                    if total_files > 0:
                        messages.success(request, f'Успешно загружено {total_files} изображений в галерею отеля.')
        
        # Дополнительно обрабатываем файлы из request.FILES (на случай если они не попали в cleaned_data)
        elif 'multiple_hotel_images' in request.FILES:
            files = request.FILES.getlist('multiple_hotel_images')
            
            # Проверяем общее количество изображений (текущие + новые)
            current_images_count = HotelGallery.objects.filter(hotel=obj).count()
            new_valid_files = [f for f in files if f and f.size > 0]
            total_after_upload = current_images_count + len(new_valid_files)
            
            if total_after_upload > 10:
                from django.contrib import messages
                messages.error(request, f'Превышено максимальное количество изображений для отеля. Максимум: 10, текущее количество: {current_images_count}, попытка загрузить: {len(new_valid_files)}')
            else:
                print(f"DEBUG: save_model - Обработка {len(files)} файлов из request.FILES")  # Временно для отладки
                
                for file in files:
                    if file and file.size > 0:  # Проверяем что файл не пустой
                        try:
                            gallery_instance = HotelGallery(hotel=obj, image=file)
                            gallery_instance.save()
                            print(f"DEBUG: save_model - Сохранен файл {file.name}")  # Временно для отладки
                            
                            # Добавляем сообщение об успешном сохранении
                            from django.contrib import messages
                            messages.success(request, f'Успешно загружено изображение {file.name} в галерею отеля.')
                        except Exception as e:
                            print(f"DEBUG: save_model - Ошибка сохранения файла {file.name}: {e}")  # Временно для отладки
        else:
            print("DEBUG: save_model - Файлы для загрузки не найдены")

class HotelFeatures_Tab(admin.StackedInline):
    model = HotelFeatures
    form = HotelFeaturesForm  # Подключаем кастомную форму с виджетом
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            for form in formset.form.base_fields.values():
                if 'hfid' in formset.form.base_fields:
                    formset.form.base_fields['hfid'].widget = forms.HiddenInput()
                # Скрываем базовое поле name для менеджеров
                if 'name' in formset.form.base_fields:
                    formset.form.base_fields['name'].widget = forms.HiddenInput()

        return formset

class HotelFAQs_Tab(admin.StackedInline):
    model = HotelFAQs
    exclude = ['question', 'answer']
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Скрываем технические поля
            for field in ['hfid']:
                if field in formset.form.base_fields:
                    formset.form.base_fields[field].widget = forms.HiddenInput()

        return formset

class HotelMealPlan_Tab(admin.StackedInline):
    model = HotelMealPlan
    extra = 0
    fields = ['price_per_day', 'age_min', 'age_max']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'hotel':
            if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
                kwargs['queryset'] = Hotel.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        
        class CustomFormSet(FormSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                
        return CustomFormSet

class Room_Tab(admin.StackedInline):
    model = Room
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room_type":
            parent_id = request.resolver_match.kwargs.get('object_id')  # Получаем ID текущего отеля
            if parent_id:
                kwargs["queryset"] = RoomType.objects.filter(hotel_id=parent_id)
            # Используем кастомный виджет для пользователей группы Manager
            if is_manager(request.user):
                kwargs["widget"] = RoomTypeSelectWidget()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Скрываем технические поля
            for field in ['rid']:
                if field in formset.form.base_fields:
                    formset.form.base_fields[field].widget = forms.HiddenInput()
            # Скрываем поле hotel
            if 'hotel' in formset.form.base_fields:
                formset.form.base_fields['hotel'].widget = forms.HiddenInput()

        return formset



class RoomTypeGalleryInline(admin.StackedInline):
    model = RoomTypeGallery
    form = RoomTypeGalleryForm
    extra = 0
    fields = ['thumbnail', 'image']
    readonly_fields = ['thumbnail']
    verbose_name = 'Изображение галереи'
    verbose_name_plural = 'Галерея типа номера'
    template = 'admin/hotel/roomtype_gallery_inline.html'
    
    class Media:
        js = ('admin/js/roomtype_gallery_multiple.js',)
        css = {
            'all': ('admin/css/roomtype_gallery_multiple.css',)
        }
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        # Для Manager'ов скрываем поля hotel и image (используем только multiple upload)
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            if 'hotel' in formset.form.base_fields:
                formset.form.base_fields['hotel'].widget = forms.HiddenInput()
            if 'image' in formset.form.base_fields:
                formset.form.base_fields['image'].widget = forms.HiddenInput()
        
        return formset
    
    def save_formset(self, request, form, formset, change):
        """
        Обработка множественной загрузки файлов
        """
        print(f"DEBUG: RoomTypeGalleryInline.save_formset ВЫЗВАН!")
        print(f"DEBUG: save_formset RoomTypeGallery вызван для formset {formset}")
        print(f"DEBUG: save_formset - formset.model: {formset.model}")
        print(f"DEBUG: save_formset - formset.model == RoomTypeGallery: {formset.model == RoomTypeGallery}")
        print(f"DEBUG: save_formset - request.FILES keys: {list(request.FILES.keys())}")
        print(f"DEBUG: save_formset - request.POST keys содержащие 'multiple': {[k for k in request.POST.keys() if 'multiple' in k]}")
        print(f"DEBUG: save_formset - 'multiple_roomtype_images' in request.FILES: {'multiple_roomtype_images' in request.FILES}")
        
        # Отладочная информация о всех файлах
        for key, file_list in request.FILES.lists():
            print(f"DEBUG: save_formset - FILES[{key}]: {len(file_list)} файлов")
            for i, file in enumerate(file_list):
                print(f"  Файл {i+1}: {file.name} ({file.size} bytes, {file.content_type})")
        
        instances = formset.save(commit=False)
        print(f"DEBUG: save_formset RoomTypeGallery - instances: {len(instances)}")
        
        # Проверяем, что это именно inline для RoomTypeGallery
        if formset.model == RoomTypeGallery and 'multiple_roomtype_images' in request.FILES:
            # Получаем отель и тип номера из основной формы
            room_type = form.instance
            hotel = room_type.hotel
            
            # Получаем все файлы с именем multiple_roomtype_images
            files = request.FILES.getlist('multiple_roomtype_images')
            
            print(f"DEBUG: save_formset RoomTypeGallery - Обработка {len(files)} файлов")
            
            for file in files:
                if file and file.size > 0:  # Проверяем что файл не пустой
                    try:
                        gallery_instance = RoomTypeGallery(
                            hotel=hotel,
                            room_type=room_type,
                            image=file
                        )
                        gallery_instance.save()
                        print(f"DEBUG: save_formset RoomTypeGallery - Сохранен файл {file.name}")
                    except ValidationError as e:
                        from django.contrib import messages
                        messages.error(request, f'Ошибка загрузки файла {file.name}: {str(e)}')
                        print(f"DEBUG: save_formset RoomTypeGallery - Ошибка валидации файла {file.name}: {e}")
                    except Exception as e:
                        from django.contrib import messages
                        messages.error(request, f'Ошибка сохранения файла {file.name}: {str(e)}')
                        print(f"DEBUG: save_formset RoomTypeGallery - Ошибка сохранения файла {file.name}: {e}")
            
            # Добавляем сообщение об успешном сохранении
            from django.contrib import messages
            total_files = len([f for f in files if f and f.size > 0])
            if total_files > 0:
                messages.success(request, f'Успешно загружено {total_files} изображений в галерею типа номера.')
        else:
            print("DEBUG: save_formset RoomTypeGallery - Файлы multiple_roomtype_images не найдены в request.FILES")
        
        # Сохраняем остальные instances
        for instance in instances:
            instance.save()
        formset.save_m2m()

class RoomTypeFeaturesInline(admin.StackedInline):
    model = RoomTypeFeatures
    form = RoomTypeFeaturesForm
    extra = 0
    verbose_name = 'Удобство типа номера'
    verbose_name_plural = 'Удобства типа номера'

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Скрываем технические поля
            for field in ['hfid']:
                if field in formset.form.base_fields:
                    formset.form.base_fields[field].widget = forms.HiddenInput()
            # Скрываем поле hotel
            if 'hotel' in formset.form.base_fields:
                formset.form.base_fields['hotel'].widget = forms.HiddenInput()
            # Скрываем базовое поле name для менеджеров
            if 'name' in formset.form.base_fields:
                formset.form.base_fields['name'].widget = forms.HiddenInput()

        return formset

class RoomTypeFeaturesDetailedInline(admin.StackedInline):
    model = RoomTypeFeaturesDetailed
    form = RoomTypeFeaturesDetailedForm
    extra = 0
    exclude = ['text']
    verbose_name = 'Текстовая удобство'
    verbose_name_plural = 'Текстовые удобства'

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Скрываем технические поля
            for field in ['hfid']:
                if field in formset.form.base_fields:
                    formset.form.base_fields[field].widget = forms.HiddenInput()
            # Скрываем поле hotel
            if 'hotel' in formset.form.base_fields:
                formset.form.base_fields['hotel'].widget = forms.HiddenInput()

        return formset

class RoomTypeCompleteAdmin(RussianModelAdminMixin, BaseExportAdmin):
    form = RoomTypeForm
    inlines = [
        RoomTypeGalleryInline, 
        RoomTypeFeaturesInline,
        RoomTypeFeaturesDetailedInline,
        Room_Tab,
    ]
    list_display = ['type_ru', 'hotel', 'price', 'number_of_beds', 'room_capacity', 'room_size', 'date']
    list_filter = ['hotel', 'price', 'number_of_beds', 'room_capacity']
    search_fields = ['type_ru', 'hotel__name_ru', 'price']
    search_help_text = 'Поиск по типу номера, отелю, цене'
    list_per_page = 100
    prepopulated_fields = {"slug": ("type", )}
    exclude = ['rtid', 'description']
    change_form_template = 'admin/hotel/roomtype_complete/change_form.html'
    add_form_template = 'admin/hotel/roomtype_complete/change_form.html'
    
    def save_formset(self, request, form, formset, change):
        """
        Автоматически заполняем поле hotel из главной формы RoomType
        и обрабатываем множественную загрузку файлов для галереи
        """
        print(f"DEBUG: RoomTypeCompleteAdmin.save_formset НАЧАЛО - formset: {formset}")
        print(f"DEBUG: RoomTypeCompleteAdmin.save_formset - formset.model: {formset.model}")
        print(f"DEBUG: RoomTypeCompleteAdmin.save_formset - request.FILES keys: {list(request.FILES.keys())}")
        
        instances = formset.save(commit=False)
        
        # Получаем отель из главной формы
        room_type_hotel = form.instance.hotel
        
        # Обновляем поле hotel для всех инлайн объектов
        for instance in instances:
            if hasattr(instance, 'hotel'):
                # Если отель не задан или пользователь Manager, устанавливаем отель из RoomType
                if not instance.hotel or (is_manager(request.user) and room_type_hotel):
                    instance.hotel = room_type_hotel
                # Устанавливаем room_type для связи
                if hasattr(instance, 'room_type'):
                    instance.room_type = form.instance
        
        # Сохраняем инстансы
        for instance in instances:
            instance.save()
        
        # Обрабатываем удаления
        for obj in formset.deleted_objects:
            obj.delete()
        
        formset.save_m2m()
        
        # Резервная обработка файлов для галереи, если inline save_formset не сработал
        print(f"DEBUG: RoomTypeCompleteAdmin.save_formset - formset.model: {formset.model}")
        print(f"DEBUG: RoomTypeCompleteAdmin.save_formset - request.FILES keys: {list(request.FILES.keys())}")
        
        # Проверяем, обрабатывается ли это RoomTypeGallery и есть ли файлы
        if formset.model == RoomTypeGallery and 'multiple_roomtype_images' in request.FILES:
            print(f"DEBUG: RoomTypeCompleteAdmin.save_formset - Начинаем резервную обработку файлов галереи")
            
            # Получаем все файлы с именем multiple_roomtype_images
            files = request.FILES.getlist('multiple_roomtype_images')
            print(f"DEBUG: RoomTypeCompleteAdmin.save_formset - Резервная обработка {len(files)} файлов")
            
            # Получаем отель и тип номера из основной формы
            room_type = form.instance
            hotel = room_type.hotel
            
            for file in files:
                if file and file.size > 0:  # Проверяем что файл не пустой
                    try:
                        # Проверяем, что изображение еще не существует
                        existing = RoomTypeGallery.objects.filter(
                            room_type=room_type,
                            image__icontains=file.name
                        ).exists()
                        
                        if not existing:
                            gallery_instance = RoomTypeGallery(
                                hotel=hotel,
                                room_type=room_type,
                                image=file
                            )
                            gallery_instance.save()
                            print(f"DEBUG: RoomTypeCompleteAdmin.save_formset - Резервно сохранен файл {file.name}")
                        else:
                            print(f"DEBUG: RoomTypeCompleteAdmin.save_formset - Файл {file.name} уже существует, пропускаем")
                    except Exception as e:
                        print(f"DEBUG: RoomTypeCompleteAdmin.save_formset - Ошибка резервного сохранения файла {file.name}: {e}")
            
            # Добавляем сообщение об успешном сохранении
            from django.contrib import messages
            total_files = len([f for f in files if f and f.size > 0])
            if total_files > 0:
                messages.success(request, f'Успешно загружено {total_files} изображений в галерею типа номера (резервная обработка).')
        
        # Отладочная информация
        if 'multiple_roomtype_images' in request.FILES:
            files = request.FILES.getlist('multiple_roomtype_images')
            print(f"DEBUG: RoomTypeCompleteAdmin.save_formset - Обнаружено {len(files)} файлов")
            for i, file in enumerate(files):
                print(f"  Файл {i+1}: {file.name} ({file.size} bytes, {file.content_type})")
        else:
            print(f"DEBUG: RoomTypeCompleteAdmin.save_formset - Файлы multiple_roomtype_images НЕ найдены")
    
    def get_search_fields(self, request):
        if is_manager(request.user):
            self.search_help_text = 'Поиск по типу номера, цене'
            return ['type', 'price']
        return self.search_fields

    def get_list_filter(self, request):
        if is_manager(request.user):
            return ['price', 'number_of_beds', 'room_capacity']
        return self.list_filter

    def get_list_display(self, request):
        if is_manager(request.user):
            return ['type', 'price', 'number_of_beds', 'room_capacity', 'room_size']
        return self.list_display

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if is_manager(request.user):
            return queryset.filter(hotel__user=request.user)
        return queryset

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        if is_manager(request.user):
            # Ограничиваем выбор отелей только теми, которые принадлежат пользователю
            if 'hotel' in form.base_fields:
                form.base_fields['hotel'].queryset = Hotel.objects.filter(user=request.user)
            # Скрываем технические поля
            for field in ['rtid', 'slug', 'dynamic_pricing', 'description']:
                if field in form.base_fields:
                    form.base_fields[field].widget = forms.HiddenInput()
            # Скрываем базовое поле типа для менеджеров (type)
            if 'type' in form.base_fields:
                form.base_fields['type'].widget = forms.HiddenInput()
        
        return form

    def save_model(self, request, obj, form, change):
        # Если пользователь менеджер и не указан отель, устанавливаем один из его отелей
        if is_manager(request.user) and not obj.hotel:
            user_hotels = Hotel.objects.filter(user=request.user)
            if user_hotels.exists():
                obj.hotel = user_hotels.first()
        
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Manager').exists():
            if obj is None:
                return True
            return obj.hotel.user == request.user
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Manager').exists():
            if obj is None:
                return True
            return obj.hotel.user == request.user
        return False

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='Manager').exists()

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Manager').exists():
            if obj is None:
                return True
            # Проверяем, принадлежит ли тип номера пользователю
            if obj.hotel.user != request.user:
                return False
            # Проверяем, есть ли связанные записи бронирования
            from hotel.models import Booking
            if Booking.objects.filter(room_type=obj).exists():
                return False
            return True
        return False
    
    def delete_view(self, request, object_id, extra_context=None):
        """
        Переопределяем delete_view для отображения сообщения о необходимости связаться с поддержкой
        """
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            try:
                obj = self.get_object(request, object_id)
                if obj:
                    from hotel.models import Booking
                    if Booking.objects.filter(room_type=obj).exists():
                        from django.contrib import messages
                        messages.error(request, 
                            f'Невозможно удалить тип номера "{obj.type}" так как с ним связаны записи бронирования. '
                            f'Для удаления необходимо связаться с поддержкой сайта support@ekol.kz')
                        from django.shortcuts import redirect
                        return redirect('admin:hotel_roomtypecomplete_changelist')
            except Exception:
                pass
        return super().delete_view(request, object_id, extra_context)
    
    def get_actions(self, request):
        """
        Переопределяем действия для группы Manager
        """
        actions = super().get_actions(request)
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Удаляем стандартное действие delete_selected
            if 'delete_selected' in actions:
                del actions['delete_selected']
            # Добавляем кастомное действие
            actions['delete_roomtypes_with_check'] = (
                delete_roomtypes_with_check,
                'delete_roomtypes_with_check',
                'Удалить выбранные типы номеров'
            )
        return actions

class HotelAdmin(RussianModelAdminMixin, BaseExportAdmin):
    form = HotelAdminForm
    inlines = [
        HotelGallery_Tab, HotelFeatures_Tab, HotelMealPlan_Tab, HotelFAQs_Tab
    ]
    list_filter = ['featured', 'status']
    list_editable = ['status']
    list_display = ['thumbnail', 'name_ru', 'user', 'status', 'featured', 'views']
    list_per_page = 100
    prepopulated_fields = {"slug": ("name_en", )}
    exclude = ['description']
    search_fields = ['name_ru', 'user__username', 'status']
    search_help_text = 'Поиск по Названию [RU], Пользователю, Статусу'
    
    def response_change(self, request, obj):
        """
        Обработка ответа после изменения объекта
        """
        # Сначала получаем стандартный response
        response = super().response_change(request, obj)
        
        # Проверяем, есть ли файлы для загрузки
        if 'multiple_hotel_images' in request.FILES:
            files = request.FILES.getlist('multiple_hotel_images')
            print(f"DEBUG: response_change - Найдено {len(files)} файлов для загрузки")
            
            # Проверяем общее количество изображений (текущие + новые)
            current_images_count = HotelGallery.objects.filter(hotel=obj).count()
            new_valid_files = [f for f in files if f and f.size > 0]
            total_after_upload = current_images_count + len(new_valid_files)
            
            if total_after_upload > 10:
                from django.contrib import messages
                messages.error(request, f'Превышено максимальное количество изображений для отеля. Максимум: 10, текущее количество: {current_images_count}, попытка загрузить: {len(new_valid_files)}')
            else:
                for file in files:
                    if file and file.size > 0:
                        try:
                            gallery_instance = HotelGallery(hotel=obj, image=file)
                            gallery_instance.save()
                            print(f"DEBUG: response_change - Сохранен файл {file.name}")
                        except Exception as e:
                            print(f"DEBUG: response_change - Ошибка сохранения файла {file.name}: {e}")
                
                # Добавляем сообщение об успешном сохранении
                from django.contrib import messages
                total_files = len([f for f in files if f and f.size > 0])
                if total_files > 0:
                    messages.success(request, f'Успешно загружено {total_files} изображений в галерею отеля.')
        
        return response
    
    def response_add(self, request, obj, post_url_continue=None):
        """
        Обработка ответа после добавления нового объекта
        """
        # Сначала получаем стандартный response
        response = super().response_add(request, obj, post_url_continue)
        
        print(f"DEBUG: response_add вызван для объекта {obj}")
        print(f"DEBUG: response_add - request.FILES: {list(request.FILES.keys())}")
        
        # Проверяем, есть ли файлы для загрузки
        if 'multiple_hotel_images' in request.FILES:
            files = request.FILES.getlist('multiple_hotel_images')
            print(f"DEBUG: response_add - Найдено {len(files)} файлов для загрузки")
            
            # Проверяем общее количество изображений (текущие + новые)
            current_images_count = HotelGallery.objects.filter(hotel=obj).count()
            new_valid_files = [f for f in files if f and f.size > 0]
            total_after_upload = current_images_count + len(new_valid_files)
            
            if total_after_upload > 10:
                from django.contrib import messages
                messages.error(request, f'Превышено максимальное количество изображений для отеля. Максимум: 10, текущее количество: {current_images_count}, попытка загрузить: {len(new_valid_files)}')
            else:
                for file in files:
                    if file and file.size > 0:
                        try:
                            gallery_instance = HotelGallery(hotel=obj, image=file)
                            gallery_instance.save()
                            print(f"DEBUG: response_add - Сохранен файл {file.name}")
                        except Exception as e:
                            print(f"DEBUG: response_add - Ошибка сохранения файла {file.name}: {e}")
                
                # Добавляем сообщение об успешном сохранении
                from django.contrib import messages
                total_files = len([f for f in files if f and f.size > 0])
                if total_files > 0:
                    messages.success(request, f'Успешно загружено {total_files} изображений в галерею отеля.')
        else:
            print("DEBUG: response_add - Файлы multiple_hotel_images не найдены")
        
        return response
    
    def get_search_fields(self, request):
        if is_manager(request.user):
            self.search_help_text = 'Поиск по Названию [RU]'
            return ['name_ru']
        return self.search_fields

    def get_list_filter(self, request):
        if is_manager(request.user):
            return []
        return self.list_filter

    def get_list_display(self, request):
        if is_manager(request.user):
            return ['thumbnail', 'name_ru']
        return super().get_list_display(request)

    def get_form(self, request, obj=None, **kwargs):
        # Для Manager'ов используем специальную форму с исключенными полями
        if is_manager(request.user):
            class ManagerHotelForm(HotelAdminForm):
                class Meta:
                    model = Hotel
                    # Исключаем технические поля для Manager'ов
                    exclude = ['user', 'hid', 'views', 'featured', 'slug', 'name', 'description', 'status']
                    widgets = {
                        'check_in_time': forms.TimeInput(attrs={'type': 'time'}),
                        'check_out_time': forms.TimeInput(attrs={'type': 'time'}),
                        'start_date': DDMMDateInput(),
                        'end_date': DDMMDateInput(),
                    }
                
                def __init__(self, *args, **kwargs):
                    self.request = kwargs.pop('request', None)
                    super().__init__(*args, **kwargs)
                    
                    # Скрываем поле множественной загрузки для менеджеров
                    if 'multiple_hotel_images' in self.fields:
                        self.fields['multiple_hotel_images'].widget = forms.HiddenInput()
                        self.fields['multiple_hotel_images'].required = False
                    
                    # Добавляем подсказку к полю названия
                    if 'name_ru' in self.fields:
                        self.fields['name_ru'].help_text = 'Заполните хотя бы одно из полей названий'
            
            # Создаем кастомную форму, которая будет принимать request в kwargs
            class RequestAwareManagerForm(ManagerHotelForm):
                def __init__(self, *args, **kwargs):
                    kwargs['request'] = request  # Передаем request в kwargs
                    super().__init__(*args, **kwargs)
            
            return RequestAwareManagerForm
        
        else:
            # Для суперпользователей используем стандартную форму
            form_class = super().get_form(request, obj, **kwargs)
            
            class RequestAwareForm(form_class):
                def __init__(self, *args, **kwargs):
                    kwargs['request'] = request  # Передаем request в kwargs
                    super().__init__(*args, **kwargs)
            
            return RequestAwareForm

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if is_manager(request.user):
            return queryset.filter(user=request.user)
        return queryset

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Назначаем маску DD.MM для сезонных полей
        if db_field.name in ('start_date', 'end_date'):
            kwargs['widget'] = DDMMDateInput()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_prepopulated_fields(self, request, obj=None):
        """
        Переопределяем prepopulated_fields для менеджеров
        """
        if is_manager(request.user):
            return {}  # Для менеджеров не используем prepopulated_fields
        return self.prepopulated_fields

    def save_model(self, request, obj, form, change):
        # Для новых объектов устанавливаем пользователя
        if not change:
            obj.user = request.user
        
        # Для Manager'ов устанавливаем значения по умолчанию для скрытых полей
        if is_manager(request.user):
            # Обязательно устанавливаем пользователя
            obj.user = request.user
            
            # Устанавливаем статус по умолчанию если не установлен
            if not obj.status:
                obj.status = 'In Review'  # На проверке для Manager'ов
            
            # Устанавливаем featured в False если не установлен
            if obj.featured is None:
                obj.featured = False
            
            # Устанавливаем views в 0 если не установлен
            if obj.views is None:
                obj.views = 0
            
            # Генерируем hid если не установлен
            if not obj.hid:
                import shortuuid
                obj.hid = shortuuid.uuid()[:10]
        
        super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Manager').exists():
            if obj is None:
                return True
            # Проверяем, принадлежит ли отель пользователю
            if obj.user != request.user:
                return False
            # Проверяем, есть ли связанные записи бронирования
            from hotel.models import Booking
            if Booking.objects.filter(hotel=obj).exists():
                return False
            return True
        return False
    
    def delete_view(self, request, object_id, extra_context=None):
        """
        Переопределяем delete_view для отображения сообщения о необходимости связаться с поддержкой
        """
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            try:
                obj = self.get_object(request, object_id)
                if obj:
                    from hotel.models import Booking
                    if Booking.objects.filter(hotel=obj).exists():
                        from django.contrib import messages
                        messages.error(request, 
                            f'Невозможно удалить отель "{obj.name}" так как с ним связаны записи бронирования. '
                            f'Для удаления необходимо связаться с поддержкой сайта support@ekol.kz')
                        from django.shortcuts import redirect
                        return redirect('admin:hotel_hotel_changelist')
            except Exception:
                pass
        return super().delete_view(request, object_id, extra_context)
    
    def get_actions(self, request):
        """
        Переопределяем действия для группы Manager
        """
        actions = super().get_actions(request)
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Удаляем стандартное действие delete_selected
            if 'delete_selected' in actions:
                del actions['delete_selected']
            # Добавляем кастомное действие
            actions['delete_hotels_with_check'] = (
                delete_hotels_with_check,
                'delete_hotels_with_check',
                'Удалить выбранные отели'
            )
        return actions

class RoomAdmin(RussianModelAdminMixin, BaseExportAdmin):
    list_display = ['hotel', 'get_room_type', 'room_number', 'get_price', 'get_number_of_beds', 'get_room_capacity', 'is_available']
    list_per_page = 100
    list_filter = ['is_available']
    search_fields = ['hotel__name_ru', 'room_type__type', 'room_number', 'room_type__price']
    search_help_text = 'Поиск по Отелю, Типу номера, Номеру комнаты, Цене'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Если пользователь является менеджером, ограничиваем выбор отелей и типов комнат
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            if db_field.name == "hotel":
                # Показываем только отели, созданные пользователем
                kwargs["queryset"] = Hotel.objects.filter(user=request.user)
            elif db_field.name == "room_type":
                # Показываем только типы комнат, относящиеся к отелям пользователя
                kwargs["queryset"] = RoomType.objects.filter(hotel__user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_room_type(self, obj):
        """Отображает только название типа номера"""
        if obj.room_type:
            return obj.room_type.type
        return None
    
    get_room_type.short_description = 'Тип номера'
    get_room_type.admin_order_field = 'room_type__type'

    def get_price(self, obj):
        if obj.room_type:
            return obj.room_type.price
        return None
    
    get_price.short_description = 'Цена'
    get_price.admin_order_field = 'room_type__price'

    def get_number_of_beds(self, obj):
        """Отображает количество кроватей с русским названием"""
        if obj.room_type:
            return obj.room_type.number_of_beds
        return None
    
    get_number_of_beds.short_description = 'Количество кроватей'
    get_number_of_beds.admin_order_field = 'room_type__number_of_beds'

    def get_room_capacity(self, obj):
        """Отображает вместимость с русским названием"""
        if obj.room_type:
            return obj.room_type.room_capacity
        return None
    
    get_room_capacity.short_description = 'Вместимость'
    get_room_capacity.admin_order_field = 'room_type__room_capacity'

    def get_list_filter(self, request):
        if is_manager(request.user):
            return []
        return self.list_filter
    def get_search_fields(self, request):
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            self.search_help_text = 'Поиск по Типу номера, Номеру комнаты'
            return ['room_type__type', 'room_number']
        return self.search_fields

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Если пользователь принадлежит группе Manager и не является суперпользователем
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Фильтруем только те комнаты, которые связаны с отелями, созданным пользователем
            queryset = queryset.filter(hotel__user=request.user)
        return queryset

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if is_manager(request.user):
            form.base_fields.pop('user', None)
            for field in ['rid']:
                if field in form.base_fields:
                    form.base_fields[field].widget = forms.HiddenInput()
        return form

class HotelFilter(admin.SimpleListFilter):
    title = 'Отель'
    parameter_name = 'hotel'

    def lookups(self, request, model_admin):
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            hotels = Hotel.objects.filter(user=request.user)
        else:
            hotels = Hotel.objects.all()
        return [(hotel.id, hotel.name) for hotel in hotels]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(hotel_id=self.value())
        return queryset

class RoomTypeFilter(admin.SimpleListFilter):
    title = 'Тип номера'
    parameter_name = 'room_type'

    def lookups(self, request, model_admin):
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            room_types = RoomType.objects.filter(hotel__user=request.user)
        else:
            room_types = RoomType.objects.all()
        return [(rt.id, rt.type) for rt in room_types]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(room_type_id=self.value())
        return queryset


class CheckInDateFilter(admin.SimpleListFilter):
    title = _('Check-In Date')
    parameter_name = 'check_in_date'
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        return (),

    def choices(self, changelist):
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice

    def queryset(self, request, queryset):
        date_value = request.GET.get(self.parameter_name)
        if date_value:
            try:
                filter_date = datetime.strptime(date_value, '%Y-%m-%d').date()
                return queryset.filter(check_in_date=filter_date).distinct()
            except ValueError:
                return queryset
        return queryset



class BookingAdmin(RussianModelAdminMixin, BaseExportAdmin):
    # inlines = [ActivityLog_Tab, StaffOnDuty_Tab]
    list_filter = [HotelFilter, RoomTypeFilter, 'is_active', 'checked_in', 'checked_out', CheckInDateFilter, 'payment_status']
    list_display = ['booking_id', 'user', 'hotel', 'get_room_type', 'rooms', 'total', 'prepayment', 'payment_for_hotel', 'payment_status', 'total_days', 'num_adults', 'num_children', 'check_in_date', 'check_out_date', 'date']
    search_fields = ['booking_id', 'robokassa_inv_id']
    search_help_text = 'Поиск по ID бронирования, ID инвойса Robokassa, Сумме'
    list_per_page = 100

    def get_room_type(self, obj):
        """Отображает только название типа номера"""
        if obj.room_type:
            return obj.room_type.type
        return None
    
    get_room_type.short_description = 'Тип номера'
    get_room_type.admin_order_field = 'room_type__type'

    def get_search_fields(self, request):
        if is_manager(request.user):
            self.search_help_text = 'Поиск по ID бронирования, ID инвойса Robokassa'
            return ['booking_id', 'robokassa_inv_id']
        return self.search_fields

    def get_list_display(self, request):
        if is_manager(request.user):
            return ['booking_id', 'hotel', 'get_room_type', 'rooms', 'total', 'payment_for_hotel', 'total_days', 'num_adults', 'num_children', 'check_in_date', 'check_out_date', 'date']
        return self.list_display

    def get_list_filter(self, request):
        if is_manager(request.user):
            return [HotelFilter, RoomTypeFilter, 'checked_in', 'checked_out']
        return self.list_filter

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Если пользователь принадлежит группе Manager и не является суперпользователем
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Фильтруем только те записи, которые связаны с отелями пользователя и имеют статус "paid"
            queryset = queryset.filter(hotel__user=request.user, payment_status='paid')
        return queryset
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if is_manager(request.user) and not request.user.is_superuser:
            # Удаляем поля из формы для менеджеров
            if 'selection_data' in form.base_fields:
                del form.base_fields['selection_data']
            if 'checked_in_tracker' in form.base_fields:
                del form.base_fields['checked_in_tracker']
            if 'checked_out_tracker' in form.base_fields:
                del form.base_fields['checked_out_tracker']
            if 'expires_at' in form.base_fields:
                del form.base_fields['expires_at']
            if 'is_active' in form.base_fields:
                del form.base_fields['is_active']
            # Скрываем legal_agreements от менеджеров согласно требованиям
            if 'legal_agreements' in form.base_fields:
                del form.base_fields['legal_agreements']
            # Делаем поля prepayment и payment_for_hotel только для чтения
            if 'prepayment' in form.base_fields:
                form.base_fields['prepayment'].widget.attrs['readonly'] = True
            if 'payment_for_hotel' in form.base_fields:
                form.base_fields['payment_for_hotel'].widget.attrs['readonly'] = True
        return form

class RoomServicesAdmin(RussianModelAdminMixin, BaseExportAdmin):
    list_display = ['booking', 'room', 'date', 'price', 'service_type']
    list_per_page = 100

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ограничиваем видимость записей для менеджеров
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(booking__hotel__user=request.user)
        return queryset

class CouponUsers_Tab(admin.TabularInline):
    model = CouponUsers

class CouponAdmin(RussianModelAdminMixin, BaseExportAdmin):
    inlines = [CouponUsers_Tab]
    list_editable = ['valid_from', 'valid_to', 'active', 'type']
    list_display = ['code', 'discount', 'type', 'redemption', 'valid_from', 'valid_to', 'active', 'date']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ограничиваем видимость записей для менеджеров
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(hotel__user=request.user)
        return queryset

class NotificationAdmin(RussianModelAdminMixin, BaseExportAdmin):
    list_editable = ['seen', 'type']
    list_display = ['user', 'booking', 'type', 'seen', 'date']
    
    def has_module_permission(self, request):
        # Разрешаем доступ только суперпользователям
        return request.user.is_superuser
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ограничиваем видимость записей для менеджеров
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(booking__hotel__user=request.user)
        return queryset


class BookmarkAdmin(RussianModelAdminMixin, BaseExportAdmin):
    list_display = ['user', 'hotel']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ограничиваем видимость записей для менеджеров
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(hotel__user=request.user)
        return queryset


class ReviewAdmin(RussianModelAdminMixin, admin.ModelAdmin):
    list_editable = ['active']
    list_display = ['user', 'hotel', 'review', 'reply', 'rating', 'active']
    search_fields = ['user__username', 'hotel__name_ru']
    search_help_text = 'Поиск по Пользователю, Отелю'
    list_filter = ['rating', 'active']

    def has_module_permission(self, request):
        # Разрешаем доступ только суперпользователям
        return request.user.is_superuser

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ограничиваем видимость записей для менеджеров
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(hotel__user=request.user)
        return queryset

class PriceOnDateAdmin(RussianModelAdminMixin, BaseExportAdmin):
    form = PriceOnDateForm
    list_display = ['type', 'hotel']
    list_filter = [HotelFilter]
    search_fields = ['type', 'hotel__name_ru']
    search_help_text = 'Поиск по Типу номера, Отелю'
    exclude = ['dynamic_pricing', 'number_of_beds', 'room_capacity', 'room_size', 'rtid', 'description', 'description_ru', 'description_kk', 'description_en']
    prepopulated_fields = {"slug": ("type", )}
    change_form_template = 'admin/hotel/roomtype/change_form.html'  # Кастомный шаблон для PriceOnDate
    
    # def _setup_russian_verbose_names(self):
    #     """Переопределяем для специального названия 'Цены по датам'"""
    #     self.model._meta.verbose_name = 'Цена по датам'
    #     self.model._meta.verbose_name_plural = 'Цены по датам'

    def has_module_permission(self, request):
        # Разрешаем доступ суперпользователям и менеджерам для модели PriceOnDate
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Manager').exists():
            return True
        return False
 
    def has_view_permission(self, request, obj=None):
        # Разрешаем просмотр суперпользователям и менеджерам
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Manager').exists():
            if obj is None:
                return True
            return obj.hotel.user == request.user
        return False
 
    def has_change_permission(self, request, obj=None):
        # Разрешаем изменение суперпользователям и менеджерам только своих записей
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Manager').exists():
            if obj is None:
                return True
            return obj.hotel.user == request.user
        return False

    def has_add_permission(self, request):
        # Запрещаем добавление записей для пользователей группы Manager
        return False

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление записей в PriceOnDateAdmin
        return False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(hotel__user=request.user)
        return queryset
 
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if is_manager(request.user):
            # Hide fields for Managers
            for field in ['slug', 'rtid', 'hotel', 'type', 'price']:
                if field in form.base_fields:
                    form.base_fields[field].widget = forms.HiddenInput()
        return form
 
    def save_model(self, request, obj, form, change):
        print(f"Save model called. POST data: {request.POST}")
        if 'dynamic_pricing_input' in request.POST:
            try:
                dynamic_pricing_input = request.POST.getlist('dynamic_pricing_input')[0]
                print(f"Raw dynamic_pricing_input from POST: {dynamic_pricing_input}")
                if dynamic_pricing_input and dynamic_pricing_input.strip() != '{}':
                    pricing_data = json.loads(dynamic_pricing_input)
                    print(f"Loaded dynamic pricing from POST: {pricing_data}")
                    obj.dynamic_pricing = pricing_data
                else:
                    print("Empty or blank dynamic_pricing_input, not updating.")
            except (json.JSONDecodeError, IndexError) as e:
                print(f"Error processing dynamic pricing: {e}")
             
        if hasattr(form, 'cleaned_data') and 'dynamic_pricing_input' in form.cleaned_data:
            pricing_data = form.cleaned_data['dynamic_pricing_input']
            print(f"Setting dynamic_pricing from cleaned_data: {pricing_data}")
            obj.dynamic_pricing = pricing_data
         
        super().save_model(request, obj, form, change)
        print(f"After save: obj.dynamic_pricing = {obj.dynamic_pricing}")
     
    def response_change(self, request, obj):
        if obj.dynamic_pricing:
            pricing_count = len(obj.dynamic_pricing) if isinstance(obj.dynamic_pricing, dict) else 0
            self.message_user(request, f"Динамические цены успешно сохранены. {pricing_count} дней с ценами.")
        return super().response_change(request, obj)

@receiver(post_migrate)
def add_permissions_to_manager_group(sender, **kwargs):
    """Добавляет права на изменение отелей группе Manager"""
    try:
        manager_group, created = Group.objects.get_or_create(name='Manager')
        
        # Список моделей для которых нужно добавить разрешения
        models_to_add = ['Hotel', 'Room', 'HotelGallery', 'HotelFeatures', 
                        'HotelFAQs', 'RoomType', 'RoomTypeDescription', 
                        'RoomTypeGallery', 'RoomTypeFeatures', 'RoomTypeFeaturesDetailed']
        
        for model_name in models_to_add:
            try:
                content_type = ContentType.objects.get(app_label='hotel', model=model_name.lower())
                permissions = Permission.objects.filter(content_type=content_type)
                manager_group.permissions.add(*permissions)
            except ContentType.DoesNotExist:
                pass  # Модель может не существовать в некоторых случаях
                
    except Exception as e:
        print(f"Ошибка при создании группы Manager: {e}")

class CustomAdminSite(admin.AdminSite):
    site_header = "Админ панель Alakol"
    site_title = "Alakol Admin"
    index_title = "Добро пожаловать в административную панель Alakol"
    
    # Словарь переводов для моделей
    MODEL_TRANSLATIONS = {
        'Hotel': 'Отели',
        'Room': 'Номера',
        'RoomType': 'Типы номеров',
        'RoomTypeComplete': 'Типы номеров',
        'Booking': 'Бронирования',
        'RoomServices': 'Услуги номеров',
        'Coupon': 'Купоны',
        'Notification': 'Уведомления',
        'Bookmark': 'Закладки',
        'Review': 'Отзывы',
        'User': 'Пользователи',
        'Profile': 'Профили',
        'Group': 'Группы',
        'Permission': 'Разрешения',
        'RoomUnavailability': 'Недоступность номеров',
        'HotelGallery': 'Галерея отелей',
        'HotelFeatures': 'Удобства отелей',
        'HotelFAQs': 'FAQ отелей',
        'HotelMealPlan': 'Планы питания отелей',
        'RoomTypeDescription': 'Описания типов номеров',
        'RoomTypeGallery': 'Галерея типов номеров',
        'RoomTypeFeatures': 'Удобства типов номеров',
        'RoomTypeFeaturesDetailed': 'Текстовые удобства типов номеров',
    }
    
    # Словарь переводов для приложений
    APP_TRANSLATIONS = {
        'hotel': 'Отель',
        'userauths': 'Пользователи',
        'booking': 'Бронирования',
        'auth': 'Аутентификация',
        'admin': 'Администрирование',
    }
    
    def each_context(self, request):
        """
        Переопределяем контекст для принудительного использования русского языка
        """
        from django.utils import translation
        
        # Принудительно активируем русский язык
        translation.activate('ru')
        request.LANGUAGE_CODE = 'ru'
        
        context = super().each_context(request)
        
        # Добавляем дополнительные русские переводы в контекст
        context.update({
            'LANGUAGE_CODE': 'ru',
            'ADMIN_FORCE_RUSSIAN': True,
            'site_header': self.site_header,
            'site_title': self.site_title,
            'index_title': self.index_title,
            'model_translations': self.MODEL_TRANSLATIONS,
            'app_translations': self.APP_TRANSLATIONS,
        })
        
        return context
    
    def get_app_list(self, request, app_label=None):
        """
        Переопределяем список приложений и моделей с русскими названиями
        """
        if app_label:
            app_list = super().get_app_list(request, app_label)
        else:
            app_list = super().get_app_list(request)
        
        for app in app_list:
            # Переводим название приложения
            if app['app_label'] in self.APP_TRANSLATIONS:
                app['name'] = self.APP_TRANSLATIONS[app['app_label']]
            
            # Переводим названия моделей
            for model in app['models']:
                model_name = model['object_name']
                if model_name in self.MODEL_TRANSLATIONS:
                    model['name'] = self.MODEL_TRANSLATIONS[model_name]
                
                # Специальные случаи
                if model_name == 'RoomType' and model['admin_url'] == '/admin/hotel/roomtype/':
                    model['name'] = 'Цены по датам'
        
        return app_list

# Instantiate the custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register models with the custom admin site in the required order
custom_admin_site.register(Hotel, HotelAdmin)

# Регистрируем новый полный админ для RoomType отдельно (используем прокси модель из models.py)
from .models import RoomTypeComplete
custom_admin_site.register(RoomTypeComplete, RoomTypeCompleteAdmin)

# custom_admin_site.register(Room, RoomAdmin)
custom_admin_site.register(RoomType, PriceOnDateAdmin)
custom_admin_site.register(Booking, BookingAdmin)
custom_admin_site.register(RoomServices, RoomServicesAdmin)
custom_admin_site.register(Bookmark, BookmarkAdmin)
custom_admin_site.register(Coupon, CouponAdmin)
custom_admin_site.register(Review, ReviewAdmin)
custom_admin_site.register(Notification, NotificationAdmin)

# Register Django auth models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import GroupAdmin, UserAdmin
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(Permission)