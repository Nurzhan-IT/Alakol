# Generated on 2025-05-31 02:59 AM +05
from .models import UserConsent


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def save_user_consent(user, consent_type, request, document_version='1.0'):
    """Save user consent"""
    UserConsent.objects.update_or_create(
        user=user,
        consent_type=consent_type,
        document_version=document_version,
        defaults={
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'is_active': True,
            'withdrawn_at': None
        }
    ) 