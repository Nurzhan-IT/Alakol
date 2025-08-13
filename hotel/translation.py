from modeltranslation.translator import register, TranslationOptions
from .models import Hotel, HotelFAQs, RoomType, RoomTypeComplete, RoomTypeFeaturesDetailed, HotelFeatures, RoomTypeFeatures

@register(Hotel)
class HotelTranslationOptions(TranslationOptions):
    fields = ('name', 'description')  # Указываем поля для перевода

@register(HotelFAQs)
class HotelFAQsTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')  # Указываем поля для перевода

@register(RoomType)
class RoomTypeTranslationOptions(TranslationOptions):
    fields = ['description', 'type']

@register(RoomTypeComplete)
class RoomTypeCompleteTranslationOptions(TranslationOptions):
    fields = ['description', 'type']

@register(RoomTypeFeaturesDetailed)
class RoomTypeFeaturesDetailedTranslationOptions(TranslationOptions):
    fields = ('text',)  # Указываем поле для перевода

@register(HotelFeatures)
class HotelFeaturesTranslationOptions(TranslationOptions):
    fields = ('name',)  # Указываем поле для перевода

@register(RoomTypeFeatures)
class RoomTypeFeaturesTranslationOptions(TranslationOptions):
    fields = ('name',)  # Указываем поле для перевода