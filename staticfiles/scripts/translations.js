// Функция для определения текущего языка из URL
function getCurrentLanguage() {
    const path = window.location.pathname;
    if (path.startsWith('/ru/')) {
        return 'ru';
    } else if (path.startsWith('/kk/')) {
        return 'kk';
    } else if (path.startsWith('/en/')) {
        return 'en';
    }
    return 'ru'; // по умолчанию английский
}

// Объект с переводами
const translations = {
    'en': {
        'Adding room...': 'Adding room...',
        'Added to selection': 'Added to selection',
        'Updated': 'Updated',
        'Update': 'Update',
        'Корзина очищена и добавлен новый номер': 'Cart cleared and new room added'
    },
    'ru': {
        'Adding room...': 'Добавляем номер...',
        'Added to selection': 'Добавлено в выборку',
        'Updated': 'Обновлено',
        'Update': 'Обновить',
        'Корзина очищена и добавлен новый номер': 'Корзина очищена и добавлен новый номер'
    },
    'kk': {
        'Adding room...': 'Бөлме қосуда...',
        'Added to selection': 'Таңдауға қосылды',
        'Updated': 'Жаңартылды',
        'Update': 'Жаңарту',
        'Корзина очищена и добавлен новый номер': 'Себет тазартылды және жаңа бөлме қосылды'
    }
};

// Добавляем массивы месяцев для каждого языка
const monthNames = {
    'en': [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ],
    'ru': [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ],
    'kk': [
        'Қаңтар', 'Ақпан', 'Наурыз', 'Сәуір', 'Мамыр', 'Маусым',
        'Шілде', 'Тамыз', 'Қыркүйек', 'Қазан', 'Қараша', 'Желтоқсан'
    ]
};

// Функция для получения перевода
function gettext(text) {
    const currentLang = getCurrentLanguage();
    if (translations[currentLang] && translations[currentLang][text]) {
        return translations[currentLang][text];
    }
    return text; // возвращаем оригинальный текст, если перевод не найден
}

// Функция для получения массива месяцев на текущем языке
function getMonthNames() {
    const lang = getCurrentLanguage();
    return monthNames[lang] || monthNames['en'];
}

// Псевдоним для более короткого использования
window._ = gettext;
window.getMonthNames = getMonthNames; 