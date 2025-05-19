from django import forms
from django.contrib import admin
from hotel.models import  ICON_CHOICES,Hotel, Room, Booking, RoomServices, HotelGallery, RoomTypeGallery,RoomTypeFeatures, HotelFeatures, HotelFAQs, RoomType, RoomTypeDescription, Coupon, CouponUsers, Notification, Bookmark, Review, RoomTypeFeaturesDetailed
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from django.utils.html import mark_safe

from modeltranslation.admin import TranslationAdmin
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .widgets import IconSelectWidget

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


# Проверка принадлежности пользователя к группе Manager
def is_manager(user):
    return user.groups.filter(name='Manager').exists() and not user.is_superuser

class BaseImportExportAdmin(ImportExportModelAdmin):
    formats = [base_formats.CSV, base_formats.XLS, base_formats.XLSX]

class HotelAdminForm(forms.ModelForm):
    description_ru = forms.CharField(widget=CKEditorUploadingWidget())
    description_kk = forms.CharField(widget=CKEditorUploadingWidget())
    description_en = forms.CharField(widget=CKEditorUploadingWidget())
    
    class Meta:
        model = Hotel
        fields = '__all__'

class HotelFeaturesForm(forms.ModelForm):
    class Meta:
        model = HotelFeatures
        fields = '__all__'
        widgets = {
            'icon': IconSelectWidget(choices=ICON_CHOICES)  # Используем кастомный виджет
        }


class RoomTypeFeaturesForm(forms.ModelForm):
    class Meta:
        model = RoomTypeFeatures
        fields = '__all__'
        widgets = {
            'icon': IconSelectWidget(choices=ICON_CHOICES)  # Используем кастомный виджет для поля icon
        }

class RoomTypeFeaturesDetailedForm(forms.ModelForm):
    text_ru = forms.CharField(max_length=100)
    text_kk = forms.CharField(max_length=100)
    text_en = forms.CharField(max_length=100)
    
    class Meta:
        model = RoomTypeFeaturesDetailed
        fields = '__all__'

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = '__all__'

    
class PriceOnDateForm(forms.ModelForm):
    dynamic_pricing_input = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
        help_text="Введите цены по датам в формате JSON: {'YYYY-MM-DD': price}. Например: {'2025-05-15': 150.00}"
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

class RoomTypeDescriptionForm(forms.ModelForm):
    description_ru = forms.CharField(widget=CKEditorUploadingWidget(attrs={'cols': 100, 'rows': 100}))
    description_kk = forms.CharField(widget=CKEditorUploadingWidget())
    description_en = forms.CharField(widget=CKEditorUploadingWidget())
    
    class Meta:
        model = RoomTypeDescription
        fields = '__all__'
        
    class Media:
        css = {
            'all': ('css/custom_admin.css',),  # Подключаем кастомный CSS
        }

        
class HotelGallery_Tab(admin.TabularInline):
    model = HotelGallery
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            for form in formset.form.base_fields.values():
                if 'hgid' in formset.form.base_fields:
                    formset.form.base_fields['hgid'].widget = forms.HiddenInput()

        return formset

class HotelFeatures_Tab(admin.TabularInline):
    model = HotelFeatures
    form = HotelFeaturesForm  # Подключаем кастомную форму с виджетом
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            for form in formset.form.base_fields.values():
                if 'hfid' in formset.form.base_fields:
                    formset.form.base_fields['hfid'].widget = forms.HiddenInput()

        return formset

class HotelFAQs_Tab(admin.TabularInline):
    model = HotelFAQs
    exclude = ['question', 'answer']
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            for form in formset.form.base_fields.values():
                if 'hfid' in formset.form.base_fields:
                    formset.form.base_fields['hfid'].widget = forms.HiddenInput()

        return formset

