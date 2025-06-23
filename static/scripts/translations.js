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
    return 'ru'; // по умолчанию русский
}

// Объект с переводами
const translations = {
    'en': {
        // Booking system
        'Adding room...': 'Adding room...',
        'Added to selection': 'Added to selection',
        'Updated': 'Updated',
        'Update': 'Update',
        'Корзина очищена и добавлен новый номер': 'Cart cleared and new room added',
        
        // SweetAlert messages
        'Attention!': 'Attention!',
        'Yes, clear': 'Yes, clear',
        'No, cancel': 'No, cancel',
        'No Selections Yet...': 'No Selections Yet...',
        'Add some selection to continue to cart...': 'Add some selection to continue to cart...',
        
        // Notifications
        'Notification Seen!': 'Notification Seen!',
        'Bookmark Deleted': 'Bookmark Deleted',
        'Login To Bookmark Hotel': 'Login To Bookmark Hotel',
        'Review submitted successfully': 'Review submitted successfully',
        'Add To Selection': 'Add To Selection',
        
        // Legal documents
        'Print Document': 'Print Document',
        'consents confirmed': 'consents confirmed',
        'Please confirm all required consents': 'Please confirm all required consents',
        
        // Currency
        'currency_symbol': '₽'
    },
    'ru': {
        // Booking system
        'Adding room...': 'Добавляем номер...',
        'Added to selection': 'Добавлено в выборку',
        'Updated': 'Обновлено',
        'Update': 'Обновить',
        'Корзина очищена и добавлен новый номер': 'Корзина очищена и добавлен новый номер',
        
        // SweetAlert messages
        'Attention!': 'Внимание!',
        'Yes, clear': 'Да, очистить',
        'No, cancel': 'Нет, отмена',
        'No Selections Yet...': 'Пока нет выбранных номеров...',
        'Add some selection to continue to cart...': 'Добавьте номера для продолжения оформления...',
        
        // Notifications
        'Notification Seen!': 'Уведомление просмотрено!',
        'Bookmark Deleted': 'Закладка удалена',
        'Login To Bookmark Hotel': 'Войдите для добавления в закладки',
        'Review submitted successfully': 'Отзыв успешно отправлен',
        'Add To Selection': 'Добавить в выборку',
        
        // Legal documents
        'Print Document': 'Печать документа',
        'consents confirmed': 'согласий подтверждено',
        'Please confirm all required consents': 'Пожалуйста, подтвердите все обязательные согласия',
        
        // Currency
        'currency_symbol': '₽'
    },
    'kk': {
        // Booking system
        'Adding room...': 'Бөлме қосуда...',
        'Added to selection': 'Таңдауға қосылды',
        'Updated': 'Жаңартылды',
        'Update': 'Жаңарту',
        'Корзина очищена и добавлен новый номер': 'Себет тазартылды және жаңа бөлме қосылды',
        
        // SweetAlert messages
        'Attention!': 'Назар аударыңыз!',
        'Yes, clear': 'Иә, тазарту',
        'No, cancel': 'Жоқ, болдырмау',
        'No Selections Yet...': 'Әлі таңдалған бөлмелер жоқ...',
        'Add some selection to continue to cart...': 'Рәсімдеуді жалғастыру үшін бөлмелерді қосыңыз...',
        
        // Notifications
        'Notification Seen!': 'Хабарландыру көрілді!',
        'Bookmark Deleted': 'Бетбелгі жойылды',
        'Login To Bookmark Hotel': 'Бетбелгіге қосу үшін кіріңіз',
        'Review submitted successfully': 'Пікір сәтті жіберілді',
        'Add To Selection': 'Таңдауға қосу',
        
        // Legal documents
        'Print Document': 'Құжатты басып шығару',
        'consents confirmed': 'келісім расталды',
        'Please confirm all required consents': 'Барлық міндетті келісімдерді растаңыз',
        
        // Currency
        'currency_symbol': '₸'
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