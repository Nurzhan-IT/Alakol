from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    verbose_name = 'Новости'
    
    def ready(self):
        """Импорт сигналов и настроек при инициализации приложения"""
        try:
            # Импортируем настройки переводов
            import news.translation
        except ImportError:
            pass