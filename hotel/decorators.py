from django.contrib import messages
from django.shortcuts import redirect

def require_selection_data(view_func):
    """Декоратор, проверяющий наличие 'selection_data_obj' в сессии."""
    def wrapper(request, *args, **kwargs):
        if 'selection_data_obj' not in request.session or not request.session['selection_data_obj']:
            messages.warning(request, "You don't have any room selections yet!")
            return redirect("/")
        return view_func(request, *args, **kwargs)
    return wrapper