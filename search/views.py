from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Q, Min, Avg, Count, F, Exists, OuterRef, Sum, Case, When, IntegerField, Subquery, Prefetch
from django.db import connection
from django.utils.functional import cached_property
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.vary import vary_on_headers
from django.core.cache import cache
from django.conf import settings

from hotel.models import Hotel, HotelFeatures, RoomType, Room, Booking, Review
from booking.models import RoomUnavailability
from hotel.cache_utils import (
    CacheKeyGenerator, CacheHelper
)
import datetime
import logging

logger = logging.getLogger(__name__)

# Create your views here.

@method_decorator(vary_on_headers('User-Agent', 'Accept-Language'), name='dispatch')
class SearchListView(ListView):
    model = Hotel
    template_name = 'search/search_results.html'
    context_object_name = 'hotels'
    paginate_by = 10
    
    @cached_property
    def search_params(self):
        """
        Кэшируем параметры поиска для повторного использования.
        Это предотвращает повторное извлечение параметров из request.GET.
        """
        return {
            'name': self.request.GET.get('name'),
            'check_in_date': self.request.GET.get('check_in_date'),
            'check_out_date': self.request.GET.get('check_out_date'),
            'min_price': self.request.GET.get('min_price'),
            'max_price': self.request.GET.get('max_price'),
            'min_rating': self.request.GET.get('min_rating'),
            'features': self.request.GET.getlist('features'),
            'room_type': self.request.GET.get('room_type'),
            'guests': self.request.GET.get('guests'),
            'sort_by': self.request.GET.get('sort_by', 'name'),
        }
    
    @cached_property
    def date_objects(self):
        """
        Кэшируем объекты дат для повторного использования.
        """
        check_in_date = self.search_params['check_in_date']
        check_out_date = self.search_params['check_out_date']
        
        check_in_date_obj = None
        check_out_date_obj = None
        
        if check_in_date and check_out_date:
            try:
                check_in_date_obj = datetime.datetime.strptime(check_in_date, '%Y-%m-%d').date()
                check_out_date_obj = datetime.datetime.strptime(check_out_date, '%Y-%m-%d').date()
            except ValueError:
                # В случае ошибки формата используем None
                pass
        
        return check_in_date_obj, check_out_date_obj
    
    def get_unavailable_room_ids(self):
        """
        Получаем ID недоступных номеров одним запросом.
        """
        check_in_date_obj, check_out_date_obj = self.date_objects
        
        if not (check_in_date_obj and check_out_date_obj):
            return []
        
        # Получаем ID всех забронированных номеров на указанные даты
        booked_room_ids = list(Booking.objects.filter(
            Q(check_in_date__lt=check_out_date_obj, check_out_date__gt=check_in_date_obj),
            is_active=True,
            payment_status__in=["paid", "processing", "pending"]
        ).values_list('room__id', flat=True).distinct())
        
        # Получаем ID номеров, которые отмечены как недоступные в RoomUnavailability
        unavailable_room_ids = list(RoomUnavailability.objects.filter(
            Q(start_date__lt=check_out_date_obj, end_date__gt=check_in_date_obj)
        ).values_list('room__id', flat=True).distinct())
        
        # Объединяем оба списка ID недоступных номеров и удаляем дубликаты
        return list(set(booked_room_ids + unavailable_room_ids))
    
    def get_queryset(self):
        """Получение результатов поиска с кэшированием."""
        # Логирование для отслеживания производительности
        logger.debug("Starting search query execution")
        
        # Получаем параметры поиска из кэшированного свойства
        params = self.search_params
        check_in_date_obj, check_out_date_obj = self.date_objects
        
        # Генерируем ключ кэша на основе параметров поиска
        search_cache_key = CacheKeyGenerator.search_results(params)
        
        def execute_search_query():
            # Базовый запрос с фильтром статуса
            queryset = Hotel.objects.filter(status="Live").distinct()
            
            # Фильтрация отелей по датам активности
            if check_in_date_obj and check_out_date_obj:
                queryset = queryset.filter(
                    Q(start_date__isnull=True) | Q(start_date__lte=check_in_date_obj)
                ).filter(
                    Q(end_date__isnull=True) | Q(end_date__gte=check_out_date_obj)
                )
            
            # Получаем ID недоступных номеров
            all_unavailable_room_ids = self.get_unavailable_room_ids()
            
            # Базовая аннотация для получения мин. цены и среднего рейтинга
            queryset = queryset.annotate(
                min_price=Min('roomtype__price'),  # Оставляем для базовой цены
                avg_rating=Avg('reviews__rating', filter=Q(reviews__active=True)),
                # Подсчет только доступных и не забронированных номеров
                rooms_count=Count(
                    'roomtype__room', 
                    filter=Q(roomtype__room__is_available=True) & ~Q(roomtype__room__id__in=all_unavailable_room_ids), 
                    distinct=True
                ),
                # Рассчитываем общую вместимость для доступных и не забронированных номеров
                total_capacity=Sum(
                    Case(
                        When(
                            Q(roomtype__room__is_available=True) & ~Q(roomtype__room__id__in=all_unavailable_room_ids), 
                            then=F('roomtype__room_capacity')
                        ),
                        default=0,
                        output_field=IntegerField()
                    )
                )
            )
            
            # Поиск по названию отеля
            if params['name']:
                queryset = queryset.filter(name__icontains=params['name'])
            
            # Фильтрация по диапазону цен
            if params['min_price']:
                queryset = queryset.filter(roomtype__price__gte=params['min_price'])
            if params['max_price']:
                queryset = queryset.filter(roomtype__price__lte=params['max_price'])
            
            # Фильтрация по минимальному рейтингу
            if params['min_rating']:
                queryset = queryset.filter(avg_rating__gte=params['min_rating'])
            
            # Фильтрация по типу номера
            if params['room_type']:
                queryset = queryset.filter(roomtype__type=params['room_type'])
            
            # Фильтрация по количеству гостей
            if params['guests']:
                queryset = queryset.filter(total_capacity__gte=params['guests'])
            
            # Фильтрация по удобствам отеля
            if params['features']:
                for feature in params['features']:
                    queryset = queryset.filter(hotelfeatures__name=feature)
            
            # Фильтрация по датам (наличие свободных номеров)
            if check_in_date_obj and check_out_date_obj and all_unavailable_room_ids:
                # Подзапрос для отелей с доступными номерами
                available_rooms = Room.objects.filter(
                    hotel=OuterRef('pk'),
                    is_available=True
                ).exclude(id__in=all_unavailable_room_ids)
                
                queryset = queryset.filter(Exists(available_rooms))
            
            # Сортировка результатов
            sort_by = params['sort_by']
            if sort_by == 'price_asc':
                queryset = queryset.order_by('min_price')
            elif sort_by == 'price_desc':
                queryset = queryset.order_by('-min_price')
            elif sort_by == 'rating':
                queryset = queryset.order_by('-avg_rating')
            elif sort_by == 'popularity':
                queryset = queryset.order_by('-views')
            else:
                queryset = queryset.order_by('name')
            
            # Оптимизация запросов с предварительной загрузкой связанных данных
            optimized_queryset = queryset.select_related('user').prefetch_related(
                Prefetch('hotelfeatures_set', queryset=HotelFeatures.objects.all()),
                Prefetch('roomtype_set', queryset=RoomType.objects.prefetch_related(
                    Prefetch('room_set', queryset=Room.objects.filter(is_available=True))
                )),
                Prefetch('reviews', queryset=Review.objects.filter(active=True).select_related('user'))
            )
            
            # Логирование для отслеживания производительности
            logger.debug(f"Generated SQL: {str(optimized_queryset.query)}")
            logger.debug(f"Search query executed with {len(connection.queries)} database queries")
            
            return list(optimized_queryset)  # Преобразуем в список для кэширования
        
        # Используем кэш для результатов поиска
        cached_results = CacheHelper.get_or_set_complex(
            search_cache_key,
            execute_search_query,
            timeout=settings.CACHE_TTL['search_results']
        )
        
        # Возвращаем queryset для совместимости с ListView
        if cached_results:
            # Создаем queryset из кэшированных результатов
            cached_ids = [hotel.id for hotel in cached_results]
            queryset = Hotel.objects.filter(id__in=cached_ids)
            
            # Восстанавливаем порядок из кэша
            ordering_map = {hotel.id: index for index, hotel in enumerate(cached_results)}
            queryset = sorted(queryset, key=lambda x: ordering_map[x.id])
            
            return queryset
        else:
            return Hotel.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем параметры запроса в контекст для формы поиска
        context['search_params'] = self.search_params
        
        # Получаем даты для расчета динамических цен в шаблоне
        check_in_date_obj, check_out_date_obj = self.date_objects
        
        if check_in_date_obj and check_out_date_obj:
            context['check_in_date_obj'] = check_in_date_obj
            context['check_out_date_obj'] = check_out_date_obj
        else:
            # Если даты не указаны, используем текущую дату и завтра
            context['check_in_date_obj'] = datetime.datetime.now().date()
            context['check_out_date_obj'] = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
        
        # Кэшируем статические данные для фильтров поиска
        def get_all_features():
            return list(HotelFeatures.objects.values_list('name', flat=True).distinct())
        
        def get_room_types():
            return list(RoomType.objects.values_list('type', flat=True).distinct())
        
        all_features = CacheHelper.get_or_set_complex(
            'search_filters:all_features',
            get_all_features,
            timeout=settings.CACHE_TTL['features_and_amenities']
        )
        
        room_types = CacheHelper.get_or_set_complex(
            'search_filters:room_types', 
            get_room_types,
            timeout=settings.CACHE_TTL['features_and_amenities']
        )
            
        context['all_features'] = all_features
        context['room_types'] = room_types
        
        # Добавляем количество найденных результатов
        queryset = self.get_queryset()
        if isinstance(queryset, list):
            context['results_count'] = len(queryset)
        else:
            context['results_count'] = queryset.count()
        
        # Логирование для отслеживания производительности
        logger.debug(f"Context data prepared with {len(connection.queries)} total database queries")
        
        return context
