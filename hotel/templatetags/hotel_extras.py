from django import template

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