# Инструкция по запуску SEO тестирования

## 🚀 Быстрый старт

### 1. Запуск Django сервера
```bash
python manage.py runserver 0.0.0.0:8000
```

### 2. Тестирование структурированных данных
```bash
python test_structured_data.py
```
При запросе введите: `http://localhost:8000`

### 3. Проверка основных SEO элементов

#### Sitemap.xml
```bash
curl http://localhost:8000/sitemap.xml
```
Или откройте в браузере: http://localhost:8000/sitemap.xml

#### Robots.txt
```bash
curl http://localhost:8000/robots.txt
```
Или откройте в браузере: http://localhost:8000/robots.txt

### 4. Проверка мультиязычности

#### Русский (основной)
- http://localhost:8000/
- http://localhost:8000/ru/

#### Казахский
- http://localhost:8000/kk/

#### Английский
- http://localhost:8000/en/

## 🔍 Онлайн тестирование

### Google Rich Results Test
1. Откройте: https://search.google.com/test/rich-results
2. Введите URL вашей страницы отеля
3. Нажмите "Test URL"

### Schema.org Validator
1. Откройте: https://validator.schema.org/
2. Вставьте HTML код страницы или URL
3. Проверьте валидность структурированных данных

## ✅ Ожидаемые результаты

### Структурированные данные должны содержать:
- ✅ Hotel Schema с полной информацией
- ✅ ItemList для списка отелей
- ✅ TouristDestination для Алаколя
- ✅ BreadcrumbList для навигации
- ✅ Review Schema для отзывов

### Мета-теги должны быть:
- ✅ Уникальные title для каждой страницы
- ✅ Описательные meta description
- ✅ Open Graph теги
- ✅ Twitter Card теги
- ✅ Hreflang теги для языков

## 🐛 Возможные проблемы

### Если структурированные данные не найдены:
1. Проверьте что Django сервер запущен
2. Убедитесь что в базе есть отели со статусом "Live"
3. Проверьте что шаблоны правильно наследуются

### Если sitemap.xml не работает:
1. Проверьте что в INSTALLED_APPS добавлен 'django.contrib.sitemaps'
2. Убедитесь что URL для sitemap добавлен в urls.py
3. Проверьте что нет ошибок в sitemaps.py

### Если robots.txt не работает:
1. Проверьте что функция robots_txt добавлена в views.py
2. Убедитесь что URL для robots.txt добавлен в urls.py

## 📱 Тестирование на мобильных устройствах

### Используйте ngrok для внешнего доступа:
```bash
# Установка ngrok (если не установлен)
# Скачайте с https://ngrok.com/

# Запуск туннеля
ngrok http 8000
```

Полученный URL можно использовать для тестирования в Google Rich Results Test.

## 📊 Мониторинг

После запуска в продакшен:
1. Добавьте сайт в Google Search Console
2. Отправьте sitemap.xml
3. Мониторьте Rich Results Report
4. Отслеживайте индексацию страниц

---
*Создано: декабрь 2024* 