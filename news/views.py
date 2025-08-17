from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import Http404
from django.db.models import Q, F
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from .models import News, NewsCategory


class NewsListView(ListView):
    """Список всех новостей"""
    model = News
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10
    
    def get_queryset(self):
        """Получить опубликованные новости"""
        queryset = News.objects.filter(
            status='published'
        ).select_related('category').order_by('-published_at')
        
        # Фильтр по категории
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Поиск
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = NewsCategory.objects.filter(is_active=True)
        context['current_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class NewsDetailView(DetailView):
    """Детальный просмотр новости"""
    model = News
    template_name = 'news/news_detail.html'
    context_object_name = 'news'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Получить только опубликованные новости"""
        return News.objects.filter(status='published').select_related('category')
    
    def get_object(self, queryset=None):
        """Увеличить счетчик просмотров"""
        obj = super().get_object(queryset)
        # Увеличиваем счетчик просмотров
        News.objects.filter(pk=obj.pk).update(views_count=F('views_count') + 1)
        # Обновляем объект с новым значением счетчика
        obj.refresh_from_db(fields=['views_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем связанные новости
        context['related_news'] = News.objects.filter(
            status='published',
            category=self.object.category
        ).exclude(pk=self.object.pk)[:3]
        
        # Добавляем галерею изображений
        context['gallery'] = self.object.gallery.all().order_by('order')
        
        return context


def news_for_homepage(request):
    """Получить новости для главной страницы (используется как context processor или в шаблонах)"""
    featured_news = News.get_featured(limit=3)
    latest_news = News.get_published()[:6]
    
    return {
        'featured_news': featured_news,
        'latest_news': latest_news,
    }


# Дополнительные view-функции для AJAX запросов или API

def get_latest_news_ajax(request):
    """AJAX view для получения последних новостей"""
    from django.http import JsonResponse
    from django.template.loader import render_to_string
    
    limit = int(request.GET.get('limit', 5))
    offset = int(request.GET.get('offset', 0))
    
    news_list = News.get_published()[offset:offset + limit]
    
    html = render_to_string('news/partials/news_list_items.html', {
        'news_list': news_list
    }, request=request)
    
    return JsonResponse({
        'html': html,
        'has_more': News.get_published().count() > offset + limit
    })


def search_news_ajax(request):
    """AJAX поиск новостей"""
    from django.http import JsonResponse
    from django.template.loader import render_to_string
    
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    news_list = News.objects.filter(
        status='published'
    ).filter(
        Q(title__icontains=query) |
        Q(excerpt__icontains=query)
    ).select_related('category')[:10]
    
    results = []
    for news in news_list:
        results.append({
            'title': news.title,
            'url': news.get_absolute_url(),
            'excerpt': news.excerpt[:100] + '...' if len(news.excerpt) > 100 else news.excerpt,
            'category': news.category.name if news.category else '',
            'published_at': news.published_at.strftime('%d.%m.%Y') if news.published_at else ''
        })
    
    return JsonResponse({'results': results})


# Кэшированные views для повышения производительности

@method_decorator(cache_page(60 * 15), name='dispatch')  # Кэш на 15 минут
class CachedNewsListView(NewsListView):
    """Кэшированная версия списка новостей"""
    pass


@method_decorator(cache_page(60 * 30), name='dispatch')  # Кэш на 30 минут  
class CachedNewsDetailView(NewsDetailView):
    """Кэшированная версия детального просмотра новости"""
    pass