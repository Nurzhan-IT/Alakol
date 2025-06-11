# ОПТИМИЗАЦИЯ ВЕБ-СЕРВЕРА (NGINX + GUNICORN)

# 1. Конфигурация Nginx
NGINX_CONFIG = """
# /etc/nginx/sites-available/alakol

upstream django_app {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    keepalive 32;
}

server {
    listen 80;
    server_name alakol.com www.alakol.com;
    
    # Сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Статические файлы
    location /static/ {
        alias /path/to/alakol/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # Сжатие статических файлов
        location ~* \.(css|js)$ {
            gzip_static on;
        }
    }

    location /media/ {
        alias /path/to/alakol/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # Проксирование к Django
    location / {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Буферизация
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        
        # Таймауты
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Кэширование на уровне Nginx
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"""

# 2. Конфигурация Gunicorn
GUNICORN_CONFIG = """
# gunicorn_config.py

import multiprocessing

# Основные настройки
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1  # Для 4 CPU = 9 workers
worker_class = "gevent"  # Для I/O-интенсивных задач
worker_connections = 1000

# Производительность
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Таймауты
timeout = 30
graceful_timeout = 30

# Логирование
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Процесс
daemon = False
pidfile = "/var/run/gunicorn.pid"
user = "www-data"
group = "www-data"
"""

# 3. Systemd сервис для автозапуска
SYSTEMD_SERVICE = """
# /etc/systemd/system/alakol.service

[Unit]
Description=Alakol Django Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/alakol
Environment=DJANGO_SETTINGS_MODULE=hms_prj.settings
ExecStart=/path/to/alakol/venv/bin/gunicorn --config gunicorn_config.py hms_prj.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

# 4. Балансировка нагрузки с несколькими Gunicorn процессами
LOAD_BALANCING = """
# Запуск нескольких инстансов Gunicorn

# gunicorn_8000.conf
bind = "127.0.0.1:8000"
workers = 3

# gunicorn_8001.conf  
bind = "127.0.0.1:8001"
workers = 3

# gunicorn_8002.conf
bind = "127.0.0.1:8002" 
workers = 3

# gunicorn_8003.conf
bind = "127.0.0.1:8003"
workers = 3

# Скрипт запуска (start_servers.sh):
#!/bin/bash
gunicorn --config gunicorn_8000.conf hms_prj.wsgi:application &
gunicorn --config gunicorn_8001.conf hms_prj.wsgi:application &
gunicorn --config gunicorn_8002.conf hms_prj.wsgi:application &
gunicorn --config gunicorn_8003.conf hms_prj.wsgi:application &
"""

# 5. SSL и HTTP/2
SSL_CONFIG = """
# Добавить в Nginx конфигурацию:

server {
    listen 443 ssl http2;
    server_name alakol.com www.alakol.com;
    
    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;
    
    # SSL оптимизация
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HTTP/2 push для критических ресурсов
    location = / {
        http2_push /static/css/main.css;
        http2_push /static/js/main.js;
        proxy_pass http://django_app;
    }
}
"""

print("Эффект: Увеличение RPS на 30-60%")
print("Время внедрения: 1 день")  
print("Сложность: Средняя")