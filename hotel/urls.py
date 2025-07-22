from django.urls import path 
from hotel import views 

app_name = "hotel"

urlpatterns = [
    path("", views.index, name="index"),
    path("detail/<slug:slug>/", views.hotel_detail, name="detail"),
    path("detail/<slug:slug>/room-type/<slug:rt_slug>/", views.room_type_detail, name="room_type_detail"),
    path("selected_rooms/", views.selected_rooms, name="selected_rooms"),
    path("payment_method_selection/", views.payment_method_selection, name="payment_method_selection"),
    path("invoice/<booking_id>/", views.invoice, name="invoice"),
    
    # Session validation API
    path('check-session-data/', views.check_session_data, name='check_session_data'),
    
    # Real-time data API (no cache)
    path('api/selected-items-count/', views.get_selected_items_count, name='get_selected_items_count'),
    path('api/messages/', views.get_messages, name='get_messages'),
    path('api/user-auth-status/', views.get_user_auth_status, name='get_user_auth_status'),
    
    # Language Change API (без CSRF)
    path('api/change-language/', views.CustomLanguageChangeView.as_view(), name='custom_change_language'),
    
    # Robokassa Payment API
    path('api/robokassa-payment/', views.create_robokassa_payment, name='api_robokassa_payment'),
    path('api/robokassa-payment/<payment_key>/', views.create_robokassa_payment, name='api_robokassa_payment_with_key'),
    path('robokassa/result/', views.robokassa_result, name='robokassa_result'),
    path('robokassa/success/<booking_id>/', views.robokassa_success, name='robokassa_success'),
    path('robokassa/failed/<booking_id>/', views.robokassa_failed, name='robokassa_failed'),
] 