# Generated on 2025-05-31 02:59 AM +05
from django.utils import timezone
from .models import UserConsent


def save_user_consent(user, consent_type, request, document_version='1.0'):
    """
    Сохраняет согласие пользователя с юридическими документами
    
    Args:
        user: Пользователь
        consent_type: Тип согласия (из CONSENT_TYPES)
        request: HTTP запрос для получения User-Agent
        document_version: Версия документа
    """
    user_agent = request.headers.get('user-agent', '') if request else ''
    
    consent, created = UserConsent.objects.update_or_create(
        user=user,
        consent_type=consent_type,
        document_version=document_version,
        defaults={
            'user_agent': user_agent,
            'is_active': True,
            'withdrawn_at': None,
            'given_at': timezone.now()
        }
    )
    return consent


def save_registration_consents(user, request, consent_data):
    """
    Сохраняет все согласия при регистрации пользователя
    
    Args:
        user: Пользователь
        request: HTTP запрос
        consent_data: Словарь с данными о согласиях из формы
    """
    consent_mapping = {
        'terms_consent': 'terms_of_use',
        'privacy_consent': 'privacy_policy', 
        'personal_data_consent': 'personal_data',
        'marketing_consent': 'marketing'
    }
    
    saved_consents = []
    for form_field, consent_type in consent_mapping.items():
        if consent_data.get(form_field):
            consent = save_user_consent(user, consent_type, request)
            saved_consents.append(consent)
    
    return saved_consents


def save_booking_consents(booking, request, consent_data):
    """
    Сохраняет согласия при создании бронирования
    
    Args:
        booking: Объект бронирования
        request: HTTP запрос
        consent_data: Словарь с данными о согласиях из формы
    """
    consent_mapping = {
        'public_offer_consent': 'public_offer',
        'booking_rules_consent': 'booking_terms',
        'payment_rules_consent': 'payment_terms'
    }
    
    # Создаем структуру для сохранения в JSON
    legal_agreements = {
        'consents': {},
        'timestamp': timezone.now().isoformat(),
        'user_agent': request.headers.get('user-agent', '') if request else ''
    }
    
    for form_field, consent_type in consent_mapping.items():
        if consent_data.get(form_field):
            legal_agreements['consents'][consent_type] = {
                'agreed': True,
                'document_version': '1.0',
                'timestamp': timezone.now().isoformat()
            }
    
    # Сохраняем в поле legal_agreements модели Booking
    booking.legal_agreements = legal_agreements
    booking.save(update_fields=['legal_agreements'])
    
    return legal_agreements