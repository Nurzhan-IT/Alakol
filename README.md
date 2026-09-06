<p align="center">
  <img src="static/images/logo.png" alt="Alakol HMS logo" width="360">
</p>

<h1 align="center">Alakol HMS</h1>

<p align="center">
  Full-stack платформа онлайн-бронирования отелей и баз отдыха на озере Алаколь (Казахстан):<br>
  поиск и бронирование номеров, онлайн-оплата, персональный кабинет, мультиязычность и админ-панель для управления бизнесом.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white">
  <img alt="Django" src="https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white">
  <img alt="Redis" src="https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white">
  <a href="https://github.com/Nurzhan-IT/Alakol/actions/workflows/deploy.yml"><img alt="CI" src="https://github.com/Nurzhan-IT/Alakol/actions/workflows/deploy.yml/badge.svg"></a>
</p>

---

## О проекте

**Alakol HMS** — коммерческий сервис бронирования (в духе Booking.com в миниатюре) для отелей и баз отдыха региона озера Алаколь. Гость ищет размещение по датам и фильтрам, выбирает номер, вносит **онлайн-предоплату 10%** через платёжный шлюз **Робокасса** и доплачивает оставшиеся 90% при заселении. Проект разрабатывается и поддерживается мной как основным автором на протяжении свыше года, с одним соавтором [@ct0202](https://github.com/ct0202) по отдельным задачам.

Проект написан на Django и построен как классическое монолитное приложение с чётким разделением на предметные модули (apps), собственным слоем кэширования, фоновым обработчиком бронирований и полностью автоматизированным CI/CD.

## Ключевые возможности

**Бронирование и оплата**
- Поиск отелей по датам, цене, рейтингу, вместимости и удобствам (`search`), с пагинацией и сортировкой
- Гибкая модель номеров: типы номеров, галереи, детальные удобства, планы питания, вместимость
- Динамическое ценообразование по датам (`RoomType.dynamic_pricing`) и сезонность работы отеля (диапазон дат в формате ДД.ММ с поддержкой периодов, переходящих через Новый год)
- Проверка занятости номеров с учётом пересечений броней и периодов недоступности (`booking.RoomUnavailability`)
- Купоны на скидку (процент/фикс), отзывы и рейтинги отелей, избранное (закладки)
- Интеграция с **Робокассой**: подпись запросов SHA-256, тестовый/боевой режим, локализованные описания платежа (ru/kk/en)
- Автоматическое разделение суммы 10% (предоплата онлайн) 
- Бронирования автоматически "сгорают" через 10 минут без оплаты — фоновый воркер (`run_booking_processor`) и `cron`-задача каждые 5 минут переводят просроченные брони в статус `unpaid`

**Личный кабинет и аккаунты**
- Кастомная модель пользователя с входом по email (регистронезависимый бэкенд аутентификации)
- Кабинет гостя: история и детали бронирований, уведомления, избранное, отзывы, профиль, смена пароля
- Учёт согласий с юридическими документами (условия использования, политика конфиденциальности, условия оплаты и т.д.) с версионированием и историей отказа от согласия

**Мультиязычность и SEO**
- Полная локализация интерфейса и контента на **русском, казахском и английском** (`django-modeltranslation`, `i18n_patterns`)
- Автоматическая генерация `sitemap.xml` и `robots.txt`, микроразметка Schema.org, Open Graph
- Отдельные версии юридических документов для каждого языка

**Админ-панель и аналитика**
- Кастомизированная админка на **Jazzmin** с собственной темой, иконками разделов и виджетами
- Дашборд администратора: статистика по броням/доходу/популярным типам номеров, экспорт в CSV/JSON, точечная инвалидация кэша
- `django-import-export` для массовой работы с данными, лёгкий встроенный WYSIWYG-редактор для текстового контента

**Производительность и эксплуатация**
- Многоуровневое кэширование на **Redis** (короткоживущий кэш запросов + отдельный `long_term` кэш) с собственным генератором ключей и сигналами инвалидации
- Оптимизированные запросы (`select_related`/`prefetch_related`) для устранения N+1
- `/health/`, `/ready/`, `/live/` — эндпоинты проверки состояния для контейнерной оркестрации
- Отправка почты через AWS SES или Mailgun (`django-anymail`)

**Тесты + CI/CD**
- Свыше 160 автотестов (unit + view-тесты) в приложениях `hotel`, `booking`, `search`, `userauths`, `robokassa`, `user_dashboard`
- CI на GitHub Actions: проверка `manage.py check`, прогон полного тестового набора против реальных Postgres/Redis перед каждым деплоем

## Технологический стек

| Категория        | Технологии |
|-------------------|------------|
| Backend           | Python 3.11, Django 4.2, Django REST Framework |
| База данных       | PostgreSQL 15 |
| Кэш / сессии      | Redis 7 (`django-redis`) |
| Платежи           | Робокасса (собственная интеграция, SHA-256 подпись) |
| Почта             | AWS SES / Mailgun (`django-anymail`) |
| Локализация       | `django-modeltranslation`, `gettext` (ru / kk / en) |
| Админка           | `django-jazzmin`, `django-import-export` |
| Frontend          | Django Templates, Bootstrap, jQuery, Slick, Daterangepicker, Google Maps |
| Инфраструктура    | Docker, Docker Compose, Nginx, Gunicorn, WhiteNoise |
| CI/CD             | GitHub Actions (тесты → SSH-деплой на сервер с автоматическим health-check и откатом) |
| Мониторинг        | Sentry, healthcheck-эндпоинты |

## Архитектура приложений

Проект разбит на слабо связанные Django-приложения, каждое отвечает за свою предметную область:

```
hotel/           # Отели, номера, бронирование, платежи, поиск, SEO (ядро домена)
booking/         # Недоступность номеров, проверка пересечений броней
addon/           # Дополнительные сервисы/удобства
userauths/       # Кастомный пользователь, аутентификация, согласия
user_dashboard/  # Личный кабинет гостя
search/          # Поиск и фильтрация отелей
robokassa/       # Интеграция с платёжным шлюзом
legal/           # Юридические документы и учёт согласий (в т.ч. для админки)
news/            # Новости/блог с категориями и галереями
```

Продакшн-окружение (`docker-compose.prod.yml`) состоит из пяти сервисов: `nginx` (реверс-прокси + раздача статики/медиа), `web` (Gunicorn), `booking_processor` (фоновый воркер, снимающий просроченные брони), `db` (PostgreSQL) и `redis`, каждый с health-check и настроенными лимитами ресурсов.

## Быстрый старт (локальная разработка)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
pip install -r requirements/base.txt
# для Windows дополнительно: pip install -r requirements/windows.txt

cp env_template.txt .env     # заполнить значения: SECRET_KEY, DB_*, REDIS_URL и т.д.

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

`collectstatic` обязателен даже для локальной разработки: `urls.py` отдаёт статику из `STATIC_ROOT` (`staticfiles/`), а не напрямую из `static/`. Каталог `staticfiles/` — генерируемый артефакт сборки и не хранится в git.

Каталог `media/` (загруженные пользователями файлы) также не хранится в git — Django создаёт его автоматически при первой загрузке файла.

Проекту требуются запущенные **PostgreSQL** и **Redis** (локально или через Docker) — соответствующие адреса указываются в `.env`.

### Docker (продакшен)

`docker-compose.prod.yml` уже выполняет `collectstatic` и `migrate` при старте контейнера `web` (см. секцию `command`), результат кладётся в именованный volume `static_volume` — руками ничего собирать не нужно:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Перед запуском нужен файл `.env.prod` (по образцу `env.prod.example`) со всеми продакшн-секретами.

## Переменные окружения

Полный шаблон — в [`env_template.txt`](env_template.txt). Основные группы настроек:

| Группа | Переменные |
|---|---|
| Django | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `WEBSITE_ADDRESS` |
| База данных | `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` |
| Redis | `REDIS_URL` |
| Почта | `EMAIL_BACKEND`, `DEFAULT_FROM_EMAIL`, `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` или `MAILGUN_API_KEY`/`MAILGUN_SENDER_DOMAIN` |
| Робокасса | `ROBOKASSA_MERCHANT_LOGIN`, `ROBOKASSA_MERCHANT_PASSWORD_1/2`, `ROBOKASSA_TEST_PASSWORD_1/2`, `ROBOKASSA_USE_TEST_MODE` |

## Тестирование

```bash
python manage.py test --settings=hms_prj.test_settings
```

В проекте свыше 160 тестов, покрывающих модели, вьюхи и платёжный флоу (`hotel`, `booking`, `search`, `userauths`, `robokassa`, `user_dashboard`). Тесты гоняются в CI против настоящих контейнеров PostgreSQL и Redis, а не моков — это ловит проблемы, которые не видны при подмене инфраструктуры.

## CI/CD

Пайплайн в [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) на каждый пуш в `main`:

1. Поднимает сервисы PostgreSQL и Redis, устанавливает зависимости из `requirements/test.txt`
2. Запускает `manage.py check` и полный набор тестов
3. При успехе — деплоит на продакшн-сервер по SSH: обновляет код, пересобирает и перезапускает Docker-контейнеры
4. Проверяет `/health/` после деплоя; при неудаче — автоматический откат к предыдущей версии `docker-compose.prod.yml`

---

<p align="center">Автор: Nurzhan Zhumatayev · <a href="https://github.com/Nurzhan-IT/Alakol">github.com/Nurzhan-IT/Alakol</a></p>
