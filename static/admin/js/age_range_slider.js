// Двухползунковый слайдер возраста для инлайна HotelMealPlan
(function(){
    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    function initSlider(container) {
        // Не трогаем шаблонные формы (__prefix__), чтобы не копировать флаг initialized при клонировании
        if (container.id && container.id.indexOf('__prefix__') !== -1) {
            return;
        }
        if (container.dataset.initialized === 'true') return;
        container.dataset.initialized = 'true';
        
        console.log('Инициализация слайдера:', container);

        var minAge = parseInt(container.getAttribute('data-min'), 10) || 0;
        var maxAge = parseInt(container.getAttribute('data-max'), 10) || 99;
        var step = parseInt(container.getAttribute('data-step'), 10) || 1;

        // Находим родительский контейнер поля (form-group или field-row)
        var fieldContainer = container.closest('.form-group') || container.closest('.field-row') || container.parentElement;
        if (!fieldContainer) return;
        
        // Ищем age_min input в том же контейнере или рядом
        var minInput = fieldContainer.querySelector('input[name*="age_min"]');
        if (!minInput) {
            // Пробуем найти предыдущий элемент (виджет рендерится после input)
            var prev = container.previousElementSibling;
            if (prev && prev.tagName === 'INPUT' && prev.name && prev.name.includes('age_min')) {
                minInput = prev;
            }
        }
        
        if (!minInput) {
            console.log('Не найден age_min input для слайдера');
            return;
        }
        
        console.log('Найден age_min input:', minInput.name, minInput);
        
        // Ищем соответствующий age_max в том же инлайне
        var minName = minInput.getAttribute('name') || '';
        var maxName = minName.replace('age_min', 'age_max');
        
        // Находим родительский инлайн
        var inlineRoot = container.closest('.inline-related') || container.closest('fieldset') || fieldContainer.parentElement || document;
        
        var maxInput = inlineRoot.querySelector('input[name="' + maxName + '"]');
        if (!maxInput) {
            // Резервный поиск
            var maxInputs = inlineRoot.querySelectorAll('input[name*="age_max"]');
            for (var i = 0; i < maxInputs.length; i++) {
                var maxCandidate = maxInputs[i];
                // Проверяем, что это поле из того же префикса
                if (maxCandidate.name.replace('age_max', 'age_min') === minName) {
                    maxInput = maxCandidate;
                    break;
                }
            }
        }
        
        if (!maxInput) {
            console.log('Не найден age_max input для слайдера. Искали:', maxName);
            return;
        }
        
        console.log('Найден age_max input:', maxInput.name, maxInput);

        // Инициализация значений
        var minValue = parseInt(minInput.value || minAge, 10);
        var maxValue = parseInt(maxInput.value || maxAge, 10);
        if (Number.isNaN(minValue)) minValue = minAge;
        if (Number.isNaN(maxValue)) maxValue = maxAge;
        minValue = clamp(minValue, minAge, maxAge);
        maxValue = clamp(maxValue, minAge, maxAge);
        if (minValue > maxValue) minValue = maxValue;
        
        // Устанавливаем значения в поля, если они пустые
        if (!minInput.value) {
            minInput.value = minValue;
        }
        if (!maxInput.value) {
            maxInput.value = maxValue;
        }

        // Элементы
        var track = container.querySelector('.ars-track');
        var range = container.querySelector('.ars-range');
        var handleMin = container.querySelector('.ars-handle-min');
        var handleMax = container.querySelector('.ars-handle-max');
        var labelMin = container.querySelector('.ars-label-min');
        var labelMax = container.querySelector('.ars-label-max');

        function valueToPercent(val){
            return ((val - minAge) / (maxAge - minAge)) * 100;
        }

        function percentToValue(p){
            var val = minAge + (p / 100) * (maxAge - minAge);
            // шаг
            val = Math.round(val / step) * step;
            return clamp(val, minAge, maxAge);
        }

        function layout(){
            var left = valueToPercent(minValue);
            var right = valueToPercent(maxValue);
            handleMin.style.left = left + '%';
            handleMax.style.left = right + '%';
            range.style.left = left + '%';
            range.style.width = (right - left) + '%';
            labelMin.textContent = String(minValue);
            labelMax.textContent = String(maxValue);
        }

        function startDrag(handle, isMin) {
            function onMove(e){
                var rect = container.getBoundingClientRect();
                var clientX = e.touches ? e.touches[0].clientX : e.clientX;
                var p = ((clientX - rect.left) / rect.width) * 100;
                var v = percentToValue(p);
                if (isMin) {
                    // Не позволяем перекрытие: min <= max
                    v = Math.min(v, maxValue);
                    minValue = v;
                    minInput.value = v;
                } else {
                    // Не позволяем перекрытие: max >= min
                    v = Math.max(v, minValue);
                    maxValue = v;
                    maxInput.value = v;
                }
                layout();
                e.preventDefault();
            }
            function onUp(){
                document.removeEventListener('mousemove', onMove);
                document.removeEventListener('mouseup', onUp);
                document.removeEventListener('touchmove', onMove);
                document.removeEventListener('touchend', onUp);
            }
            document.addEventListener('mousemove', onMove);
            document.addEventListener('mouseup', onUp);
            document.addEventListener('touchmove', onMove, {passive:false});
            document.addEventListener('touchend', onUp);
        }

        handleMin.addEventListener('mousedown', function(e){ 
            console.log('Mousedown на handleMin');
            startDrag(handleMin, true); 
            e.preventDefault(); 
        });
        handleMax.addEventListener('mousedown', function(e){ 
            console.log('Mousedown на handleMax');
            startDrag(handleMax, false); 
            e.preventDefault(); 
        });
        handleMin.addEventListener('touchstart', function(e){ 
            console.log('Touchstart на handleMin');
            startDrag(handleMin, true); 
            e.preventDefault(); 
        }, {passive:false});
        handleMax.addEventListener('touchstart', function(e){ 
            console.log('Touchstart на handleMax');
            startDrag(handleMax, false); 
            e.preventDefault(); 
        }, {passive:false});

        // Синхронизация при ручном вводе (если кто-то снимет hidden или через devtools)
        minInput.addEventListener('input', function(){
            var v = parseInt(minInput.value, 10);
            if (Number.isNaN(v)) v = minAge;
            v = clamp(v, minAge, maxValue);
            minValue = v;
            layout();
        });
        maxInput.addEventListener('input', function(){
            var v = parseInt(maxInput.value, 10);
            if (Number.isNaN(v)) v = maxAge;
            v = clamp(v, minValue, maxAge);
            maxValue = v;
            layout();
        });

        layout();
        
        console.log('Слайдер успешно инициализирован для:', container.id, 'min:', minValue, 'max:', maxValue);
    }

    function initAll(root){
        (root || document).querySelectorAll('.age-range-slider').forEach(initSlider);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function(){ initAll(document); });
    } else {
        initAll(document);
    }

    // Переинициализация при добавлении новых inline-формsetов в админке
    if (window.jQuery) {
        // Django admin событие
        window.jQuery(document).on('formset:added', function(event, $row){
            setTimeout(function(){
                if ($row && $row[0]) {
                    // Сбрасываем флаг инициализации, который мог прийти из шаблонной формы
                    $row[0].querySelectorAll('.age-range-slider').forEach(function(el){
                        if (el.getAttribute('data-initialized') === 'true') {
                            el.removeAttribute('data-initialized');
                        }
                    });
                    initAll($row[0]);
                } else {
                    document.querySelectorAll('.age-range-slider').forEach(function(el){
                        if (el.getAttribute('data-initialized') === 'true') {
                            el.removeAttribute('data-initialized');
                        }
                    });
                    initAll(document);
                }
            }, 50);
        });
    }

    // Также отслеживаем клики по кнопкам "Добавить еще один"
    document.addEventListener('click', function(e) {
        if (e.target && (e.target.classList.contains('add-row') || e.target.textContent.includes('Добавить'))) {
            setTimeout(function(){
                initAll(document);
            }, 100);
        }
    });

    // Резервно: наблюдаем за добавлением элементов
    if (window.MutationObserver && document.body) {
        var observer = new MutationObserver(function(mutations){
            var needInit = false;
            mutations.forEach(function(m){
                m.addedNodes && m.addedNodes.forEach(function(node){
                    if (node.nodeType === 1) {
                        if (node.matches && node.matches('.age-range-slider')) {
                            initSlider(node);
                            needInit = true;
                        } else if (node.querySelectorAll) {
                            var sliders = node.querySelectorAll('.age-range-slider');
                            if (sliders && sliders.length) needInit = true;
                        }
                    }
                });
            });
            if (needInit) {
                setTimeout(function(){ initAll(document); }, 10);
            }
        });
        
        // Проверяем что document.body существует перед observe
        if (document.body) {
            observer.observe(document.body, { childList: true, subtree: true });
        }
    }

    // Дополнительная инициализация через интервал (для сложных случаев)
    var initCounter = 0;
    var initInterval = setInterval(function(){
        initAll(document);
        initCounter++;
        if (initCounter > 10) {
            clearInterval(initInterval);
        }
    }, 500);
})();


