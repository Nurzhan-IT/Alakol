from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    # Список новостей
    path('', views.NewsListView.as_view(), name='news_list'),
    
    # Детальный просмотр новости
    path('<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),
    
    # AJAX endpoints
    path('ajax/latest/', views.get_latest_news_ajax, name='latest_ajax'),
    path('ajax/search/', views.search_news_ajax, name='search_ajax'),
    
    # Кэшированные версии (опционально)
    path('cached/', views.CachedNewsListView.as_view(), name='cached_news_list'),
    path('cached/<slug:slug>/', views.CachedNewsDetailView.as_view(), name='cached_news_detail'),
]
