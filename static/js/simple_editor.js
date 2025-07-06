document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех простых редакторов на странице
    const editors = document.querySelectorAll('.simple-editor-container');
    
    editors.forEach(function(editorContainer) {
        const toolbar = editorContainer.querySelector('.simple-editor-toolbar');
        const textarea = editorContainer.querySelector('.simple-text-editor');
        
        if (!toolbar || !textarea) return;
        
        // Создаем contenteditable div для редактирования
        const editableDiv = document.createElement('div');
        editableDiv.contentEditable = true;
        editableDiv.className = 'simple-text-editor';
        editableDiv.style.cssText = textarea.style.cssText;
        editableDiv.style.display = 'block';
        editableDiv.style.minHeight = '200px';
        editableDiv.style.padding = '12px';
        editableDiv.style.border = 'none';
        editableDiv.style.outline = 'none';
        editableDiv.style.fontFamily = 'inherit';
        editableDiv.style.lineHeight = '1.5';
        
        // Копируем содержимое из textarea
        editableDiv.innerHTML = textarea.value || '';
        
        // Скрываем textarea и показываем editable div
        textarea.style.display = 'none';
        textarea.parentNode.insertBefore(editableDiv, textarea);
        
        // Синхронизация с textarea
        editableDiv.addEventListener('input', function() {
            textarea.value = editableDiv.innerHTML;
        });
        
        editableDiv.addEventListener('blur', function() {
            textarea.value = editableDiv.innerHTML;
        });
        
        // Обработка кнопок форматирования
        toolbar.addEventListener('click', function(e) {
            if (e.target.tagName === 'BUTTON') {
                e.preventDefault();
                
                const command = e.target.dataset.command;
                const value = e.target.dataset.value;
                
                // Фокусируемся на editable div
                editableDiv.focus();
                
                // Выполняем команду (убрали поддержку formatBlock для заголовков)
                document.execCommand(command, false, null);
                
                // Обновляем textarea
                textarea.value = editableDiv.innerHTML;
                
                // Обновляем активное состояние кнопок
                updateButtonStates();
            }
        });
        
        // Функция обновления состояния кнопок
        function updateButtonStates() {
            const buttons = toolbar.querySelectorAll('button');
            buttons.forEach(function(button) {
                button.classList.remove('active');
            });
            
            // Проверяем текущее форматирование
            if (document.queryCommandState('bold')) {
                toolbar.querySelector('[data-command="bold"]').classList.add('active');
            }
            if (document.queryCommandState('italic')) {
                toolbar.querySelector('[data-command="italic"]').classList.add('active');
            }
            if (document.queryCommandState('underline')) {
                toolbar.querySelector('[data-command="underline"]').classList.add('active');
            }
        }
        
        // Обновляем состояние кнопок при изменении выделения
        editableDiv.addEventListener('keyup', updateButtonStates);
        editableDiv.addEventListener('mouseup', updateButtonStates);
        editableDiv.addEventListener('input', updateButtonStates);
        
        // Обработка клавиатурных сокращений
        editableDiv.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'b':
                        e.preventDefault();
                        document.execCommand('bold', false, null);
                        break;
                    case 'i':
                        e.preventDefault();
                        document.execCommand('italic', false, null);
                        break;
                    case 'u':
                        e.preventDefault();
                        document.execCommand('underline', false, null);
                        break;
                }
                updateButtonStates();
                textarea.value = editableDiv.innerHTML;
            }
        });
    });
}); 