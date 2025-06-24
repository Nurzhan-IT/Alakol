/* Generated on 2025-05-31 02:59 AM +05 */
/* Legal documents JavaScript for HMS Alakol */

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-open legal documents in new tabs
    const legalLinks = document.querySelectorAll('a[href*="/legal/"]');
    legalLinks.forEach(link => {
        if (link.getAttribute('target') !== '_blank') {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        }
    });
    
    // Highlight required checkboxes
    const requiredCheckboxes = document.querySelectorAll('input[type="checkbox"][required]');
    requiredCheckboxes.forEach(checkbox => {
        const label = document.querySelector(`label[for="${checkbox.id}"]`);
        if (label && !label.innerHTML.includes('*')) {
            label.innerHTML += ' <span class="text-danger">*</span>';
        }
    });
    
    // Form validation for consents
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredConsents = form.querySelectorAll('input[type="checkbox"][required]');
            let allChecked = true;
            let firstUnchecked = null;
            
            // Reset previous error states
            requiredConsents.forEach(checkbox => {
                const formCheck = checkbox.closest('.form-check');
                if (formCheck) {
                    formCheck.classList.remove('error');
                }
            });
            
            // Check all required checkboxes
            requiredConsents.forEach(checkbox => {
                if (!checkbox.checked) {
                    allChecked = false;
                    const formCheck = checkbox.closest('.form-check');
                    if (formCheck) {
                        formCheck.classList.add('error');
                        if (!firstUnchecked) {
                            firstUnchecked = checkbox;
                        }
                    }
                }
            });
            
            if (!allChecked) {
                e.preventDefault();
                
                // Show alert in multiple languages
                alert(gettext('Please confirm all required consents'));
                
                // Focus on first unchecked checkbox
                if (firstUnchecked) {
                    firstUnchecked.focus();
                }
            }
        });
    });
    
    // Smooth scroll for internal links
    const internalLinks = document.querySelectorAll('a[href^="#"]');
    internalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const headerOffset = 80; // Account for fixed header
                const elementPosition = targetElement.offsetTop;
                const offsetPosition = elementPosition - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
                
                // Update URL without triggering scroll
                history.pushState(null, null, `#${targetId}`);
            }
        });
    });
    
    // Language switcher functionality
    function switchDocumentLanguage(language) {
        const currentPath = window.location.pathname;
        let newPath = currentPath;
        
        // Remove existing language prefix
        const pathParts = currentPath.split('/').filter(part => part);
        if (pathParts.length > 0 && ['en', 'ru', 'kk'].includes(pathParts[0])) {
            pathParts.shift();
        }
        
        // Add new language prefix
        newPath = `/${language}/${pathParts.join('/')}/`;
        
        window.location.href = newPath;
    }
    
    // Make function globally available
    window.switchDocumentLanguage = switchDocumentLanguage;
    
    // Checkbox state management
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const formCheck = this.closest('.form-check');
            if (formCheck) {
                formCheck.classList.remove('error');
            }
            
            // Save checkbox state to localStorage
            const checkboxId = this.id || this.name;
            if (checkboxId) {
                localStorage.setItem(`checkbox_${checkboxId}`, this.checked);
            }
        });
        
        // Restore checkbox state from localStorage
        const checkboxId = checkbox.id || checkbox.name;
        if (checkboxId) {
            const savedState = localStorage.getItem(`checkbox_${checkboxId}`);
            if (savedState === 'true') {
                checkbox.checked = true;
            }
        }
    });
    
    // Print functionality
    function printDocument() {
        window.print();
    }
    
    // Add print button if not exists
    const legalDocument = document.querySelector('.legal-document');
    if (legalDocument && !document.querySelector('.print-button')) {
        const printButton = document.createElement('button');
        printButton.innerHTML = '🖨️ ' + gettext('Print Document');
        printButton.className = 'btn btn-outline-secondary print-button';
        printButton.style.cssText = 'margin-bottom: 20px; padding: 10px 20px; border: 1px solid #6c757d; background: none; cursor: pointer;';
        printButton.addEventListener('click', printDocument);
        
        legalDocument.insertBefore(printButton, legalDocument.firstChild);
    }
    
    // Accessibility: keyboard navigation for checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.checked = !this.checked;
                this.dispatchEvent(new Event('change'));
            }
        });
    });
    
    // Auto-scroll to section from URL hash
    if (window.location.hash) {
        setTimeout(() => {
            const targetElement = document.querySelector(window.location.hash);
            if (targetElement) {
                const headerOffset = 80;
                const elementPosition = targetElement.offsetTop;
                const offsetPosition = elementPosition - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        }, 100);
    }
    
    // Form progress tracking
    const consentForms = document.querySelectorAll('form');
    consentForms.forEach(form => {
        const checkboxes = form.querySelectorAll('input[type="checkbox"][required]');
        
        function updateProgress() {
            const checkedCount = form.querySelectorAll('input[type="checkbox"][required]:checked').length;
            const totalCount = checkboxes.length;
            const progress = totalCount > 0 ? (checkedCount / totalCount) * 100 : 0;
            
            // Create or update progress bar
            let progressContainer = form.querySelector('.consent-progress');
            if (!progressContainer && totalCount > 0) {
                progressContainer = document.createElement('div');
                progressContainer.className = 'consent-progress';
                progressContainer.style.cssText = 'margin-bottom: 15px;';
                
                const progressBar = document.createElement('div');
                progressBar.className = 'progress-bar';
                progressBar.style.cssText = 'height: 6px; background-color: #e9ecef; border-radius: 3px; overflow: hidden;';
                
                const progressFill = document.createElement('div');
                progressFill.className = 'progress-fill';
                progressFill.style.cssText = 'height: 100%; background-color: #28a745; transition: width 0.3s ease; width: 0%;';
                
                const progressText = document.createElement('div');
                progressText.className = 'progress-text';
                progressText.style.cssText = 'font-size: 12px; color: #6c757d; margin-top: 5px; text-align: center;';
                
                progressBar.appendChild(progressFill);
                progressContainer.appendChild(progressBar);
                progressContainer.appendChild(progressText);
                
                const firstCheckbox = checkboxes[0];
                if (firstCheckbox) {
                    const firstFormCheck = firstCheckbox.closest('.form-check');
                    if (firstFormCheck && firstFormCheck.parentNode) {
                        firstFormCheck.parentNode.insertBefore(progressContainer, firstFormCheck);
                    }
                }
            }
            
            if (progressContainer) {
                const progressFill = progressContainer.querySelector('.progress-fill');
                const progressText = progressContainer.querySelector('.progress-text');
                
                if (progressFill) {
                    progressFill.style.width = `${progress}%`;
                }
                
                if (progressText) {
                    progressText.textContent = `${checkedCount}/${totalCount} ${gettext('consents confirmed')}`;
                }
            }
        }
        
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateProgress);
        });
        
        // Initial progress update
        updateProgress();
    });
    
    // Analytics tracking (if Google Analytics is available)
    function trackLegalDocumentView(documentType) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'legal_document_view', {
                'document_type': documentType,
                'page_title': document.title,
                'page_location': window.location.href
            });
        }
        
        // Also track in localStorage for internal analytics
        const views = JSON.parse(localStorage.getItem('legal_document_views') || '[]');
        views.push({
            document: documentType,
            timestamp: new Date().toISOString(),
            url: window.location.href
        });
        
        // Keep only last 100 views
        if (views.length > 100) {
            views.splice(0, views.length - 100);
        }
        
        localStorage.setItem('legal_document_views', JSON.stringify(views));
    }
    
    // Track current document view
    const currentPath = window.location.pathname;
    if (currentPath.includes('/legal/')) {
        const documentType = currentPath.split('/').pop().replace('.html', '').replace('/', '');
        trackLegalDocumentView(documentType);
    }
    
    // Removed console.log for legal documents initialization
}); 