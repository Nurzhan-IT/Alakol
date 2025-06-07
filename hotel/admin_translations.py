"""
Переводы для административной панели на русский язык
"""

ADMIN_TRANSLATIONS = {
    # Основные действия
    'Add': 'Добавить',
    'Change': 'Изменить',
    'Delete': 'Удалить',
    'Save': 'Сохранить',
    'Save and continue editing': 'Сохранить и продолжить редактирование',
    'Save and add another': 'Сохранить и добавить еще',
    'Save as new': 'Сохранить как новое',
    'Delete selected': 'Удалить выбранные',
    
    # Навигация
    'Home': 'Главная',
    'Log out': 'Выйти',
    'Change password': 'Изменить пароль',
    'View site': 'Просмотреть сайт',
    'Documentation': 'Документация',
    
    # Интерфейс
    'Action': 'Действие',
    'Go': 'Выполнить',
    'Filter': 'Фильтр',
    'All': 'Все',
    'Search': 'Поиск',
    'Clear all filters': 'Очистить все фильтры',
    
    # Состояния
    'Recent actions': 'Последние действия',
    'My actions': 'Мои действия',
    'None available': 'Недоступно',
    'Welcome': 'Добро пожаловать',
    'Django administration': 'Админ панель Alakol',
    
    # Пагинация
    'Show all': 'Показать все',
    'results': 'результатов',
    'result': 'результат',
    
    # Формы
    'Yes, I\'m sure': 'Да, я уверен',
    'No, take me back': 'Нет, вернуться назад',
    'Please correct the error below.': 'Пожалуйста, исправьте ошибку ниже.',
    'Please correct the errors below.': 'Пожалуйста, исправьте ошибки ниже.',
    
    # Модели
    'Users': 'Пользователи',
    'Groups': 'Группы',
    'Permissions': 'Разрешения',
    
    # Даты и время
    'Today': 'Сегодня',
    'Now': 'Сейчас',
    'Date/time': 'Дата/Время',
    'Date': 'Дата',
    'Time': 'Время',
    
    # Сообщения
    'Successfully deleted': 'Успешно удалено',
    'Successfully added': 'Успешно добавлено',
    'Successfully changed': 'Успешно изменено',
    
    # Поля
    'This field is required.': 'Это поле обязательно.',
    'Enter a valid email address.': 'Введите корректный email адрес.',
    'Enter a valid URL.': 'Введите корректный URL.',
    
    # Прочее
    'Available': 'Доступные',
    'Chosen': 'Выбранные',
    'Choose': 'Выбрать',
    'Remove': 'Удалить',
    'Add another': 'Добавить еще',
    'Show': 'Показать',
    'Hide': 'Скрыть',
    'Open': 'Открыть',
    'Close': 'Закрыть',
    'Clear': 'Очистить',
    'Reset': 'Сбросить',
    'Apply': 'Применить',
    'Cancel': 'Отменить',
    'OK': 'ОК',
    'Yes': 'Да',
    'No': 'Нет',
}

def get_translation(text):
    """
    Получить русский перевод для английского текста
    """
    return ADMIN_TRANSLATIONS.get(text, text) 