from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Hotel, RoomType

class HotelSitemap(Sitemap):
    """Sitemap для отелей с мультиязычной поддержкой"""
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Hotel.objects.filter(status='Live').order_by('-date')

    def location(self, item):
        return reverse('hotel:detail', args=[item.slug])

    def lastmod(self, item):
        return item.date

class RoomTypeSitemap(Sitemap):
    """Sitemap для типов номеров"""
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return RoomType.objects.filter(hotel__status='Live').select_related('hotel')

    def location(self, item):
        # Возвращаем URL к отелю с якорем на тип номера
        return f"{reverse('hotel:detail', args=[item.hotel.slug])}#room-{item.id}"

    def lastmod(self, item):
        return item.date

class StaticViewSitemap(Sitemap):
    """Sitemap для статических страниц"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'hotel:index',
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        return timezone.now()

class SearchPagesSitemap(Sitemap):
    """Sitemap для страниц поиска"""
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return [
            'search:search_results',
        ]

    def location(self, item):
        try:
            return reverse(item)
        except:
            return '/search/'

    def lastmod(self, obj):
        return timezone.now()

class LegalPagesSitemap(Sitemap):
    """Sitemap для юридических страниц"""
    priority = 0.4
    changefreq = "monthly"

    def items(self):
        return [
            'legal:terms_of_use',
            'legal:privacy_policy', 
            'legal:public_offer',
        ]

    def location(self, item):
        try:
            return reverse(item)
        except:
            # Fallback для случаев, когда URL не найден
            page_name = item.split(":")[-1].replace("_", "-")
            return f'/legal/{page_name}/'

    def lastmod(self, obj):
        return timezone.now() 