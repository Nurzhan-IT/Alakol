from django.contrib import admin
from userauths.models import User, Profile, UserConsent
from django.utils.html import mark_safe
from hotel.admin import custom_admin_site, RussianModelAdminMixin

@admin.register(User, site=custom_admin_site)
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

@admin.register(Profile, site=custom_admin_site)
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

    @admin.display(
        description='Миниатюра'
    )
    def thumbnail(self, obj):
        return mark_safe('<img src="/media/%s" width="50" height="50" style="object-fit: cover; border-radius: 6px;" />' % (obj.image))

@admin.register(UserConsent, site=custom_admin_site)
class UserConsentAdmin(RussianModelAdminMixin, admin.ModelAdmin):
    """Админка для согласий пользователей"""
    list_display = ['user', 'consent_type', 'document_version', 'given_at', 'is_active', 'withdrawn_at']
    list_filter = ['consent_type', 'document_version', 'is_active', 'given_at']
    search_fields = ['user__username', 'user__email', 'user__full_name']
    readonly_fields = ['user_agent', 'given_at']
    ordering = ['-given_at']
    
    def _setup_russian_verbose_names(self):
        """Устанавливает русские названия для модели"""
        self.model._meta.verbose_name = 'Согласие пользователя'
        self.model._meta.verbose_name_plural = 'Согласия пользователей'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.groups.filter(name='Manager').exists() and not request.user.is_superuser:
            # Менеджеры видят только свои согласия
            queryset = queryset.filter(user=request.user)
        return queryset

# Регистрируем модели в админке
