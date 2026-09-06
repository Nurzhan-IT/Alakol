# Generated on 2025-06-21 01:55 AM +05
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils.translation import get_language
from .models import DocumentView
from django.http import HttpResponse


@method_decorator(cache_page(60 * 60 * 24), name='dispatch')  # Cache for 24 hours
class LegalDocumentView(TemplateView):
    """Base class for legal documents"""
    document_type = None
    base_template_name = None  # Базовое имя шаблона без языкового префикса
    
    def get_template_names(self):
        """Динамически выбираем шаблон в зависимости от активного языка"""
        if not self.base_template_name:
            return super().get_template_names()
        
        current_language = get_language()
        
        # Определяем папку в зависимости от языка
        if current_language == 'ru':
            template_path = f'legal_ru/{self.base_template_name}'
        elif current_language == 'kk':
            template_path = f'legal_kk/{self.base_template_name}'
        else:
            # Для английского и всех остальных языков используем стандартную папку
            template_path = f'legal/{self.base_template_name}'
        
        return [template_path]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'document_version': '1.0',
            'last_updated': '2025-06-19',
            'generation_time': '2025-06-19 04:45 AM +05',
            'company_info': {
                'name': '[ORGANIZATION NAME]',
                'bin': '[BIN/IIN]',
                'address': '[LEGAL ADDRESS]',
                'phone': '[PHONE]',
                'email': '[EMAIL]'
            }
        })
        return context
    
    def get(self, request, *args, **kwargs):
        # Track document view with error handling
        if self.document_type:
            try:
                DocumentView.objects.create(
                    document_type=self.document_type,
                    user=request.user if request.user.is_authenticated else None,
                    user_agent=request.headers.get('user-agent', '')
                )
            except Exception as e:
                # Log the error but don't break the page
                print(f"Error logging document view: {e}")
        
        return super().get(request, *args, **kwargs)


def test_view(request):
    return HttpResponse("Legal app is working!")


class TermsOfUseView(LegalDocumentView):
    base_template_name = 'terms_of_use.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'document_version': '1.0',
            'last_updated': '2025-06-19',
            'generation_time': '2025-06-19 04:45 AM +05',
        })
        return context


class PrivacyPolicyView(LegalDocumentView):
    base_template_name = 'privacy_policy.html'


class PublicOfferView(LegalDocumentView):
    base_template_name = 'public_offer.html'


class BookingRulesView(LegalDocumentView):
    base_template_name = 'booking_rules.html'


class PersonalDataConsentView(LegalDocumentView):
    base_template_name = 'personal_data_consent.html'


class PaymentRulesView(LegalDocumentView):
    base_template_name = 'payment_rules.html'


# ===== HOTEL OWNER DOCUMENTS =====

class HotelOwnerAgreementView(LegalDocumentView):
    """Соглашение с владельцами отелей"""
    base_template_name = 'hotel_owner_docs/hotel_owner_agreement.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'document_version': '1.0',
            'last_updated': '2025-06-19',
            'generation_time': '2025-06-19 04:45 AM +05',
        })
        return context


