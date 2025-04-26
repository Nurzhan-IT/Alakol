from django import forms
from django.contrib import admin
from hotel.models import  ICON_CHOICES,Hotel, Room, Booking, RoomServices, HotelGallery, RoomTypeGallery,RoomTypeFeatures, HotelFeatures, HotelFAQs, RoomType, RoomTypeDescription,ActivityLog, StaffOnDuty, Coupon, CouponUsers, Notification, Bookmark, Review
from import_export.admin import ImportExportModelAdmin
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

# Проверка принадлежности пользователя к группе Manager
def is_manager(user):
    return user.groups.filter(name='Manager').exists() and not user.is_superuser

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

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = '__all__'   

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


class ActivityLog_Tab(admin.TabularInline):
    model = ActivityLog

class StaffOnDuty_Tab(admin.TabularInline):
    model = StaffOnDuty

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

class HotelAdmin(ImportExportModelAdmin):
    form = HotelAdminForm
    inlines = [
        HotelGallery_Tab, HotelFeatures_Tab, RoomType_Tab, RoomTypeDescription_Tab, 
        RoomTypeGallery_Tab, RoomTypeFeatures_Tab, Room_Tab, HotelFAQs_Tab
    ]
    search_fields = ['user__username', 'name']
    list_filter = ['featured', 'status']
    list_editable = ['status']
    list_display = ['thumbnail', 'name_ru', 'user', 'status', 'featured', 'views', 'chessboard_link']
    list_per_page = 100
    prepopulated_fields = {"slug": ("name_en", )}
    exclude = ['description']

    def get_list_display(self, request):
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            return ['thumbnail', 'name_ru']  # Упрощенный список для менеджеров
        return super().get_list_display(request)


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            form.base_fields.pop('user', None)  # Без ошибки, если поля нет

    
            for field in ['featured','slug','hid','status','views','name']:
                if field in form.base_fields:
                    form.base_fields[field].widget = forms.HiddenInput()
        return form

    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        custom_urls = [
            path('<int:hotel_id>/chessboard/', 
                 self.admin_site.admin_view(self.chessboard_view), 
                 name='hotel_chessboard'),
        ]
        return custom_urls + urls

    def chessboard_view(self, request, hotel_id):
        if not is_manager(request.user):
            self.message_user(request, "У вас нет доступа к шахматке.", level='error')
            return redirect('admin:index')

        try:
            hotel = Hotel.objects.get(id=hotel_id, user=request.user)
        except Hotel.DoesNotExist:
            self.message_user(request, "Отель не найден или не принадлежит вам.", level='error')
            return redirect('admin:hotel_hotel_changelist')

        start_date = timezone.now().date()
        days_to_show = 30
        end_date = start_date + timedelta(days=days_to_show)
        
        rooms = Room.objects.filter(hotel=hotel).select_related('room_type')
        bookings = Booking.objects.filter(
            hotel=hotel,
            check_in_date__lte=end_date,
            check_out_date__gte=start_date,
            is_active=True
        ).prefetch_related('room')
        
        date_range = [start_date + timedelta(days=x) for x in range(days_to_show)]
        
        # Преобразуем chessboard_data в формат, удобный для шаблона
        chessboard_data = []
        for room in rooms:
            room_data = {
                'room': room,
                'dates': {}
            }
            for date in date_range:
                booking = next(
                    (b for b in bookings 
                    if room in b.room.all() and b.check_in_date <= date < b.check_out_date),
                    None
                )
                room_data['dates'][date] = {
                    'booking': booking,
                    'status': booking.payment_status if booking else 'free',
                }
            chessboard_data.append(room_data)

        context = {
            'hotel': hotel,
            'chessboard_data': chessboard_data,
            'date_range': date_range,
            'opts': self.model._meta,
        }
        return render(request, 'admin/hotel_chessboard.html', context)
    
    # Добавляем ссылку на шахматку в список отелей
    def chessboard_link(self, obj):
        if is_manager(self.request.user):
            url = reverse('admin:hotel_chessboard', args=[obj.id])
            return format_html('<a href="{}">Шахматка</a>', url)
        return "-"
    chessboard_link.short_description = "Шахматка"

    def get_list_display(self, request):
        self.request = request  # Сохраняем request для chessboard_link
        if is_manager(request.user):
            return ['thumbnail', 'name_ru', 'chessboard_link']
        return super().get_list_display(request)

    # Ограничение видимости записей
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Показываем только записи, созданные текущим пользователем
            return queryset.filter(user=request.user)
        return queryset

    # Установка текущего пользователя как автора записи
    def save_model(self, request, obj, form, change):
        if not change:  # Если создается новая запись
            obj.user = request.user
        super().save_model(request, obj, form, change)


class RoomAdmin(ImportExportModelAdmin):
    list_display = ['hotel' ,'room_number',  'room_type', 'price', 'number_of_beds' ,'is_available']
    list_per_page = 100

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Если пользователь принадлежит группе Manager и не является суперпользователем
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Фильтруем только те комнаты, которые связаны с отелями, созданными пользователем
            queryset = queryset.filter(hotel__user=request.user)
        return queryset


class BookingAdmin(ImportExportModelAdmin):
    inlines = [ActivityLog_Tab, StaffOnDuty_Tab]
    list_filter = [ 'hotel', 'room_type', 'check_in_date', 'check_out_date', 'is_active' , 'checked_in' ,'checked_out']
    list_display = ['booking_id', 'user', 'hotel', 'room_type', 'rooms', 'total', 'total_days', 'num_adults', 'num_children', 'check_in_date', 'check_out_date', 'is_active' , 'checked_in' ,'checked_out']
    search_fields = ['booking_id', 'user__username', 'user__email']
    list_per_page = 100

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Если пользователь принадлежит группе Manager и не является суперпользователем
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Фильтруем только бронирования, относящиеся к отелям, созданным пользователем
            queryset = queryset.filter(hotel__user=request.user)
        return queryset


class RoomServicesAdmin(ImportExportModelAdmin):
    list_display = ['booking', 'room', 'date', 'price', 'service_type']
    list_per_page = 100

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ограничиваем видимость записей для менеджеров
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(booking__hotel__user=request.user)
        return queryset
    

class CouponAdmin(ImportExportModelAdmin):
    inlines = [CouponUsers_Tab]
    list_editable = ['valid_from', 'valid_to', 'active', 'type']
    list_display = ['code', 'discount', 'type', 'redemption', 'valid_from', 'valid_to', 'active', 'date']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ограничиваем видимость записей для менеджеров
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(hotel__user=request.user)
        return queryset

class NotificationAdmin(ImportExportModelAdmin):
    list_editable = ['seen', 'type']
    list_display = ['user', 'booking', 'type', 'seen', 'date']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ограничиваем видимость записей для менеджеров
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(booking__hotel__user=request.user)
        return queryset


class BookmarkAdmin(ImportExportModelAdmin):
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Ограничиваем видимость записей для менеджеров
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(hotel__user=request.user)
        return queryset


admin.site.register(Hotel, HotelAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(RoomServices, RoomServicesAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Review, ReviewAdmin)

