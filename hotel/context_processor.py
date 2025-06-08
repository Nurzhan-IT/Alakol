from hotel.models import Notification

def default(request):
    if 'selection_data_obj' in request.session:
        total_selected_items = len(request.session['selection_data_obj'])
    else:
        total_selected_items = 0
    
    try:
        noti = Notification.objects.filter(user=request.user, seen=False)
    except:
        noti = None

    return {
        "total_selected_items": total_selected_items,
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