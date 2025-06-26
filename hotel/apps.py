from django.apps import AppConfig


class HotelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hotel'
    
    def ready(self):
        """Инициализация приложения и регистрация сигналов кэширования."""
        try:
            from hotel.cache_utils import register_cache_signals
            register_cache_signals()
        except ImportError:
            pass
