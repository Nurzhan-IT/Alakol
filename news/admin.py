from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import News, NewsCategory, NewsGallery

# Проверяем, доступен ли modeltranslation
try:
    from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
    TRANSLATION_AVAILABLE = True
except ImportError:
    # Если modeltranslation недоступен, используем обычный админ
    TranslationAdmin = admin.ModelAdmin
    TranslationTabularInline = admin.TabularInline
    TRANSLATION_AVAILABLE = False


class NewsGalleryInline(admin.TabularInline):
    """Inline для дополнительных изображений новостей"""
    model = NewsGallery
    extra = 1
    max_num = 10
    fields = ('image', 'caption', 'order', 'thumbnail')
    readonly_fields = ('thumbnail',)


class NewsCategoryAdmin(admin.ModelAdmin):
    """Админка для категорий новостей"""
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
    )


class NewsAdmin(admin.ModelAdmin):
    """Админка для новостей с поддержкой многоязычности"""
    list_display = (
        'thumbnail', 'title', 'category', 'author', 'status', 
        'is_featured', 'on_homepage', 'views_count', 'published_at', 'view_on_site'
    )
    list_filter = (
        'status', 'is_featured', 'on_homepage', 'category', 'created_at', 'published_at'
    )
    search_fields = ('title', 'excerpt', 'content', 'author')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('nid', 'views_count', 'created_at', 'updated_at', 'thumbnail')
    inlines = [NewsGalleryInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title', 'slug', 'category', 'author', 'status', 'is_featured', 'on_homepage'
            )
        }),
        ('Содержание', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('SEO настройки', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Даты и статистика', {
            'fields': (
                'published_at', 'views_count', 'created_at', 'updated_at', 'nid'
            ),
            'classes': ('collapse',)
        }),
        ('Изображение', {
            'fields': ('thumbnail',),
            'classes': ('collapse',)
        }),
    )
    
    # Настройки отображения списка
    list_per_page = 20
    date_hierarchy = 'published_at'
    
    # Настройки фильтрации
    list_editable = ('status', 'is_featured', 'on_homepage')
    
    actions = ['make_published', 'make_draft', 'make_featured', 'remove_featured', 'add_to_homepage', 'remove_from_homepage']

    @admin.action(
        description="Опубликовать выбранные новости"
    )
    def make_published(self, request, queryset):
        """Действие для публикации новостей"""
        updated = 0
        for news in queryset:
            if news.status != 'published':
                news.status = 'published'
                if not news.published_at:
                    news.published_at = timezone.now()
                news.save()
                updated += 1
        
        self.message_user(
            request, 
            f'Опубликовано новостей: {updated}'
        )

    @admin.action(
        description="Перевести в черновик"
    )
    def make_draft(self, request, queryset):
        """Действие для перевода новостей в черновик"""
        updated = queryset.update(status='draft')
        self.message_user(
            request, 
            f'Переведено в черновик: {updated} новостей'
        )

    @admin.action(
        description="Добавить в рекомендуемые"
    )
    def make_featured(self, request, queryset):
        """Действие для добавления в рекомендуемые"""
        updated = queryset.update(is_featured=True)
        self.message_user(
            request, 
            f'Добавлено в рекомендуемые: {updated} новостей'
        )

    @admin.action(
        description="Удалить из рекомендуемых"
    )
    def remove_featured(self, request, queryset):
        """Действие для удаления из рекомендуемых"""
        updated = queryset.update(is_featured=False)
        self.message_user(
            request, 
            f'Удалено из рекомендуемых: {updated} новостей'
        )

    @admin.action(
        description="Добавить на главную страницу"
    )
    def add_to_homepage(self, request, queryset):
        """Действие для добавления на главную страницу"""
        updated = queryset.update(on_homepage=True)
        self.message_user(
            request, 
            f'Добавлено на главную страницу: {updated} новостей'
        )

    @admin.action(
        description="Удалить с главной страницы"
    )
    def remove_from_homepage(self, request, queryset):
        """Действие для удаления с главной страницы"""
        updated = queryset.update(on_homepage=False)
        self.message_user(
            request, 
            f'Удалено с главной страницы: {updated} новостей'
        )

    @admin.display(
        description="Просмотр"
    )
    def view_on_site(self, obj):
        """Ссылка для просмотра новости на сайте"""
        if obj.status == 'published':
            url = obj.get_absolute_url()
            return format_html(
                '<a href="{}" target="_blank">Посмотреть на сайте</a>',
                url
            )
        return "Не опубликовано"

    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related('category')

    def save_model(self, request, obj, form, change):
        """Дополнительная обработка при сохранении"""
        # Автоматическая установка даты публикации
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = timezone.now()
        
        super().save_model(request, obj, form, change)


class NewsGalleryAdmin(admin.ModelAdmin):
    """Админка для дополнительных изображений новостей"""
    list_display = ('thumbnail', 'news', 'caption', 'order')
    list_filter = ('news__category', 'news__status')
    search_fields = ('news__title', 'caption')
    list_editable = ('order',)
    readonly_fields = ('thumbnail',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('news', 'image', 'caption', 'order')
        }),
        ('Изображение', {
            'fields': ('thumbnail',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related('news')