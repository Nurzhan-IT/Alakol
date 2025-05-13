from django.contrib import admin
from .models import RoomUnavailability
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Q

@admin.register(RoomUnavailability)
class RoomUnavailabilityAdmin(admin.ModelAdmin):
    list_display = ('room', 'start_date', 'end_date', 'reason', 'created_at')
    list_filter = ('room', 'start_date', 'end_date')
    search_fields = ('room__room_number', 'reason')
    date_hierarchy = 'start_date'
    
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
        except ValidationError as e:
            self.message_user(request, str(e), level=messages.ERROR)