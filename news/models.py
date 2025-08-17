from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.utils.translation import gettext_lazy as _
from shortuuid.django_fields import ShortUUIDField

import shortuuid


def validate_news_image(file):
    """Валидация изображений для новостей"""
    max_size_mb = 5  # Максимальный размер файла в MB
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Максимальный размер файла {max_size_mb}MB")
    
    width, height = get_image_dimensions(file)
    if width < 300 or height < 200:  # Минимальные размеры для новостей
        raise ValidationError("Изображение слишком маленькое. Минимальные размеры: 300x200 пикселей.")


NEWS_STATUS = (
    ("draft", "Черновик"),
    ("published", "Опубликовано"),
    ("archived", "Архив"),
)


class NewsCategory(models.Model):
    """Категории новостей"""
    name = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(unique=True, blank=True, verbose_name='Слаг')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Категория новостей'
        verbose_name_plural = 'Категории новостей'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class News(models.Model):
    """Модель новостей с поддержкой многоязычности"""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(unique=True, blank=True, verbose_name='Слаг')
    category = models.ForeignKey(
        NewsCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='Категория'
    )
    
    # Краткое описание для главной страницы
    excerpt = models.TextField(
        max_length=300, 
        verbose_name='Краткое описание',
        help_text='Краткое описание новости для отображения на главной странице'
    )
    
    # Полный текст новости
    content = models.TextField(verbose_name='Содержание')
    
    # Изображения
    featured_image = models.ImageField(
        upload_to='news/featured/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_news_image
        ],
        verbose_name='Главное изображение',
        help_text='Изображение для отображения на главной странице'
    )
    
    # Дополнительные поля
    author = models.CharField(
        max_length=100, 
        default='Редакция Alakol',
        verbose_name='Автор'
    )
    
    # SEO поля
    meta_title = models.CharField(
        max_length=60, 
        blank=True, 
        verbose_name='Meta Title',
        help_text='SEO заголовок (до 60 символов)'
    )
    meta_description = models.CharField(
        max_length=160, 
        blank=True, 
        verbose_name='Meta Description',
        help_text='SEO описание (до 160 символов)'
    )
    
    # Статус и даты
    status = models.CharField(
        max_length=20, 
        choices=NEWS_STATUS, 
        default='draft', 
        verbose_name='Статус'
    )
    
    is_featured = models.BooleanField(
        default=False, 
        verbose_name='Рекомендуемая',
        help_text='Отображать в блоке рекомендуемых новостей'
    )
    
    on_homepage = models.BooleanField(
        default=False,
        verbose_name='На главной',
        help_text='Отображать новость на главной странице'
    )
    
    views_count = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')
    
    # Технические поля
    nid = ShortUUIDField(
        unique=True, 
        length=10, 
        max_length=20, 
        alphabet="abcdefghijklmnopqrstuvxyz",
        verbose_name='ID новости'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['is_featured', 'published_at']),
            models.Index(fields=['on_homepage', 'published_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Генерация slug из заголовка
        if not self.slug:
            uuid_key = shortuuid.uuid()
            uniqueid = uuid_key[:4]
            self.slug = slugify(self.title) + "-" + str(uniqueid.lower())
        
        # Автоматическая установка published_at при публикации
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        # Автоматическое заполнение meta полей, если они пустые
        if not self.meta_title:
            self.meta_title = self.title[:60]
        
        if not self.meta_description:
            self.meta_description = self.excerpt[:160]
        
        super().save(*args, **kwargs)

    def thumbnail(self):
        """Миниатюра изображения для админки"""
        if self.featured_image and hasattr(self.featured_image, 'url'):
            try:
                return mark_safe(
                    f'<img src="{self.featured_image.url}" '
                    f'width="80" height="60" '
                    f'style="object-fit:cover; border-radius: 4px;" />'
                )
            except ValueError:
                return mark_safe(
                    '<div style="width: 80px; height: 60px; background-color: #f0f0f0; '
                    'display: flex; align-items: center; justify-content: center; '
                    'border-radius: 4px; font-size: 12px; color: #666;">Нет изображения</div>'
                )
        return mark_safe(
            '<div style="width: 80px; height: 60px; background-color: #f0f0f0; '
            'display: flex; align-items: center; justify-content: center; '
            'border-radius: 4px; font-size: 12px; color: #666;">Нет изображения</div>'
        )
    
    thumbnail.short_description = 'Миниатюра'

    def get_absolute_url(self):
        """URL для просмотра новости"""
        return f'/news/{self.slug}/'

    def is_published(self):
        """Проверка, опубликована ли новость"""
        return self.status == 'published'

    @classmethod
    def get_published(cls):
        """Получить все опубликованные новости"""
        return cls.objects.filter(status='published').order_by('-published_at')

    @classmethod
    def get_featured(cls, limit=3):
        """Получить рекомендуемые новости для главной страницы"""
        return cls.objects.filter(
            status='published', 
            is_featured=True
        ).order_by('-published_at')[:limit]
    
    @classmethod
    def get_homepage_news(cls, limit=6):
        """Получить новости для отображения на главной странице"""
        return cls.objects.filter(
            status='published',
            on_homepage=True
        ).order_by('-published_at')[:limit]


class NewsGallery(models.Model):
    """Дополнительные изображения для новостей"""
    news = models.ForeignKey(
        News, 
        on_delete=models.CASCADE, 
        related_name='gallery',
        verbose_name='Новость'
    )
    image = models.ImageField(
        upload_to='news/gallery/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_news_image
        ],
        verbose_name='Изображение'
    )
    caption = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Подпись к изображению'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Изображение новости'
        verbose_name_plural = 'Изображения новостей'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.news.title} - Изображение {self.id}"

    def thumbnail(self):
        """Миниатюра изображения для админки"""
        if self.image and hasattr(self.image, 'url'):
            try:
                return mark_safe(
                    f'<img src="{self.image.url}" '
                    f'width="60" height="45" '
                    f'style="object-fit:cover; border-radius: 4px;" />'
                )
            except ValueError:
                return "Нет изображения"
        return "Нет изображения"
    
    thumbnail.short_description = 'Миниатюра'