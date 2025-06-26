from userauths.models import UserConsent


def check_user_consent(user, consent_type='hotel_owner_agreement', document_version='1.0'):
    """
    Проверяет, есть ли у пользователя активное согласие с указанным типом документа
    """
    if not user.is_authenticated:
        return False
        
    return UserConsent.objects.filter(
        user=user,
        consent_type=consent_type,
        document_version=document_version,
        is_active=True
    ).exists()


def save_user_consent(user, consent_type='hotel_owner_agreement', document_version='1.0', user_agent=''):
    """
    Сохраняет согласие пользователя с документом
    """
    consent, created = UserConsent.objects.get_or_create(
        user=user,
        consent_type=consent_type,
        document_version=document_version,
        defaults={
            'user_agent': user_agent,
            'is_active': True
        }
    )
    
    if not created and not consent.is_active:
        # Если согласие уже существует, но неактивно, активируем его
        consent.is_active = True
        consent.save()
    
    return consent


def get_document_version(document_type='hotel_owner_agreement'):
    """
    Получает текущую версию документа
    """
    # Для hotel_owner_agreement используем фиксированную версию
    if document_type == 'hotel_owner_agreement':
        return '1.0'
    
    # Для других типов документов можно добавить логику получения версии из базы
    return '1.0' 