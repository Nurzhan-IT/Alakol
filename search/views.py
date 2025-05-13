from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Q, Min, Avg, Count, F, Exists, OuterRef, Sum, Case, When, IntegerField, Subquery
from hotel.models import Hotel, HotelFeatures, RoomType, Room, Booking, Review
from booking.models import RoomUnavailability
import datetime

# Create your views here.

class SearchListView(ListView):
    model = Hotel
    template_name = 'search/search_results.html'
    context_object_name = 'hotels'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Hotel.objects.filter(status="Live").distinct()
        
        # Получение параметров поиска из GET запроса
        name = self.request.GET.get('name')
        check_in_date = self.request.GET.get('check_in_date')
        check_out_date = self.request.GET.get('check_out_date')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        min_rating = self.request.GET.get('min_rating')
        features = self.request.GET.getlist('features')
        room_type = self.request.GET.get('room_type')
        guests = self.request.GET.get('guests')
        sort_by = self.request.GET.get('sort_by', 'name')
        
        # Конвертируем даты для проверки динамических цен
        check_in_date_obj = None
        check_out_date_obj = None
        if check_in_date and check_out_date:
            try:
                check_in_date_obj = datetime.datetime.strptime(check_in_date, '%Y-%m-%d').date()
                check_out_date_obj = datetime.datetime.strptime(check_out_date, '%Y-%m-%d').date()
            except ValueError:
                # В случае ошибки формата используем None
                pass
        
        # Подготовка запроса для получения ID забронированных номеров
        booked_room_ids = []
        if check_in_date_obj and check_out_date_obj:
            # Получаем ID всех забронированных номеров на указанные даты
            booked_room_ids = Booking.objects.filter(
                Q(check_in_date__lt=check_out_date_obj, check_out_date__gt=check_in_date_obj),
                is_active=True,
                payment_status__in=["paid", "processing", "pending"]
            ).values_list('room__id', flat=True).distinct()
            
            # Получаем ID номеров, которые отмечены как недоступные в RoomUnavailability
            unavailable_room_ids = RoomUnavailability.objects.filter(
                Q(start_date__lt=check_out_date_obj, end_date__gt=check_in_date_obj)
            ).values_list('room__id', flat=True).distinct()
            
            # Объединяем оба списка ID недоступных номеров
            all_unavailable_room_ids = list(booked_room_ids) + list(unavailable_room_ids)
        else:
            all_unavailable_room_ids = []
        
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
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        # Фильтрация по диапазону цен
        # Примечание: для точного фильтра по динамическим ценам потребуется более сложная логика
        # Сейчас используем базовую цену как приблизительный фильтр
        if min_price:
            queryset = queryset.filter(roomtype__price__gte=min_price)
        if max_price:
            queryset = queryset.filter(roomtype__price__lte=max_price)
        
        # Фильтрация по минимальному рейтингу
        if min_rating:
            queryset = queryset.filter(avg_rating__gte=min_rating)
        
        # Фильтрация по типу номера
        if room_type:
            queryset = queryset.filter(roomtype__type=room_type)
        
        # Фильтрация по количеству гостей (используя общую вместимость)
        if guests:
            queryset = queryset.filter(total_capacity__gte=guests)
        
        # Фильтрация по удобствам отеля
        if features:
            for feature in features:
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
        
        # Оптимизация запросов
        return queryset.select_related('user').prefetch_related(
            'hotelfeatures_set', 
            'roomtype_set', 
            'roomtype_set__room_set',
            'reviews'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем параметры запроса в контекст для формы поиска
        context['search_params'] = {
            'name': self.request.GET.get('name', ''),
            'check_in_date': self.request.GET.get('check_in_date', ''),
            'check_out_date': self.request.GET.get('check_out_date', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'min_rating': self.request.GET.get('min_rating', ''),
            'features': self.request.GET.getlist('features'),
            'room_type': self.request.GET.get('room_type', ''),
            'guests': self.request.GET.get('guests', ''),
            'sort_by': self.request.GET.get('sort_by', 'name'),
        }
        
        # Получаем даты для расчета динамических цен в шаблоне
        check_in_date = self.request.GET.get('check_in_date')
        check_out_date = self.request.GET.get('check_out_date')
        
        if check_in_date and check_out_date:
            try:
                context['check_in_date_obj'] = datetime.datetime.strptime(check_in_date, '%Y-%m-%d').date()
                context['check_out_date_obj'] = datetime.datetime.strptime(check_out_date, '%Y-%m-%d').date()
            except ValueError:
                # В случае ошибки формата используем текущую дату
                context['check_in_date_obj'] = datetime.datetime.now().date()
                context['check_out_date_obj'] = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
        else:
            # Если даты не указаны, используем текущую дату и завтра
            context['check_in_date_obj'] = datetime.datetime.now().date()
            context['check_out_date_obj'] = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
        
        # Добавляем список всех удобств и типов номеров для фильтрации
        context['all_features'] = HotelFeatures.objects.values_list('name', flat=True).distinct()
        context['room_types'] = RoomType.objects.values_list('type', flat=True).distinct()
        
        return context
