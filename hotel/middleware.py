from django.utils import translation
from django.utils.deprecation import MiddlewareMixin


class AdminRussianLanguageMiddleware(MiddlewareMixin):
    """
    Middleware для принудительной установки русского языка в админской панели,
    независимо от языкового префикса в URL или настроек пользователя
    """
    
    def process_request(self, request):
        # Проверяем, является ли запрос к админской панели
        if request.path.startswith('/admin/'):
            # Принудительно устанавливаем русский язык для админки
            translation.activate('ru')
            request.LANGUAGE_CODE = 'ru'
            
            # Устанавливаем дополнительные заголовки для принудительного русского
            request.META['HTTP_ACCEPT_LANGUAGE'] = 'ru-RU,ru;q=0.9'
            
            # Устанавливаем атрибут для обозначения админского запроса
            request.is_admin_request = True
        
        return None
    
    def process_response(self, request, response):
        # Если это админский запрос, убеждаемся что язык остается русским
        if hasattr(request, 'is_admin_request') and request.is_admin_request:
            # Устанавливаем заголовки для принудительного русского языка
            response['Content-Language'] = 'ru'
            
            # Можно добавить JavaScript для принудительной замены текстов
            if response.get('Content-Type', '').startswith('text/html'):
                # Добавляем мета-тег для языка
                content = response.content.decode('utf-8')
                if '<head>' in content and 'lang=' not in content:
                    content = content.replace('<html', '<html lang="ru"')
                    response.content = content.encode('utf-8')
        
        return response 