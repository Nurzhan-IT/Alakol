document.addEventListener('DOMContentLoaded', function() {
    const startDateInput = document.getElementById('id_start_date');
    const endDateInput = document.getElementById('id_end_date');
    
    if (startDateInput && endDateInput) {
        // Функция для проверки дат
        function validateDates() {
            const startDate = new Date(startDateInput.value);
            const endDate = new Date(endDateInput.value);
            
            // Удаляем предыдущие ошибки
            clearErrors();
            
            if (startDateInput.value && endDateInput.value) {
                if (endDate < startDate) {
                    showError(endDateInput, 'Дата окончания не может быть раньше даты начала');
                    return false;
                }
            }
            
            return true;
        }
        
        // Функция для отображения ошибки
        function showError(input, message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = message;
            
            input.parentNode.appendChild(errorDiv);
            input.classList.add('error');
        }
        
        // Функция для очистки ошибок
        function clearErrors() {
            const errorMessages = document.querySelectorAll('.error-message');
            errorMessages.forEach(function(error) {
                error.remove();
            });
            
            startDateInput.classList.remove('error');
            endDateInput.classList.remove('error');
        }
        
        // Добавляем обработчики событий
        startDateInput.addEventListener('change', validateDates);
        endDateInput.addEventListener('change', validateDates);
        
        // Валидация при отправке формы
        const form = startDateInput.closest('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                if (!validateDates()) {
                    e.preventDefault();
                    return false;
                }
            });
        }
    }
}); 