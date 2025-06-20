# Generated on 2025-05-31 02:59 AM +05
from django.urls import path
from . import views

app_name = 'legal'

urlpatterns = [
    # path('test/', views.test_view, name='test'),
    path('terms-of-use/', views.TermsOfUseView.as_view(), name='terms_of_use'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('public-offer/', views.PublicOfferView.as_view(), name='public_offer'),
    path('booking-rules/', views.BookingRulesView.as_view(), name='booking_rules'),
    path('personal-data-consent/', views.PersonalDataConsentView.as_view(), name='personal_data_consent'),
    path('payment-rules/', views.PaymentRulesView.as_view(), name='payment_rules'),
    
    # Hotel Owner Documents
    path('hotel-owner-agreement/', views.HotelOwnerAgreementView.as_view(), name='hotel_owner_agreement'),
] 