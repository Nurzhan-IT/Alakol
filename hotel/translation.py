from modeltranslation.translator import register, TranslationOptions
from .models import Hotel, HotelFAQs, RoomTypeDescription

@register(Hotel)
class HotelTranslationOptions(TranslationOptions):
    fields = ('name', 'description')  # Указываем поля для перевода

@register(HotelFAQs)
class HotelFAQsTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')  # Указываем поля для перевода

@register(RoomTypeDescription)
class RoomTypeDescriptionTranslationOptions(TranslationOptions):
    fields = ['description']