from django.contrib import admin
from userauths.models import User, Profile
from django.utils.html import mark_safe

class UserAdmin(admin.ModelAdmin):
    search_fields  = ['full_name', 'username', 'email',  'phone', 'gender']
    list_display  = ['full_name', 'username', 'email',  'phone', 'gender']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            queryset = queryset.filter(id=getattr(request.user, "id", None))
        return queryset

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'full_name']
    
    # Список полей, доступных только для Manager
    manager_fields = [
        "image", 
        "full_name", 
        "phone", 
        "gender", 
        "country", 
        "city", 
        "state", 
        "address", 
        "identity_type", 
        "identity_image", 
        "facebook", 
        "twitter"
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




admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)