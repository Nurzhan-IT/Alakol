from hotel.models import Notification

def default(request):
    # total_selected_items УБРАНО из context processor'а чтобы предотвратить кэширование
    # пользовательских данных. Теперь это значение загружается динамически через AJAX
    
    try:
        # Уведомления загружаются напрямую из БД без кэширования для обеспечения данных реального времени
        noti = Notification.objects.filter(user=request.user, seen=False)
    except:
        noti = None

    return {
        # "total_selected_items": удалено для предотвращения кэширования пользовательских данных
        "noti": noti,
    }

def admin_russian_language(request):
    """
    Context processor для принудительной установки русского языка в админке
    """
    context = {}
    
    # Если это запрос к админке, принудительно устанавливаем русский язык
    if request.path.startswith('/admin/'):
        from django.utils import translation
        translation.activate('ru')
        context['LANGUAGE_CODE'] = 'ru'
        context['ADMIN_FORCE_RUSSIAN'] = True
    
    return context