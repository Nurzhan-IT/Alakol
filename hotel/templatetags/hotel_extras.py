from django import template
from django.utils.formats import number_format
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