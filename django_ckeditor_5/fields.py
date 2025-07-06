# Фиктивная замена для django_ckeditor_5.fields
from django.db import models

class CKEditor5Field(models.TextField):
    """
    Фиктивная замена для CKEditor5Field для обратной совместимости с миграциями
    """
    def __init__(self, *args, **kwargs):
        # Убираем специфичные для CKEditor параметры
        kwargs.pop('config_name', None)
        super().__init__(*args, **kwargs)