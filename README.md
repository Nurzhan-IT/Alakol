# Alakol HMS

Django-система управления бронированием отеля.

## Локальный запуск

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements/base.txt

cp env_template.txt .env     # заполнить значения (SECRET_KEY, DB_*, REDIS_URL и т.д.)

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

`collectstatic` обязателен даже для локальной разработки: `urls.py` отдаёт статику из
`STATIC_ROOT` (`staticfiles/`), а не напрямую из `static/`. Каталог `staticfiles/` — генерируемый
артефакт сборки и не хранится в git.

Каталог `media/` (загруженные пользователями файлы) также не хранится в git — Django создаёт его
автоматически при первой загрузке файла.

## Docker (продакшен)

`docker-compose.prod.yml` уже выполняет `collectstatic` и `migrate` при старте контейнера `web`
(см. секцию `command`), результат кладётся в именованный volume `static_volume` — руками ничего
собирать не нужно:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```
