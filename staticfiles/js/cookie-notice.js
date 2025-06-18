// Cookie Notice Management
document.addEventListener('DOMContentLoaded', function() {
    const cookieNotice = document.getElementById('cookie-notice');
    const cookieAcceptBtn = document.getElementById('cookie-accept');
    const cookieDeclineBtn = document.getElementById('cookie-decline');
    
    // Проверяем, есть ли уже согласие пользователя
    const cookieConsent = localStorage.getItem('cookieConsent');
    
    // Показываем уведомление только если согласие не дано
    if (!cookieConsent) {
        setTimeout(function() {
            cookieNotice.style.display = 'block';
            // Плавное появление
            setTimeout(function() {
                cookieNotice.style.opacity = '1';
            }, 100);
        }, 1000); // Показываем через 1 секунду после загрузки страницы
    }
    
    // Обработчик принятия cookie
    cookieAcceptBtn.addEventListener('click', function() {
        localStorage.setItem('cookieConsent', 'accepted');
        localStorage.setItem('cookieConsentDate', new Date().toISOString());
        hideCookieNotice();
        
        // Можно добавить отправку события на сервер для аналитики
        // trackCookieConsent('accepted');
    });
    
    // Обработчик отклонения cookie
    cookieDeclineBtn.addEventListener('click', function() {
        localStorage.setItem('cookieConsent', 'declined');
        localStorage.setItem('cookieConsentDate', new Date().toISOString());
        hideCookieNotice();
        
        // Отключаем все не необходимые cookie
        disableNonEssentialCookies();
        
        // Можно добавить отправку события на сервер для аналитики
        // trackCookieConsent('declined');
    });
    
    function hideCookieNotice() {
        cookieNotice.style.opacity = '0';
        setTimeout(function() {
            cookieNotice.style.display = 'none';
        }, 300);
    }
    
    function disableNonEssentialCookies() {
        // Здесь можно добавить логику для отключения аналитических
        // и рекламных cookie, если они используются
        // Removed console.log for non-essential cookies disabled notification
    }
    
    // Функция для отправки события согласия на сервер (опционально)
    function trackCookieConsent(action) {
        // Пример отправки данных на сервер
        fetch('/cookie-consent/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                action: action,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent
            })
        }).catch(function(error) {
            // Removed console.log for cookie consent tracking error - error handling preserved
        });
    }
}); 