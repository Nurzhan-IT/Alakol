from django import template

register = template.Library()

@register.filter
def price_format(value):
    try:
        # Преобразуем значение в число и округляем до целого
        value = float(value)  # Преобразуем в float для обработки Decimal или строки
        integer_part = int(round(value))  # Округляем до целого числа
        
        # Преобразуем в строку
        integer_part = str(integer_part)
        
        # Разбиваем на группы по 3 цифры с конца
        formatted_integer = ""
        for i in range(len(integer_part) - 1, -1, -1):
            if i != len(integer_part) - 1 and (len(integer_part) - i - 1) % 3 == 0:
                formatted_integer = " " + formatted_integer
            formatted_integer = integer_part[i] + formatted_integer
        
        return formatted_integer or "0"
    except (ValueError, AttributeError, TypeError):
        return value