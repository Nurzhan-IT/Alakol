// Глобальные функции для модального окна изображений типов номеров
function initRoomTypeImageModal() {
    const modal = document.getElementById('roomtypeImageModal');
    
    // Если модальное окно уже существует в DOM (из шаблона)
    if (modal) {
        console.log('Модальное окно типа номера найдено в DOM, инициализируем обработчики');
        
        // Обработчик клика по фону модального окна
        modal.addEventListener('click', function(e) {
            // Закрываем только если клик был по фону модального окна
            if (e.target === modal) {
                e.preventDefault();
                e.stopPropagation();
                closeRoomTypeImageModal();
            }
        });
        
        // Обработчик для кнопки закрытия
        const closeBtn = modal.querySelector('.image-modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeRoomTypeImageModal();
            });
        }
        
        // Обработчик клавиши Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.classList.contains('show')) {
                e.preventDefault();
                e.stopPropagation();
                closeRoomTypeImageModal();
            }
        });
    } else {
        // Создаем элемент модального окна, если его нет
        console.log('Модальное окно типа номера не найдено, создаем новое');
        const newModal = document.createElement('div');
        newModal.id = 'roomtypeImageModal';
        newModal.className = 'image-modal';
        newModal.innerHTML = `
            <div class="image-modal-content">
                <button class="image-modal-close" type="button">&times;</button>
                <img id="roomtypeModalImage" src="" alt="Изображение типа номера">
                <div class="image-modal-title" id="roomtypeModalTitle"></div>
            </div>
        `;
        document.body.appendChild(newModal);
        
        // Инициализируем обработчики для нового модального окна
        initRoomTypeImageModal();
    }
}

function openRoomTypeImageModal(imageUrl, roomTypeName) {
    const modal = document.getElementById('roomtypeImageModal');
    const modalImage = document.getElementById('roomtypeModalImage');
    const modalTitle = document.getElementById('roomtypeModalTitle');
    
    if (modal && modalImage && modalTitle) {
        // Показываем лоадер пока изображение загружается
        modalImage.style.opacity = '0.5';
        modalTitle.textContent = 'Загрузка изображения...';
        modal.classList.add('show');
        
        // Предотвращаем прокрутку фона
        document.body.style.overflow = 'hidden';
        
        // Создаем новый объект изображения для предзагрузки
        const tempImg = new Image();
        
        tempImg.onload = function() {
            // Изображение загружено успешно
            modalImage.src = imageUrl;
            modalImage.style.opacity = '1';
            modalTitle.textContent = `Изображение типа номера: ${roomTypeName}`;
        };
        
        tempImg.onerror = function() {
            // Ошибка загрузки изображения
            modalImage.style.opacity = '1';
            modalTitle.textContent = `Ошибка загрузки изображения типа номера: ${roomTypeName}`;
            console.error('Ошибка загрузки изображения:', imageUrl);
        };
        
        // Начинаем загрузку изображения
        tempImg.src = imageUrl;
        
        console.log('Открыто модальное окно для типа номера:', imageUrl);
    } else {
        console.error('Модальное окно типа номера не найдено или не инициализировано');
    }
}

function closeRoomTypeImageModal() {
    const modal = document.getElementById('roomtypeImageModal');
    
    if (modal) {
        modal.classList.remove('show');
        
        // Восстанавливаем прокрутку фона
        document.body.style.overflow = '';
        
        // Очищаем src изображения для экономии памяти
        setTimeout(() => {
            const modalImage = document.getElementById('roomtypeModalImage');
            if (modalImage && !modal.classList.contains('show')) {
                modalImage.src = '';
            }
        }, 300);
        
        console.log('Модальное окно типа номера закрыто');
    }
    
    // Возвращаем false, чтобы предотвратить любые дальнейшие действия
    return false;
}

