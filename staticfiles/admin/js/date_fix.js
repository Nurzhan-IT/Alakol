// Исправление проблемы с форматами дат в русской админке
(function() {
    'use strict';
    
    // Функция для конвертации русского формата в ISO
    function convertRussianToISO(dateStr) {
        if (!dateStr) return '';
        
        // Проверяем если это уже ISO формат
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
            return dateStr;
        }
        
        // Конвертируем из русского формата DD.MM.YYYY в ISO YYYY-MM-DD
        var match = dateStr.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/);
        if (match) {
            var day = match[1].padStart(2, '0');
            var month = match[2].padStart(2, '0');
            var year = match[3];
            return year + '-' + month + '-' + day;
        }
        
        return dateStr;
    }
    
    // Функция для конвертации ISO в русский формат для отображения
    function convertISOToRussian(dateStr) {
        if (!dateStr) return '';
        
        // Проверяем если это ISO формат
        var match = dateStr.match(/^(\d{4})-(\d{2})-(\d{2})$/);
        if (match) {
            var year = match[1];
            var month = match[2];
            var day = match[3];
            return day + '.' + month + '.' + year;
        }
        
        return dateStr;
    }
    
    // Исправляем поля дат при загрузке
    function fixDateFields() {
        var dateFields = document.querySelectorAll('.vDateField');
        
        dateFields.forEach(function(field) {
            // Добавляем placeholder
            field.setAttribute('placeholder', 'YYYY-MM-DD или DD.MM.YYYY');
            
            // Обработчик фокуса - конвертируем в ISO формат для редактирования
            field.addEventListener('focus', function() {
                var value = this.value;
                if (value) {
                    this.value = convertRussianToISO(value);
                }
            });
            
            // Обработчик потери фокуса - оставляем в ISO формате
            field.addEventListener('blur', function() {
                var value = this.value.trim();
                if (value) {
                    // Проверяем русский формат и конвертируем в ISO
                    this.value = convertRussianToISO(value);
                }
            });
            
            // Обработчик ввода - разрешаем оба формата
            field.addEventListener('input', function() {
                // Удаляем некорректные символы
                this.value = this.value.replace(/[^\d\.\-]/g, '');
            });
        });
    }
    
    // Исправляем календарные виджеты Django
    function fixCalendarWidgets() {
        // Переопределяем функцию календаря если она существует
        if (window.DateTimeShortcuts && window.DateTimeShortcuts.handleCalendarCallback) {
            var originalCallback = window.DateTimeShortcuts.handleCalendarCallback;
            
            window.DateTimeShortcuts.handleCalendarCallback = function(num) {
                var callback = originalCallback(num);
                return function(y, m, d) {
                    // Форматируем дату в ISO формате
                    var dateStr = y + '-' + (m < 10 ? '0' : '') + m + '-' + (d < 10 ? '0' : '') + d;
                    window.DateTimeShortcuts.calendarInputs[num].value = dateStr;
                    window.DateTimeShortcuts.calendarInputs[num].focus();
                    document.getElementById(window.DateTimeShortcuts.calendarDivName1 + num).style.display = 'none';
                };
            };
        }
    }
    
    // Исправляем отправку форм
    function fixFormSubmission() {
        var forms = document.querySelectorAll('form');
        
        forms.forEach(function(form) {
            form.addEventListener('submit', function() {
                var dateFields = this.querySelectorAll('.vDateField');
                
                dateFields.forEach(function(field) {
                    if (field.value) {
                        // Убеждаемся что дата в ISO формате перед отправкой
                        field.value = convertRussianToISO(field.value);
                    }
                });
            });
        });
    }
    
    // Инициализация после загрузки DOM
    function init() {
        fixDateFields();
        fixCalendarWidgets();
        fixFormSubmission();
        
        // Повторяем исправления через небольшой интервал для динамически добавляемых полей
        setTimeout(function() {
            fixDateFields();
        }, 1000);
    }
    
    // Запускаем при загрузке
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Также запускаем при изменении содержимого (для inline форм)
    var observer = new MutationObserver(function(mutations) {
        var shouldReinit = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                for (var i = 0; i < mutation.addedNodes.length; i++) {
                    var node = mutation.addedNodes[i];
                    if (node.nodeType === 1 && (node.classList.contains('vDateField') || node.querySelector('.vDateField'))) {
                        shouldReinit = true;
                        break;
                    }
                }
            }
        });
        
        if (shouldReinit) {
            setTimeout(fixDateFields, 100);
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
})(); 