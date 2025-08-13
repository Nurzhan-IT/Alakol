"""
Специальные сериализаторы для кэширования Django объектов в JSON-совместимом формате.
"""

from django.core import serializers
from django.db import models
import json
from datetime import datetime, date
from decimal import Decimal


class DjangoObjectEncoder(json.JSONEncoder):
    """JSON энкодер для Django объектов."""
    
    def default(self, obj):
        if isinstance(obj, models.Model):
            return {
                '_model': f"{obj._meta.app_label}.{obj._meta.model_name}",
                '_pk': obj.pk,
                **self._serialize_model_fields(obj)
            }
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)
    
    def _serialize_model_fields(self, obj):
        """Сериализует поля модели в словарь."""
        data = {}
        for field in obj._meta.fields:
            try:
                value = getattr(obj, field.name)
                if isinstance(value, (datetime, date)):
                    data[field.name] = value.isoformat() if value else None
                elif isinstance(value, Decimal):
                    data[field.name] = float(value) if value else None
                elif isinstance(value, models.Model):
                    # Для связанных объектов сохраняем только ID
                    data[field.name + '_id'] = value.pk if value else None
                else:
                    data[field.name] = value
            except Exception:
                # Пропускаем поля, которые не удается сериализовать
                continue
        return data


def serialize_for_cache(obj):
    """
    Сериализует объект для кэширования в JSON-совместимом формате.
    """
    if isinstance(obj, models.QuerySet):
        return [serialize_for_cache(item) for item in obj]
    elif isinstance(obj, list):
        return [serialize_for_cache(item) for item in obj]
    elif isinstance(obj, models.Model):
        return {
            '_model': f"{obj._meta.app_label}.{obj._meta.model_name}",
            '_pk': obj.pk,
            '_fields': DjangoObjectEncoder()._serialize_model_fields(obj)
        }
    elif isinstance(obj, dict):
        return {key: serialize_for_cache(value) for key, value in obj.items()}
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj


def deserialize_from_cache(data):
    """
    Десериализует данные из кэша обратно в Django объекты.
    """
    if isinstance(data, dict) and '_model' in data:
        # Это сериализованная Django модель
        app_label, model_name = data['_model'].split('.')
        from django.apps import apps
        
        try:
            Model = apps.get_model(app_label, model_name)
            # Создаем объект с полями из кэша
            obj = Model()
            for field_name, value in data['_fields'].items():
                if hasattr(obj, field_name):
                    setattr(obj, field_name, value)
            obj.pk = data['_pk']
            return obj
        except Exception:
            return data
    elif isinstance(data, list):
        return [deserialize_from_cache(item) for item in data]
    elif isinstance(data, dict):
        return {key: deserialize_from_cache(value) for key, value in data.items()}
    else:
        return data


class SmartCacheSerializer:
    """
    Умный сериализатор который автоматически выбирает лучший способ кэширования.
    """
    
    @staticmethod
    def serialize(obj):
        """Сериализует объект для кэширования."""
        return serialize_for_cache(obj)
    
    @staticmethod
    def deserialize(data):
        """Десериализует объект из кэша."""
        return deserialize_from_cache(data)
    
    @staticmethod
    def _get_image_url(image_field):
        """Безопасно получает URL изображения."""
        if image_field:
            try:
                return image_field.url
            except ValueError:
                return None
        return None
    
    @staticmethod 
    def serialize_hotel_list(hotels):
        """Специализированная сериализация для списка отелей."""
        result = []
        for hotel in hotels:
            hotel_data = {
                'id': hotel.id,
                'name': hotel.name,
                'slug': hotel.slug,
                'description': hotel.description,
                'image': SmartCacheSerializer._get_image_url(hotel.image),
                'address': hotel.address,
                'views': hotel.views,
                'featured': hotel.featured,
                'status': hotel.status,
                'date': hotel.date.isoformat() if hotel.date else None,
                # Предварительно загруженные связанные данные
                'features': [
                    {
                        'id': f.id,
                        'name': f.name,
                        'icon': f.icon
                    } for f in hotel.hotelfeatures_set.all()
                ] if hasattr(hotel, 'hotelfeatures_set') else [],
                'room_types': [
                    {
                        'id': rt.id,
                        'type': rt.type,
                        'price': float(rt.price),
                        'slug': rt.slug
                    } for rt in hotel.roomtype_set.all()
                ] if hasattr(hotel, 'roomtype_set') else []
            }
            result.append(hotel_data)
        return result
    
    @staticmethod
    def serialize_hotel_detail(hotel):
        """Специализированная сериализация для деталей отеля."""
        return {
            'id': hotel.id,
            'name': hotel.name,
            'slug': hotel.slug,
            'description': hotel.description,
            'image': SmartCacheSerializer._get_image_url(hotel.image),
            'address': hotel.address,
            'mobile': hotel.mobile,
            'email': hotel.email,
            'views': hotel.views,
            'featured': hotel.featured,
            'status': hotel.status,
            'check_in_time': hotel.check_in_time.isoformat() if hotel.check_in_time else None,
            'check_out_time': hotel.check_out_time.isoformat() if hotel.check_out_time else None,
            # start_date / end_date теперь строки формата ДД.ММ
            'start_date': hotel.start_date if hotel.start_date else None,
            'end_date': hotel.end_date if hotel.end_date else None,
            'date': hotel.date.isoformat() if hotel.date else None,
        } 