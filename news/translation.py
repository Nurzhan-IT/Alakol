# Временно отключено до настройки многоязычности
"""
from modeltranslation.translator import translator, TranslationOptions
from .models import News, NewsCategory


class NewsCategoryTranslationOptions(TranslationOptions):
    Настройки перевода для категорий новостей
    fields = ('name', 'description')


class NewsTranslationOptions(TranslationOptions):
    Настройки перевода для новостей
    fields = ('title', 'excerpt', 'content', 'meta_title', 'meta_description')


# Регистрация моделей для перевода
translator.register(NewsCategory, NewsCategoryTranslationOptions)
translator.register(News, NewsTranslationOptions)
"""
