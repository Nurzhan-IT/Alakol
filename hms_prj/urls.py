"""hms_prj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import JavaScriptCatalog
from django.contrib.sitemaps.views import sitemap
from hotel.views import robokassa_result, robokassa_success_direct, robokassa_failed_direct, robots_txt, health_check, ready_check, live_check
from hotel.admin import custom_admin_site
from hotel.sitemaps import HotelSitemap, RoomTypeSitemap, StaticViewSitemap, SearchPagesSitemap, LegalPagesSitemap

# Настройка sitemaps для SEO
sitemaps = {
    'hotels': HotelSitemap,
    'room_types': RoomTypeSitemap,
    'static': StaticViewSitemap,
    'search': SearchPagesSitemap,
    'legal': LegalPagesSitemap,
}

urlpatterns = [
    path('admin/', custom_admin_site.urls),

    # Health check endpoints
    path('health/', health_check, name='health_check'),
    path('ready/', ready_check, name='ready_check'),
    path('live/', live_check, name='live_check'),

    # SEO URLs
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Apps Routes
    # path("booking/", include("booking.urls")),
    # path("user/", include("userauths.urls")),
    # path("dashboard/", include("user_dashboard.urls")),

    # Ckeditor
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')), 
    path('i18n/', include('django.conf.urls.i18n')),

    # Прямые URL для Робокассы без языкового префикса
    path('robokassa/result/', robokassa_result, name='robokassa_result_direct'),
    path('robokassa/success/', robokassa_success_direct, name='robokassa_success_direct'), 
    path('robokassa/failed/', robokassa_failed_direct, name='robokassa_failed_direct'),
]

urlpatterns += i18n_patterns(
    path("", include("hotel.urls")),
    path("booking/", include("booking.urls")),
    path("user/", include("userauths.urls")),
    path("dashboard/", include("user_dashboard.urls")),
    path("search/", include("search.urls")),
    path("legal/", include("legal.urls")),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript_catalog'),
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

