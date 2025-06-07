from django.contrib import admin
from userauths.models import User, Profile
from django.utils.html import mark_safe
from hotel.admin import custom_admin_site, RussianModelAdminMixin

class UserAdmin(RussianModelAdminMixin, admin.ModelAdmin):
    search_fields  = ['full_name', 'username', 'email',  'phone', 'gender']
    list_display  = ['full_name', 'username', 'email',  'phone', 'gender']
    
    def _setup_russian_verbose_names(self):
        """Устанавливает русские названия для модели"""
        self.model._meta.verbose_name = 'Пользователь'
        self.model._meta.verbose_name_plural = 'Пользователи'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(id=getattr(request.user, "id", None))
        return queryset

class ProfileAdmin(RussianModelAdminMixin, admin.ModelAdmin):
    search_fields = ['user__username', 'full_name']
    
    def _setup_russian_verbose_names(self):
        """Устанавливает русские названия для модели"""
        self.model._meta.verbose_name = 'Профиль'
        self.model._meta.verbose_name_plural = 'Профили'
    
    # Список полей, доступных только для Manager
    manager_fields = [
        "image", 
        "full_name", 
        "phone", 
        "gender", 
        "country", 
        "city", 
        "address", 

    ]
    
    # Поля для отображения в списке
    list_display = ['thumbnail', 'user', 'full_name', 'verified']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)  # Показываем только профиль текущего менеджера
        return queryset

    def get_fields(self, request, obj=None):
        """
        Динамически задаём поля формы в зависимости от группы пользователя.
        """
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            return self.manager_fields
        return super().get_fields(request, obj)

    def get_list_display(self, request):
        """
        Ограничиваем отображаемые колонки в списке для Manager.
        """
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            return ['thumbnail', 'full_name']  # Ограничиваем список до минимума
        return self.list_display


custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Profile, ProfileAdmin)