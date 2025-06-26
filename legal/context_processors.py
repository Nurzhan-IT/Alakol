# Generated on 2025-05-31 02:59 AM +05
def legal_documents(request):
    """Context processor for legal documents"""
    return {
        'legal_documents': {
            'terms_of_use_url': 'legal:terms_of_use',
            'privacy_policy_url': 'legal:privacy_policy',
            'public_offer_url': 'legal:public_offer',
            'booking_rules_url': 'legal:booking_rules',
            'personal_data_consent_url': 'legal:personal_data_consent',
            'payment_rules_url': 'legal:payment_rules',
        }
    } 