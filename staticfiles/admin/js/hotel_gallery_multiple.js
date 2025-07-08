// Глобальные функции для модального окна изображений
function initImageModal() {
    const modal = document.getElementById('imageModal');
    
    // Если модальное окно уже существует в DOM (из шаблона)
    if (modal) {
        console.log('Модальное окно найдено в DOM, инициализируем обработчики');
        
        // Обработчик клика по фону модального окна
        modal.addEventListener('click', function(e) {
            // Закрываем только если клик был по фону модального окна
            if (e.target === modal) {
                e.preventDefault();
                e.stopPropagation();
                closeImageModal();
            }
        });
        
        // Обработчик для кнопки закрытия
        const closeBtn = modal.querySelector('.image-modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeImageModal();
            });
        }
        
        // Обработчик клавиши Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.classList.contains('show')) {
                e.preventDefault();
                e.stopPropagation();
                closeImageModal();
            }
        });
    } else {
        // Создаем элемент модального окна, если его нет
        console.log('Модальное окно не найдено, создаем новое');
        const newModal = document.createElement('div');
        newModal.id = 'imageModal';
        newModal.className = 'image-modal';
        newModal.innerHTML = `
            <div class="image-modal-content">
                <button class="image-modal-close" type="button">&times;</button>
                <img id="modalImage" src="" alt="Изображение отеля">
                <div class="image-modal-title" id="modalTitle"></div>
            </div>
        `;
        document.body.appendChild(newModal);
        
        // Инициализируем обработчики для нового модального окна
        initImageModal();
    }
}

function openImageModal(imageUrl, hotelName) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('modalTitle');
    
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
            modalTitle.textContent = `Изображение отеля: ${hotelName}`;
        };
        
        tempImg.onerror = function() {
            // Ошибка загрузки изображения
            modalImage.style.opacity = '1';
            modalTitle.textContent = `Ошибка загрузки изображения отеля: ${hotelName}`;
            console.error('Ошибка загрузки изображения:', imageUrl);
        };
        
        // Начинаем загрузку изображения
        tempImg.src = imageUrl;
        
        console.log('Открыто модальное окно для:', imageUrl);
    } else {
        console.error('Модальное окно не найдено или не инициализировано');
    }
}

function closeImageModal() {
    const modal = document.getElementById('imageModal');
    
    if (modal) {
        modal.classList.remove('show');
        
        // Восстанавливаем прокрутку фона
        document.body.style.overflow = '';
        
        // Очищаем src изображения для экономии памяти
        setTimeout(() => {
            const modalImage = document.getElementById('modalImage');
            if (modalImage && !modal.classList.contains('show')) {
                modalImage.src = '';
            }
        }, 300);
        
        console.log('Модальное окно закрыто');
    }
    
    // Возвращаем false, чтобы предотвратить любые дальнейшие действия
    return false;
}

// Скрипт для множественной загрузки изображений отеля
document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем модальное окно
    initImageModal();
    
    // Добавляем обработчики событий для миниатюр
    setupThumbnailHandlers();
    
    // Функция для обработки множественной загрузки файлов
    function handleMultipleFileUpload() {
        // Ищем специфическое поле для загрузки изображений отеля
        const hotelImageInput = document.getElementById('multiple_hotel_images');
        
        if (hotelImageInput) {
            setupHotelImageUpload(hotelImageInput);
        }
        
        // Также обрабатываем любые другие множественные поля
        const multipleFileInputs = document.querySelectorAll('input[type="file"][multiple]');
        
        multipleFileInputs.forEach(function(input) {
            if (input.id !== 'multiple_hotel_images') {
                setupGenericMultipleUpload(input);
            }
        });
    }
    
    // Функция для настройки загрузки изображений отеля
    function setupHotelImageUpload(input) {
        // Создаем контейнер для превью изображений
        const previewContainer = document.createElement('div');
        previewContainer.className = 'multiple-image-preview';
        previewContainer.id = 'hotel-images-preview';
        
        // Вставляем контейнер после input wrapper
        const wrapper = input.closest('.multiple-file-input-wrapper');
        wrapper.appendChild(previewContainer);
        
        // Добавляем поддержку drag and drop
        setupDragAndDrop(input, previewContainer);
        
        // Обработчик изменения файлов
        input.addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            displayImagePreviews(files, previewContainer, input);
            updateFileCounter(files.length, input);
            
            // Сохраняем файлы для отправки с формой
            window.selectedHotelImages = files;
        });
        
        // Обработчик отправки формы для загрузки файлов
        const form = input.closest('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                console.log('=== DEBUG: Форма отправляется ===');
                console.log('Найдено input:', input);
                console.log('Файлы в input.files:', input.files);
                console.log('Количество файлов:', input.files.length);
                
                // Перечисляем все файлы
                for (let i = 0; i < input.files.length; i++) {
                    console.log(`Файл ${i + 1}: ${input.files[i].name}, размер: ${input.files[i].size}`);
                }
                
                if (window.selectedHotelImages && window.selectedHotelImages.length > 0) {
                    console.log('Отправляется', window.selectedHotelImages.length, 'файлов');
                }
                
                // Проверяем FormData
                const formData = new FormData(form);
                console.log('FormData entries:');
                for (let [key, value] of formData.entries()) {
                    if (value instanceof File) {
                        console.log(`${key}: ${value.name} (${value.size} bytes)`);
                    } else {
                        console.log(`${key}: ${value}`);
                    }
                }
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
    handleMultipleFileUpload();
    
    // Функция для настройки обработчиков миниатюр
    function setupThumbnailHandlers() {
        // Находим все миниатюры
        const thumbnails = document.querySelectorAll('.hotel-gallery-thumbnail');
        
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
                const hotelName = thumbnail.getAttribute('data-hotel-name');
                
                if (imageUrl && hotelName) {
                    openImageModal(imageUrl, hotelName);
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
    function refreshThumbnailHandlers() {
        setupThumbnailHandlers();
    }
    
    // Добавляем функцию в глобальную область видимости для вызова извне
    window.refreshThumbnailHandlers = refreshThumbnailHandlers;
    
    // Функция для обработки добавления новых форм в inline formset
    function handleInlineFormsetAddition() {
        // Следим за изменениями в DOM для inline formsets
        const observer = new MutationObserver(function(mutations) {
            let shouldRefresh = false;
            
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    // Проверяем, добавились ли новые элементы с классом hotel-gallery-thumbnail
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            if (node.classList && node.classList.contains('hotel-gallery-thumbnail')) {
                                shouldRefresh = true;
                            } else if (node.querySelector && node.querySelector('.hotel-gallery-thumbnail')) {
                                shouldRefresh = true;
                            }
                        }
                    });
                }
            });
            
            if (shouldRefresh) {
                // Небольшая задержка, чтобы DOM успел обновиться
                setTimeout(refreshThumbnailHandlers, 100);
            }
        });
        
        // Начинаем наблюдение
        const targetNode = document.querySelector('#hotellgallery_set-group, .gallery-grid');
        if (targetNode) {
            observer.observe(targetNode, {
                childList: true,
                subtree: true
            });
        }
    }
    
    // Инициализируем наблюдение за изменениями
    handleInlineFormsetAddition();
});
