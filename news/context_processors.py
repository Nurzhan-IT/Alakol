from .models import News, NewsCategory


def news_context(request):
    """
    Context processor для добавления новостей в контекст всех шаблонов
    """
    return {
        # Рекомендуемые новости для главной страницы
        'featured_news': News.get_featured(limit=3),
        
        # Последние новости
        'latest_news': News.get_published()[:5],
        
        # Активные категории новостей
        'news_categories': NewsCategory.objects.filter(is_active=True).order_by('name'),
    }
