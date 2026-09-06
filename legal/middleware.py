from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from userauths.models import UserConsent
from legal.views import HotelOwnerAgreementView
from legal.utils import check_user_consent, save_user_consent, get_document_version


class AdminLegalConsentMiddleware(MiddlewareMixin):
    """
    Middleware для проверки согласия пользователя с legal agreements 
    перед доступом к админке Django
    """
    
    def process_request(self, request):
        """
        Проверяет согласие пользователя перед доступом к админке
        """
        # Проверяем, является ли запрос к админской панели
        if not request.path.startswith('/admin/'):
            return None
            
        # Исключаем статические файлы и некоторые системные пути
        if any(path in request.path for path in ['/static/', '/media/', '/jsi18n/', '/admin/jsi18n/']):
            return None
            
        # Проверяем, аутентифицирован ли пользователь
        if not request.user.is_authenticated:
            return None
            
        # Проверяем, является ли пользователь staff/admin
        if not (request.user.is_staff or request.user.is_superuser):
            return None
            
        # Исключаем некоторые системные пути админки
        excluded_paths = [
            '/admin/logout/',
            '/admin/password_change/',
            '/admin/password_change/done/',
            '/admin/login/',
            '/admin/legal-consent/',
        ]
        
        if any(request.path.startswith(path) for path in excluded_paths):
            return None
            
        # Получаем текущую версию документа hotel-owner-agreement
        document_version = get_document_version('hotel_owner_agreement')
        
        # Проверяем, есть ли у пользователя согласие с текущей версией
        try:
            consent_exists = check_user_consent(request.user, 'hotel_owner_agreement', document_version)
            
            if not consent_exists:
                # Если согласия нет, показываем форму согласия
                if request.method == 'POST' and 'legal_consent_agreed' in request.POST:
                    # Обрабатываем согласие
                    if request.POST.get('legal_consent_agreed') == 'on':
                        save_user_consent(
                            user=request.user,
                            consent_type='hotel_owner_agreement',
                            document_version=document_version,
                            user_agent=request.headers.get('user-agent', '')
                        )
                        # После сохранения согласия перенаправляем обратно
                        return redirect(request.get_full_path())
                    else:
                        # Если пользователь не согласился, показываем ошибку
                        context = {
                            'error_message': 'Для доступа к административной панели необходимо согласиться с условиями соглашения.'
                        }
                        return render(request, 'admin/legal_consent_required.html', context)
                
                # Показываем форму согласия
                # Получаем контент соглашения
                agreement_view = HotelOwnerAgreementView()
                agreement_view.request = request
                agreement_context = agreement_view.get_context_data()
                
                context = {
                    'agreement_context': agreement_context,
                    'document_version': document_version,
                    'redirect_to': request.get_full_path(),
                }
                
                return render(request, 'admin/legal_consent_required.html', context)
                
        except Exception as e:
            # Логируем ошибку, но не блокируем доступ к админке
            print(f"Error in AdminLegalConsentMiddleware: {e}")
            
        return None