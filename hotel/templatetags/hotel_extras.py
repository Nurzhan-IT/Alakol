from django import template
from django.utils.formats import number_format
from datetime import datetime, time
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Фильтр для получения значения из словаря по ключу в шаблоне Django.
    Пример использования: {{ mydict|get_item:key }}
    """
    if dictionary is None:
        return None
    
    try:
        return dictionary.get(key)
    except (KeyError, AttributeError, TypeError):
        return None 
    



@register.filter
def to_decimal_dot(value):
    try:
        return number_format(value, decimal_pos=1, use_l10n=False)
    except (TypeError, ValueError):
        return value

@register.filter
def format_time(value):
    """
    Форматирует время в 24-часовом формате H:i (например, 14:30)
    независимо от локали
    """
    if not value:
        return value
    
    if isinstance(value, str):
        try:
            # Если это строка, парсим её
            value = datetime.strptime(value, '%H:%M:%S').time()
        except ValueError:
            try:
                value = datetime.strptime(value, '%H:%M').time()
            except ValueError:
                return value
    
    if isinstance(value, time):
        return value.strftime('%H:%M')
    elif isinstance(value, datetime):
        return value.strftime('%H:%M')
    
    return value