// Скрипт для множественной загрузки изображений типа номера
document.addEventListener('DOMContentLoaded', function() {
    // Предотвращаем дублирование инициализации
    if (window.roomtypeGalleryInitialized) {
        return;
    }
    window.roomtypeGalleryInitialized = true;
    
    // Инициализируем модальное окно
    initRoomTypeImageModal();
    
    // Добавляем обработчики событий для миниатюр
    setupRoomTypeThumbnailHandlers();
    
    // Функция для обработки множественной загрузки файлов типа номера
    function handleMultipleRoomTypeFileUpload() {
        // Ищем специфическое поле для загрузки изображений типа номера
        const roomtypeImageInput = document.getElementById('multiple_roomtype_images');
        
        if (roomtypeImageInput && !roomtypeImageInput.dataset.initialized) {
            setupRoomTypeImageUpload(roomtypeImageInput);
            roomtypeImageInput.dataset.initialized = 'true';
        }
        
        // Также обрабатываем любые другие множественные поля
        const multipleFileInputs = document.querySelectorAll('input[type="file"][multiple]');
        
        multipleFileInputs.forEach(function(input) {
            if (input.id !== 'multiple_roomtype_images' && !input.dataset.initialized) {
                setupGenericMultipleUpload(input);
                input.dataset.initialized = 'true';
            }
        });
    }
    
    // Функция для настройки загрузки изображений типа номера
    function setupRoomTypeImageUpload(input) {
        // Ищем существующий контейнер или создаем новый
        const wrapper = input.closest('.multiple-file-input-wrapper');
        let previewContainer = wrapper.querySelector('#roomtype-images-preview');
        
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.className = 'multiple-image-preview';
            previewContainer.id = 'roomtype-images-preview';
            wrapper.appendChild(previewContainer);
        }
        
        // Добавляем поддержку drag and drop
        setupDragAndDrop(input, previewContainer);
        
        // Обработчик изменения файлов (удаляем старый обработчик перед добавлением нового)
        const changeHandler = function(e) {
            const files = Array.from(e.target.files);
            displayImagePreviews(files, previewContainer, input);
            updateFileCounter(files.length, input);
            
            // Сохраняем файлы для отправки с формой
            window.selectedRoomTypeImages = files;
        };
        
        // Удаляем предыдущий обработчик если есть
        if (input._changeHandler) {
            input.removeEventListener('change', input._changeHandler);
        }
        
        input._changeHandler = changeHandler;
        input.addEventListener('change', changeHandler);
        
        // Обработчик отправки формы для загрузки файлов
        const form = input.closest('form');
        if (form && !form.dataset.roomtypeHandlerAdded) {
            form.dataset.roomtypeHandlerAdded = 'true';
            form.addEventListener('submit', function(e) {
                console.log('=== DEBUG: Форма RoomType отправляется ===');
                console.log('Форма enctype:', form.getAttribute('enctype'));
                console.log('Найдено input:', input);
                console.log('Input name:', input.name);
                console.log('Input id:', input.id);
                console.log('Файлы в input.files:', input.files);
                console.log('Количество файлов:', input.files.length);
                
                // КРИТИЧЕСКИ ВАЖНО: Проверяем и устанавливаем enctype
                if (form.getAttribute('enctype') !== 'multipart/form-data') {
                    console.error('ОШИБКА: enctype формы не установлен в multipart/form-data!');
                    console.log('Устанавливаем enctype принудительно...');
                    form.setAttribute('enctype', 'multipart/form-data');
                    console.log('Новый enctype:', form.getAttribute('enctype'));
                }
                
                // Убеждаемся, что input включен и виден
                console.log('Input disabled:', input.disabled);
                console.log('Input type:', input.type);
                console.log('Input style.display:', getComputedStyle(input).display);
                
                // Перечисляем все файлы
                for (let i = 0; i < input.files.length; i++) {
                    console.log(`Файл ${i + 1}: ${input.files[i].name}, размер: ${input.files[i].size}, тип: ${input.files[i].type}`);
                }
                
                if (window.selectedRoomTypeImages && window.selectedRoomTypeImages.length > 0) {
                    console.log('Отправляется', window.selectedRoomTypeImages.length, 'файлов типа номера');
                }
                
                // Проверяем FormData
                const formData = new FormData(form);
                console.log('FormData entries:');
                let fileCount = 0;
                for (let [key, value] of formData.entries()) {
                    if (value instanceof File) {
                        fileCount++;
                        console.log(`${key}: ${value.name} (${value.size} bytes, ${value.type})`);
                    } else if (key.includes('multiple_roomtype_images') || key.includes('roomtype')) {
                        console.log(`${key}: ${value}`);
                    }
                }
                console.log(`Всего файлов в FormData: ${fileCount}`);
                
                // Проверяем наличие файлов с правильным именем
                const roomtypeFiles = formData.getAll('multiple_roomtype_images');
                console.log(`Файлы с именем 'multiple_roomtype_images':`, roomtypeFiles.length);
                roomtypeFiles.forEach((file, index) => {
                    console.log(`  Файл ${index + 1}: ${file.name} (${file.size} bytes)`);
                });
            });
        }
    }
    
    // Функция для настройки обычных множественных загрузок
    function setupGenericMultipleUpload(input) {
        // Создаем контейнер для превью изображений
        const previewContainer = document.createElement('div');
        previewContainer.className = 'multiple-image-preview';
        
        // Вставляем контейнер после input
        input.parentNode.insertBefore(previewContainer, input.nextSibling);
        
        // Добавляем поддержку drag and drop
        setupDragAndDrop(input, previewContainer);
        
        // Обработчик изменения файлов
        input.addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            displayImagePreviews(files, previewContainer, input);
            updateFileCounter(files.length, input);
        });
    }
    
    // Функция для настройки drag and drop
    function setupDragAndDrop(input, previewContainer) {
        const dropZone = input.parentNode;
        
        // Проверяем, не установлены ли уже обработчики
        if (dropZone.dataset.dragHandlersSet) {
            return;
        }
        
        dropZone.dataset.dragHandlersSet = 'true';
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight(e) {
            dropZone.classList.add('drag-over');
        }
        
        function unhighlight(e) {
            dropZone.classList.remove('drag-over');
        }
        
        dropZone.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = Array.from(dt.files);
            
            // Фильтруем только изображения
            const imageFiles = files.filter(file => file.type.startsWith('image/'));
            
            if (imageFiles.length > 0) {
                // Создаем новый DataTransfer для обновления input
                const newDt = new DataTransfer();
                
                // Добавляем существующие файлы
                Array.from(input.files).forEach(file => newDt.items.add(file));
                
                // Добавляем новые файлы
                imageFiles.forEach(file => newDt.items.add(file));
                
                input.files = newDt.files;
                
                // Обновляем превью
                displayImagePreviews(Array.from(input.files), previewContainer, input);
                updateFileCounter(input.files.length, input);
            }
        }
    }
    
    // Функция для отображения превью изображений
    function displayImagePreviews(files, previewContainer, input) {
        previewContainer.innerHTML = ''; // Очищаем предыдущие превью
        
        files.forEach(function(file, index) {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const previewWrapper = document.createElement('div');
                    previewWrapper.className = 'image-preview-wrapper';
                    
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.style.cssText = `
                        width: 100px;
                        height: 100px;
                        object-fit: cover;
                        display: block;
                    `;
                    
                    const fileName = document.createElement('div');
                    fileName.textContent = file.name;
                    fileName.className = 'file-name';
                    
                    // Показываем размер файла
                    const fileSize = document.createElement('div');
                    fileSize.textContent = formatFileSize(file.size);
                    fileSize.className = 'file-size';
                    fileSize.style.cssText = `
                        padding: 2px 5px;
                        background: #e9ecef;
                        font-size: 10px;
                        text-align: center;
                        color: #6c757d;
                    `;
                    
                    const removeBtn = document.createElement('button');
                    removeBtn.textContent = '×';
                    removeBtn.type = 'button';
                    removeBtn.className = 'remove-image-btn';
                    removeBtn.title = 'Удалить изображение';
                    
                    removeBtn.addEventListener('click', function() {
                        previewWrapper.remove();
                        // Удаляем файл из списка
                        const dt = new DataTransfer();
                        const filesArray = Array.from(input.files);
                        filesArray.splice(index, 1);
                        
                        filesArray.forEach(function(file) {
                            dt.items.add(file);
                        });
                        
                        input.files = dt.files;
                        updateFileCounter(input.files.length, input);
                    });
                    
                    previewWrapper.appendChild(img);
                    previewWrapper.appendChild(fileName);
                    previewWrapper.appendChild(fileSize);
                    previewWrapper.appendChild(removeBtn);
                    previewContainer.appendChild(previewWrapper);
                };
                
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Функция для обновления счетчика файлов
    function updateFileCounter(count, input) {
        // Удаляем предыдущий счетчик, если есть
        const existingCounter = input.parentNode.querySelector('.file-count-info');
        if (existingCounter) {
            existingCounter.remove();
        }
        
        if (count > 0) {
            const fileCountInfo = document.createElement('div');
            fileCountInfo.className = 'file-count-info';
            fileCountInfo.textContent = `Выбрано файлов: ${count}`;
            input.parentNode.appendChild(fileCountInfo);
        }
    }
    
    // Функция для форматирования размера файла
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Вызываем функцию обработки множественной загрузки
    handleMultipleRoomTypeFileUpload();
    
    // Функция для настройки обработчиков миниатюр типов номеров
    function setupRoomTypeThumbnailHandlers() {
        // Находим все миниатюры типов номеров
        const thumbnails = document.querySelectorAll('.roomtype-gallery-thumbnail');
        
        thumbnails.forEach(function(thumbnail) {
            // Убираем старые обработчики если есть
            thumbnail.removeEventListener('click', thumbnail._clickHandler);
            thumbnail.removeEventListener('mouseenter', thumbnail._mouseenterHandler);
            thumbnail.removeEventListener('mouseleave', thumbnail._mouseleaveHandler);
            
            // Обработчик клика для открытия модального окна
            thumbnail._clickHandler = function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const imageUrl = thumbnail.getAttribute('data-image-url');
                const roomTypeName = thumbnail.getAttribute('data-room-type-name');
                
                if (imageUrl && roomTypeName) {
                    openRoomTypeImageModal(imageUrl, roomTypeName);
                }
            };
            
            thumbnail.addEventListener('click', thumbnail._clickHandler);
            
            // Hover-эффекты для миниатюр
            const img = thumbnail.querySelector('img');
            if (img) {
                thumbnail._mouseenterHandler = function() {
                    img.style.transform = 'scale(1.05)';
                    img.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
                };
                
                thumbnail._mouseleaveHandler = function() {
                    img.style.transform = 'scale(1)';
                    img.style.boxShadow = 'none';
                };
                
                thumbnail.addEventListener('mouseenter', thumbnail._mouseenterHandler);
                thumbnail.addEventListener('mouseleave', thumbnail._mouseleaveHandler);
            }
        });
    }
    
    // Функция, которая будет вызываться при динамическом добавлении новых миниатюр
    function refreshRoomTypeThumbnailHandlers() {
        setupRoomTypeThumbnailHandlers();
    }
    
    // Добавляем функцию в глобальную область видимости для вызова извне
    window.refreshRoomTypeThumbnailHandlers = refreshRoomTypeThumbnailHandlers;
    window.handleMultipleRoomTypeFileUpload = handleMultipleRoomTypeFileUpload;
    
    // Функция для обработки добавления новых форм в inline formset
    function handleInlineFormsetAddition() {
        // Проверяем, не создан ли уже observer
        if (window.roomtypeObserver) {
            return;
        }
        
        // Следим за изменениями в DOM для inline formsets
        window.roomtypeObserver = new MutationObserver(function(mutations) {
            let shouldRefresh = false;
            
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    // Проверяем, добавились ли новые элементы с классом roomtype-gallery-thumbnail
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            if (node.classList && node.classList.contains('roomtype-gallery-thumbnail')) {
                                shouldRefresh = true;
                            } else if (node.querySelector && node.querySelector('.roomtype-gallery-thumbnail')) {
                                shouldRefresh = true;
                            }
                        }
                    });
                }
            });
            
            if (shouldRefresh) {
                // Небольшая задержка, чтобы DOM успел обновиться
                setTimeout(refreshRoomTypeThumbnailHandlers, 100);
            }
        });
        
        // Начинаем наблюдение
        const targetNode = document.querySelector('#roomtypegallery_set-group, .gallery-grid');
        if (targetNode) {
            window.roomtypeObserver.observe(targetNode, {
                childList: true,
                subtree: true
            });
        }
    }
    
    // Инициализируем наблюдение за изменениями
    handleInlineFormsetAddition();
}); 