class Room_Tab(admin.TabularInline):
    model = Room
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room_type":
            parent_id = request.resolver_match.kwargs.get('object_id')  # Получаем ID текущего отеля
            if parent_id:
                kwargs["queryset"] = RoomType.objects.filter(hotel_id=parent_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            for form in formset.form.base_fields.values():
                if 'rid' in formset.form.base_fields:
                    formset.form.base_fields['rid'].widget = forms.HiddenInput()

        return formset

class RoomTypeDescription_Tab(admin.TabularInline):
    model = RoomTypeDescription
    form = RoomTypeDescriptionForm
    extra = 0
    exclude = ['description']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room_type":
            parent_id = request.resolver_match.kwargs.get('object_id')  # Получаем ID текущего отеля
            if parent_id:
                kwargs["queryset"] = RoomType.objects.filter(hotel_id=parent_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# class ActivityLog_Tab(admin.TabularInline):
#     model = ActivityLog

# class StaffOnDuty_Tab(admin.TabularInline):
#     model = StaffOnDuty

class CouponUsers_Tab(admin.TabularInline):
    model = CouponUsers



class RoomType_Tab(admin.TabularInline):
    model = RoomType
    form = RoomTypeForm
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            for form in formset.form.base_fields.values():
                if 'rtid' in formset.form.base_fields:
                    formset.form.base_fields['rtid'].widget = forms.HiddenInput()
                if 'slug' in formset.form.base_fields:
                    formset.form.base_fields['slug'].widget = forms.HiddenInput()

        return formset

class RoomTypeGallery_Tab(admin.TabularInline):
    model = RoomTypeGallery
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room_type":
            parent_id = request.resolver_match.kwargs.get('object_id')  # Получаем ID текущего отеля
            if parent_id:
                kwargs["queryset"] = RoomType.objects.filter(hotel_id=parent_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class RoomTypeFeatures_Tab(admin.TabularInline):
    model = RoomTypeFeatures
    form = RoomTypeFeaturesForm
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room_type":
            parent_id = request.resolver_match.kwargs.get('object_id')  # Получаем ID текущего отеля
            if parent_id:
                kwargs["queryset"] = RoomType.objects.filter(hotel_id=parent_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            for form in formset.form.base_fields.values():
                if 'hfid' in formset.form.base_fields:
                    formset.form.base_fields['hfid'].widget = forms.HiddenInput()

        return formset

class RoomTypeFeaturesDetailed_Tab(admin.TabularInline):
    model = RoomTypeFeaturesDetailed
    form = RoomTypeFeaturesDetailedForm
    extra = 0
    exclude = ['text']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room_type":
            parent_id = request.resolver_match.kwargs.get('object_id')  # Получаем ID текущего отеля
            if parent_id:
                kwargs["queryset"] = RoomType.objects.filter(hotel_id=parent_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            for form in formset.form.base_fields.values():
                if 'hfid' in formset.form.base_fields:
                    formset.form.base_fields['hfid'].widget = forms.HiddenInput()

        return formset

class HotelAdmin(BaseImportExportAdmin):
    form = HotelAdminForm
    inlines = [
        HotelGallery_Tab, HotelFeatures_Tab, RoomType_Tab, RoomTypeDescription_Tab, 
        RoomTypeGallery_Tab, RoomTypeFeatures_Tab, RoomTypeFeaturesDetailed_Tab, Room_Tab, HotelFAQs_Tab
    ]
    list_filter = ['featured', 'status']
    list_editable = ['status']
    list_display = ['thumbnail', 'name_ru', 'user', 'status', 'featured', 'views']
    list_per_page = 100
    prepopulated_fields = {"slug": ("name_en", )}
    exclude = ['description']
    search_fields = ['name_ru', 'user__username', 'status']
    search_help_text = 'Поиск по Названию [RU], Пользователю, Статусу'

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
        form = super().get_form(request, obj, **kwargs)
        if is_manager(request.user):
            form.base_fields.pop('user', None)
            for field in ['featured', 'slug', 'hid', 'status', 'views', 'name']:
                if field in form.base_fields:
                    form.base_fields[field].widget = forms.HiddenInput()
        return form

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if is_manager(request.user):
            return queryset.filter(user=request.user)
        return queryset

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

class RoomAdmin(BaseImportExportAdmin):
    list_display = ['hotel', 'room_type', 'room_number', 'get_price', 'number_of_beds', 'is_available']
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

    def get_price(self, obj):
        if obj.room_type:
            return obj.room_type.price
        return None
    
    get_price.short_description = 'Цена'
    get_price.admin_order_field = 'room_type__price'

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



class BookingAdmin(BaseImportExportAdmin):
    # inlines = [ActivityLog_Tab, StaffOnDuty_Tab]
    list_filter = [HotelFilter, RoomTypeFilter, 'is_active', 'checked_in', 'checked_out', CheckInDateFilter]
    list_display = ['booking_id', 'user', 'hotel', 'room_type', 'rooms', 'total', 'total_days', 'num_adults', 'num_children', 'check_in_date', 'check_out_date', 'is_active', 'checked_in', 'checked_out']
    search_fields = ['booking_id', 'robokassa_inv_id']
    search_help_text = 'Поиск по ID бронирования, ID инвойса Robokassa, Сумме'
    list_per_page = 100

    def get_search_fields(self, request):
        if is_manager(request.user):
            self.search_help_text = 'Поиск по ID бронирования, ID инвойса Robokassa'
            return ['booking_id', 'robokassa_inv_id']
        return self.search_fields

    def get_list_filter(self, request):
        if is_manager(request.user):
            return [HotelFilter, RoomTypeFilter, 'checked_in', 'checked_out']
        return self.list_filter

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Если пользователь принадлежит группе Manager и не является суперпользователем
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Фильтруем только те комнаты, которые связаны с отелями, созданным пользователем
            queryset = queryset.filter(hotel__user=request.user)
        return queryset

class RoomServicesAdmin(BaseImportExportAdmin):
    list_display = ['booking', 'room', 'date', 'price', 'service_type']
    list_per_page = 100

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ограничиваем видимость записей для менеджеров
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(booking__hotel__user=request.user)
        return queryset
    

class CouponAdmin(BaseImportExportAdmin):
    inlines = [CouponUsers_Tab]
    list_editable = ['valid_from', 'valid_to', 'active', 'type']
    list_display = ['code', 'discount', 'type', 'redemption', 'valid_from', 'valid_to', 'active', 'date']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ограничиваем видимость записей для менеджеров
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(hotel__user=request.user)
        return queryset

class NotificationAdmin(BaseImportExportAdmin):
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


class BookmarkAdmin(BaseImportExportAdmin):
    list_display = ['user', 'hotel']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ограничиваем видимость записей для менеджеров
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(hotel__user=request.user)
        return queryset


class ReviewAdmin(admin.ModelAdmin):
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

class PriceOnDateAdmin(BaseImportExportAdmin):
    form = PriceOnDateForm
    list_display = ['type', 'hotel']
    list_filter = [HotelFilter]
    search_fields = ['type', 'hotel__name_ru']
    search_help_text = 'Поиск по Типу номера, Отелю'
    exclude = ['dynamic_pricing', 'number_of_beds', 'room_capacity', 'room_size', 'rtid']
    prepopulated_fields = {"slug": ("type", )}
    change_form_template = 'admin/hotel/roomtype/change_form.html'  # Кастомный шаблон для PriceOnDate

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
    if sender.name == 'hotel':  # Только для приложения hotel
        # Получаем или создаем группу Manager
        manager_group, created = Group.objects.get_or_create(name='Manager')
        
        # Добавляем разрешения для PriceOnDate
        content_type = ContentType.objects.get_for_model(RoomType)
        permissions = Permission.objects.filter(content_type=content_type)
        
        for permission in permissions:
            manager_group.permissions.add(permission)
        
        print(f"Разрешения для PriceOnDate добавлены группе Manager: {[p.codename for p in permissions]}")

class CustomAdminSite(admin.AdminSite):
    def get_app_list(self, request, app_label=None):
        if app_label:
            app_list = super().get_app_list(request, app_label)
        else:
            app_list = super().get_app_list(request)
        
        for app in app_list:
            if app['app_label'] == 'hotel':
                for model in app['models']:
                    if model['object_name'] == 'RoomType' and model['admin_url'] == '/admin/hotel/roomtype/':
                        model['name'] = 'Цены по датам'
        return app_list

# Instantiate the custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register models with the custom admin site
custom_admin_site.register(Hotel, HotelAdmin)
custom_admin_site.register(Room, RoomAdmin)
custom_admin_site.register(RoomType, PriceOnDateAdmin)
custom_admin_site.register(Booking, BookingAdmin)
custom_admin_site.register(RoomServices, RoomServicesAdmin)
custom_admin_site.register(Coupon, CouponAdmin)
custom_admin_site.register(Notification, NotificationAdmin)
custom_admin_site.register(Bookmark, BookmarkAdmin)
custom_admin_site.register(Review, ReviewAdmin)

# Register Django auth models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import GroupAdmin, UserAdmin
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(Permission)