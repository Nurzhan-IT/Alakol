# Generated on 2025-05-31 02:59 AM +05
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import DocumentView
from django.http import HttpResponse


@method_decorator(cache_page(60 * 60 * 24), name='dispatch')  # Cache for 24 hours
class LegalDocumentView(TemplateView):
    """Base class for legal documents"""
    document_type = None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'document_version': '1.0',
            'last_updated': '2025-05-31',
            'generation_time': '2025-05-31 02:59 AM +05',
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
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except Exception as e:
                # Log the error but don't break the page
                print(f"Error logging document view: {e}")
        
        return super().get(request, *args, **kwargs)


def test_view(request):
    return HttpResponse("Legal app is working!")


class TermsOfUseView(TemplateView):
    template_name = 'legal/terms_of_use.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'document_version': '1.0',
            'last_updated': '2025-05-31',
            'generation_time': '2025-05-31 02:59 AM +05',
        })
        return context


class PrivacyPolicyView(TemplateView):
    template_name = 'legal/privacy_policy.html'


class PublicOfferView(TemplateView):
    template_name = 'legal/public_offer.html'


class BookingRulesView(TemplateView):
    template_name = 'legal/booking_rules.html'


class PersonalDataConsentView(TemplateView):
    template_name = 'legal/personal_data_consent.html'


class PaymentRulesView(TemplateView):
    template_name = 'legal/payment_rules.html'


# ===== HOTEL OWNER DOCUMENTS =====

class HotelTaxObligationsView(TemplateView):
    """Налоговые обязательства владельцев отелей"""
    template_name = 'legal/hotel_owner_docs/hotel_tax_obligations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'document_version': '1.0',
            'last_updated': '2025-06-03',
            'generation_time': '2025-06-03 06:24 PM +05',
        })
        return context


class HotelIntegrationRequirementsView(TemplateView):
    """Технические требования для интеграции отелей"""
    template_name = 'legal/hotel_owner_docs/hotel_integration_requirements.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'document_version': '1.0',
            'last_updated': '2025-06-03',
            'generation_time': '2025-06-03 06:24 PM +05',
        })
        return context


class HotelOwnerAgreementView(TemplateView):
    """Соглашение с владельцами отелей"""
    template_name = 'legal/hotel_owner_docs/hotel_owner_agreement.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'document_version': '1.0',
            'last_updated': '2025-06-03',
            'generation_time': '2025-06-03 06:24 PM +05',
        })
        return context
