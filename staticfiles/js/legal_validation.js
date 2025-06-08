/**
 * Legal Validation JavaScript for HMS Alakol
 * Generated on 2025-05-31 04:53 AM +05
 * For Django 4.2.2 HMS (Hotel Management System) - Alakol Region
 */

class LegalValidation {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupFormValidation();
        this.trackLegalDocumentViews();
    }

    bindEvents() {
        // Валидация чекбоксов в реальном времени
        document.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox' && e.target.closest('.legal-checkbox')) {
                this.validateCheckbox(e.target);
            }
        });

        // Валидация перед отправкой формы
        document.addEventListener('submit', (e) => {
            if (this.hasLegalCheckboxes(e.target)) {
                if (!this.validateForm(e.target)) {
                    e.preventDefault();
                    this.showValidationError();
                }
            }
        });

        // Открытие ссылок на юридические документы в новой вкладке
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('legal-link')) {
                e.target.setAttribute('target', '_blank');
                e.target.setAttribute('rel', 'noopener noreferrer');
            }
        });
    }

    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            if (this.hasLegalCheckboxes(form)) {
                this.enhanceForm(form);
            }
        });
    }

    hasLegalCheckboxes(form) {
        return form.querySelector('.legal-checkbox input[type="checkbox"]') !== null;
    }

    enhanceForm(form) {
        // Добавляем индикатор загрузки
        form.addEventListener('submit', () => {
            form.classList.add('legal-form-submitting');
        });

        // Создаем контейнер для ошибок валидации
        if (!form.querySelector('.legal-validation-error')) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'legal-validation-error';
            errorDiv.innerHTML = this.getErrorMessage();
            
            const submitButton = form.querySelector('input[type="submit"], button[type="submit"]');
            if (submitButton) {
                submitButton.parentNode.insertBefore(errorDiv, submitButton);
            }
        }
    }

    validateCheckbox(checkbox) {
        const checkboxContainer = checkbox.closest('.legal-checkbox');
        const isRequired = checkbox.hasAttribute('required');
        const isChecked = checkbox.checked;

        // Удаляем предыдущие классы состояния
        checkboxContainer.classList.remove('error', 'validated');

        if (isRequired && !isChecked) {
            checkboxContainer.classList.add('error');
            return false;
        } else if (isChecked) {
            checkboxContainer.classList.add('validated');
            return true;
        }

        return true;
    }

    validateForm(form) {
        const requiredCheckboxes = form.querySelectorAll('.legal-checkbox input[type="checkbox"][required]');
        let isValid = true;

        requiredCheckboxes.forEach(checkbox => {
            if (!this.validateCheckbox(checkbox)) {
                isValid = false;
            }
        });

        return isValid;
    }

    showValidationError() {
        const errorDiv = document.querySelector('.legal-validation-error');
        if (errorDiv) {
            errorDiv.classList.add('show');
            
            // Прокручиваем к первому невалидному чекбоксу
            const firstError = document.querySelector('.legal-checkbox.error');
            if (firstError) {
                firstError.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
            }

            // Автоматически скрываем ошибку через 5 секунд
            setTimeout(() => {
                errorDiv.classList.remove('show');
            }, 5000);
        }
    }

    getErrorMessage() {
        // Определяем язык страницы для мультиязычной поддержки
        const lang = document.documentElement.lang || 'en';
        
        const messages = {
            'en': 'Please accept all required legal documents to continue.',
            'ru': 'Пожалуйста, примите все обязательные юридические документы для продолжения.',
            'kk': 'Жалғастыру үшін барлық міндетті заңнамалық құжаттарды қабылдаңыз.'
        };

        return messages[lang] || messages['en'];
    }

    trackLegalDocumentViews() {
        // Отслеживание кликов по ссылкам на юридические документы
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('legal-link')) {
                const documentType = this.getDocumentTypeFromUrl(e.target.href);
                this.logDocumentView(documentType);
            }
        });
    }

    getDocumentTypeFromUrl(url) {
        const documentTypes = {
            'terms-of-use': 'terms_of_use',
            'privacy-policy': 'privacy_policy',
            'public-offer': 'public_offer',
            'booking-rules': 'booking_rules',
            'personal-data-consent': 'personal_data_consent',
            'payment-rules': 'payment_rules'
        };

        for (const [urlPart, type] of Object.entries(documentTypes)) {
            if (url.includes(urlPart)) {
                return type;
            }
        }

        return 'unknown';
    }

    logDocumentView(documentType) {
        // Логирование просмотра документа (можно отправлять на сервер)
        if (window.console) {
            console.log(`Legal document viewed: ${documentType} at ${new Date().toISOString()}`);
        }

        // Опционально: отправка данных на сервер для аналитики
        if (typeof gtag !== 'undefined') {
            gtag('event', 'legal_document_view', {
                'document_type': documentType,
                'timestamp': new Date().toISOString()
            });
        }
    }

    // Метод для программной валидации (можно вызывать извне)
    validateAllForms() {
        const forms = document.querySelectorAll('form');
        let allValid = true;

        forms.forEach(form => {
            if (this.hasLegalCheckboxes(form)) {
                if (!this.validateForm(form)) {
                    allValid = false;
                }
            }
        });

        return allValid;
    }

    // Метод для получения состояния согласий пользователя
    getUserConsents() {
        const consents = {};
        const checkboxes = document.querySelectorAll('.legal-checkbox input[type="checkbox"]');
        
        checkboxes.forEach(checkbox => {
            const documentType = this.getDocumentTypeFromCheckbox(checkbox);
            consents[documentType] = {
                accepted: checkbox.checked,
                timestamp: new Date().toISOString(),
                required: checkbox.hasAttribute('required')
            };
        });

        return consents;
    }

    getDocumentTypeFromCheckbox(checkbox) {
        // Получаем тип документа из атрибутов чекбокса
        const name = checkbox.name || checkbox.id || '';
        
        if (name.includes('terms')) return 'terms_of_use';
        if (name.includes('privacy')) return 'privacy_policy';
        if (name.includes('offer')) return 'public_offer';
        if (name.includes('booking')) return 'booking_rules';
        if (name.includes('personal') || name.includes('data')) return 'personal_data_consent';
        if (name.includes('payment')) return 'payment_rules';
        if (name.includes('marketing')) return 'marketing_consent';
        
        return 'unknown';
    }

    // Метод для восстановления состояния согласий из localStorage
    restoreUserConsents() {
        const savedConsents = localStorage.getItem('hms_legal_consents');
        if (savedConsents) {
            try {
                const consents = JSON.parse(savedConsents);
                Object.entries(consents).forEach(([type, data]) => {
                    const checkbox = this.findCheckboxByType(type);
                    if (checkbox && !checkbox.hasAttribute('required')) {
                        checkbox.checked = data.accepted;
                        this.validateCheckbox(checkbox);
                    }
                });
            } catch (e) {
                console.warn('Failed to restore legal consents:', e);
            }
        }
    }

    // Метод для сохранения состояния согласий в localStorage
    saveUserConsents() {
        const consents = this.getUserConsents();
        localStorage.setItem('hms_legal_consents', JSON.stringify(consents));
    }

    findCheckboxByType(type) {
        const checkboxes = document.querySelectorAll('.legal-checkbox input[type="checkbox"]');
        for (const checkbox of checkboxes) {
            if (this.getDocumentTypeFromCheckbox(checkbox) === type) {
                return checkbox;
            }
        }
        return null;
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    window.legalValidation = new LegalValidation();
    
    // Восстанавливаем состояние согласий для необязательных чекбоксов
    window.legalValidation.restoreUserConsents();
    
    // Сохраняем состояние согласий при изменении
    document.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox' && e.target.closest('.legal-checkbox')) {
            window.legalValidation.saveUserConsents();
        }
    });
});

// Экспорт для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LegalValidation;
} 