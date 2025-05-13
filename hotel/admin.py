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
    list_display = ['hotel' ,'room_number',  'room_type', 'price', 'number_of_beds' ,'is_available']
    list_per_page = 100

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

class BookingAdmin(BaseImportExportAdmin):
    #inlines = [ActivityLog_Tab, StaffOnDuty_Tab]
    list_filter = [HotelFilter, RoomTypeFilter, 'check_in_date', 'check_out_date', 'is_active', 'checked_in', 'checked_out']
    list_display = ['booking_id', 'user', 'hotel', 'room_type', 'rooms', 'total', 'total_days', 'num_adults', 'num_children', 'check_in_date', 'check_out_date', 'is_active' , 'checked_in' ,'checked_out']
    #search_fields = ['booking_id', 'user__username', 'user__email']
    list_per_page = 100

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Если пользователь принадлежит группе Manager и не является суперпользователем
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Фильтруем только бронирования, относящиеся к отелям, созданным пользователем
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
    list_display = ['hotel', 'type']
    list_filter = [HotelFilter]
    exclude = ['dynamic_pricing', 'number_of_beds', 'room_capacity', 'room_size','rtid']
    prepopulated_fields = {"slug": ("type", )}
    change_form_template = 'admin/hotel/roomtype/change_form.html'  # Кастомный шаблон для PriceOnDate
    
    verbose_name = "Цена по датам"
    verbose_name_plural = "Цены по датам"
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(hotel__user=request.user)
        return queryset
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if is_manager(request.user):
            # Hide fields for Managers
            for field in ['slug', 'rtid','hotel','type', 'price']:
                if field in form.base_fields:
                    form.base_fields[field].widget = forms.HiddenInput()
        return form
    
    def save_model(self, request, obj, form, change):
        # Проверим наличие данных в форме и их корректность
        print(f"Save model called. POST data: {request.POST}")
        
        # Получаем значение напрямую из POST запроса
        if 'dynamic_pricing_input' in request.POST:
            try:
                # Так как POST может содержать несколько значений, берем первое, которое обычно содержит актуальные данные
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
                
        # Также берем из cleaned_data если оно там есть
        if hasattr(form, 'cleaned_data') and 'dynamic_pricing_input' in form.cleaned_data:
            pricing_data = form.cleaned_data['dynamic_pricing_input']
            print(f"Setting dynamic_pricing from cleaned_data: {pricing_data}")
            obj.dynamic_pricing = pricing_data
            
        super().save_model(request, obj, form, change)
        
        # Дополнительная проверка после сохранения
        print(f"After save: obj.dynamic_pricing = {obj.dynamic_pricing}")
        
    def response_change(self, request, obj):
        # После сохранения проверим, что данные сохранились
        if obj.dynamic_pricing:
            pricing_count = len(obj.dynamic_pricing) if isinstance(obj.dynamic_pricing, dict) else 0
            self.message_user(request, f"Динамические цены успешно сохранены. {pricing_count} дней с ценами.")
        return super().response_change(request, obj)

admin.site.register(Hotel, HotelAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(RoomType, PriceOnDateAdmin)  # Регистрируем RoomType с нашим новым админ-классом
admin.site.register(Booking, BookingAdmin)
admin.site.register(RoomServices, RoomServicesAdmin)
admin.site.register(Coupon, CouponAdmin)

# Регистрируем Notification только для суперпользователей
if not admin.site.is_registered(Notification):
    admin.site.register(Notification, NotificationAdmin)

admin.site.register(Bookmark, BookmarkAdmin)

# Регистрируем Review только для суперпользователей
if not admin.site.is_registered(Review):
    admin.site.register(Review, ReviewAdmin)

