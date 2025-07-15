from django.contrib import admin
from .models import RoomUnavailability
from .forms import RoomUnavailabilityForm
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from hotel.models import Room, Hotel, RoomType
from hotel.admin import custom_admin_site, RussianModelAdminMixin

class RoomFilter(admin.SimpleListFilter):
    title = 'Номер'
    parameter_name = 'room'

    def lookups(self, request, model_admin):
        # Если пользователь в группе Manager и не является суперпользователем
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            rooms = Room.objects.filter(hotel__user=request.user)
        else:
            rooms = Room.objects.all()
        return [(room.id, f"{room.room_number} ({room.hotel.name})") for room in rooms]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(room_id=self.value())
        return queryset

class RoomTypeFilter(admin.SimpleListFilter):
    title = 'Тип номера'
    parameter_name = 'room_type'

    def lookups(self, request, model_admin):
        # Если пользователь в группе Manager и не является суперпользователем
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            room_types = RoomType.objects.filter(hotel__user=request.user)
        else:
            room_types = RoomType.objects.all()
        return [(rt.id, f"{rt.type} ({rt.hotel.name})") for rt in room_types]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(room__room_type_id=self.value())
        return queryset

# @admin.register(RoomUnavailability)
class RoomUnavailabilityAdmin(RussianModelAdminMixin, admin.ModelAdmin):
    form = RoomUnavailabilityForm
    list_display = ('get_room', 'start_date', 'end_date', 'reason', 'created_at')
    list_filter = (RoomFilter, RoomTypeFilter)  # Добавляем RoomTypeFilter
    # date_hierarchy = 'start_date'
    
    class Media:
        css = {
            'all': ('css/room_unavailability_admin.css',)
        }
        js = ('js/room_unavailability_validation.js',)

    def _setup_russian_verbose_names(self):
        """Устанавливает русские названия для модели"""
        self.model._meta.verbose_name = 'Недоступность номера'
        self.model._meta.verbose_name_plural = 'Недоступность номеров'

    def get_room(self, obj):
        """Отображает только название типа номера"""
        if obj.room:
            return f"{obj.room.room_type.type} - № {obj.room.room_number}"
        return None
    
    get_room.short_description = 'Номер'
    get_room.admin_order_field = 'room__room_number'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Если пользователь принадлежит группе Manager и не является суперпользователем
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Фильтруем только те записи, которые связаны с комнатами из отелей, созданных пользователем
            queryset = queryset.filter(room__hotel__user=request.user)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Ограничиваем выбор комнат только теми, которые находятся в отелях менеджера
        if db_field.name == "room" and request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(hotel__user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()  # Вызывает метод clean()
            super().save_model(request, obj, form, change)
            self.message_user(request, 'Запись успешно сохранена.', level=messages.SUCCESS)
        except ValidationError as e:
            # Отображаем ошибки валидации пользователю
            error_messages = []
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
            else:
                error_messages.append(str(e))
            
            for error_msg in error_messages:
                self.message_user(request, error_msg, level=messages.ERROR)

custom_admin_site.register(RoomUnavailability, RoomUnavailabilityAdmin)