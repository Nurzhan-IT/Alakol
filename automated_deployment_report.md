# Отчет по автоматизированному развертыванию для Ubuntu VPS
## Проект: Alakol Hotel Management System (HMS)

### Обзор проекта и сервера

#### Детали проекта:
- **Фреймворк**: Django 4.2.2
- **База данных**: PostgreSQL
- **Кеширование**: Redis
- **Дополнительный компонент**: Скрипт для операций чтения/обновления модели hotel.booking
- **Основные приложения**: hotel, booking, userauths, legal, robokassa
- **Многоязычность**: Русский, Казахский, Английский
- **Платежные системы**: Robokassa

#### Спецификации сервера:
- **ОС**: Ubuntu VPS
- **Хранилище**: 100 GB NVMe (DC-серия)
- **vCPU**: 4 ядра
- **RAM**: 8 GB ECC (2933 MHz)
- **Сеть**: 1 IPv4, безлимитный трафик, 100+ Mbit/s
- **Особенности**: DDoS защита, root доступ, VNC

## 1. Автоматизированный процесс развертывания

### 1.1 Рекомендуемые инструменты автоматизации

**Рекомендация: GitHub Actions + Ansible**

**Обоснование выбора:**
- **GitHub Actions**: Бесплатный CI/CD для open-source проектов, простая интеграция с GitHub
- **Ansible**: Агентless, низкое потребление ресурсов, идеально для VPS с 4 vCPU/8GB RAM
- **Docker Compose**: Для контейнеризации без overhead'а полного Kubernetes

### 1.2 Пошаговый процесс настройки

#### Этап 1: Подготовка VPS окружения

```bash
# 1. Обновление системы
sudo apt update && sudo apt upgrade -y

# 2. Установка базовых пакетов
sudo apt install -y git curl wget unzip software-properties-common

# 3. Установка Docker и Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Установка Python и зависимостей
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo apt install -y postgresql-client redis-tools nginx certbot python3-certbot-nginx

# 5. Создание пользователя для деплоя
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy
sudo mkdir -p /home/deploy/.ssh
```

#### Этап 2: Настройка файрволла и безопасности

```bash
# Настройка UFW
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow from 10.0.0.0/8 to any port 5432  # PostgreSQL
sudo ufw allow from 10.0.0.0/8 to any port 6379  # Redis
```

#### Этап 3: Структура проекта для деплоя

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER} 
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "127.0.0.1:5432:5432"
    command: >
      postgres -c max_connections=100
               -c shared_buffers=256MB
               -c effective_cache_size=2GB
               -c work_mem=4MB
               -c maintenance_work_mem=64MB
               -c checkpoint_completion_target=0.9
               -c wal_buffers=16MB
               -c default_statistics_target=100

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: >
      redis-server --maxmemory 512mb
                   --maxmemory-policy allkeys-lru
                   --appendonly yes
                   --save 900 1
                   --save 300 10
                   --save 60 10000
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"

  web:
    build: .
    restart: unless-stopped
    environment:
      - DEBUG=False
      - DJANGO_SETTINGS_MODULE=hms_prj.production_settings
    env_file:
      - .env.prod
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./logs:/app/logs
    ports:
      - "127.0.0.1:8000:8000"
    depends_on:
      - db
      - redis
    command: >
      sh -c "python manage.py collectstatic --noinput --settings=hms_prj.production_settings &&
             python manage.py migrate --settings=hms_prj.production_settings &&
             gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 --worker-class gthread hms_prj.wsgi:application"

  booking_processor:
    build: .
    restart: unless-stopped
    environment:
      - DJANGO_SETTINGS_MODULE=hms_prj.production_settings
    env_file:
      - .env.prod
    volumes:
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    command: python manage.py booking_processor --settings=hms_prj.production_settings

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

## 2. Конфигурационные файлы

### 2.1 Dockerfile

```dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Создание директорий для логов и статики
RUN mkdir -p /app/logs /app/staticfiles /app/media

# Компиляция переводов
RUN python manage.py compilemessages --settings=hms_prj.production_settings

# Настройка пользователя
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "hms_prj.wsgi:application"]
```

### 2.2 Nginx конфигурация

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Логирование
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Оптимизация
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    upstream django {
        server web:8000;
    }

    # HTTP -> HTTPS редирект
    server {
        listen 80;
        server_name ekol.kz www.ekol.kz;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS сервер
    server {
        listen 443 ssl http2;
        server_name ekol.kz www.ekol.kz;

        # SSL сертификаты
        ssl_certificate /etc/letsencrypt/live/ekol.kz/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/ekol.kz/privkey.pem;
        
        # SSL настройки
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";

        # Статические файлы
        location /static/ {
            alias /app/staticfiles/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /app/media/;
            expires 1y;
            add_header Cache-Control "public";
        }

        # API endpoints с rate limiting
        location ~ ^/api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Админка и вход с дополнительным rate limiting
        location ~ ^/(admin|accounts/login)/ {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Основное приложение
        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
    }
}
```

### 2.3 GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies  
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
      run: |
        python manage.py test --settings=hms_prj.test_settings

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup SSH
      uses: webfactory/ssh-agent@v0.7.0
      with:
        ssh-privat-key: ${{ secrets.SSH_PRIVATE_KEY }}
    
    - name: Deploy to server
      run: |
        ssh -o StrictHostKeyChecking=no deploy@${{ secrets.HOST }} << 'EOF'
          cd /opt/alakol-hms
          git pull origin main
          docker-compose -f docker-compose.prod.yml down
          docker-compose -f docker-compose.prod.yml build --no-cache
          docker-compose -f docker-compose.prod.yml up -d
          
          # Проверка здоровья сервисов
          sleep 30
          curl -f http://localhost:8000/health/ || exit 1
        EOF
```

### 2.4 Ansible Playbook

```yaml
# playbook.yml  
---
- hosts: production
  become: yes
  vars:
    app_user: deploy
    app_path: /opt/alakol-hms
    
  tasks:
    - name: Install required packages
      apt:
        name:
          - docker.io
          - docker-compose
          - nginx
          - certbot
          - python3-certbot-nginx
          - postgresql-client
          - redis-tools
        state: present
        update_cache: yes

    - name: Create app user
      user:
        name: "{{ app_user }}"
        shell: /bin/bash
        groups: docker
        append: yes

    - name: Create app directory
      file:
        path: "{{ app_path }}"
        state: directory
        owner: "{{ app_user }}"
        group: "{{ app_user }}"

    - name: Clone repository
      git:
        repo: https://github.com/username/alakol-hms.git
        dest: "{{ app_path }}"
        version: main
      become_user: "{{ app_user }}"

    - name: Copy environment file
      template:
        src: .env.prod.j2
        dest: "{{ app_path }}/.env.prod"
        owner: "{{ app_user }}"
        mode: '0600'

    - name: Start services
      docker_compose:
        project_src: "{{ app_path }}"
        files:
          - docker-compose.prod.yml
        state: present
      become_user: "{{ app_user }}"

    - name: Setup SSL certificate
      command: >
        certbot --nginx --non-interactive --agree-tos 
        --email admin@ekol.kz -d ekol.kz -d www.ekol.kz
      args:
        creates: /etc/letsencrypt/live/ekol.kz/fullchain.pem

    - name: Setup automatic SSL renewal
      cron:
        name: "SSL renewal"
        minute: "0"
        hour: "12"
        job: "/usr/bin/certbot renew --quiet"
```

## 3. Стратегии оптимизации

### 3.1 Оптимизация Django

```python
# production_settings.py дополнения

# Оптимизация для 4 vCPU / 8GB RAM
import multiprocessing

# Gunicorn настройки
GUNICORN_WORKERS = min(4, (multiprocessing.cpu_count() * 2) + 1)
GUNICORN_THREADS = 2
GUNICORN_WORKER_CLASS = 'gthread'
GUNICORN_MAX_REQUESTS = 1000
GUNICORN_MAX_REQUESTS_JITTER = 100

# Кеширование
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 20,
                'retry_on_timeout': True,
            }
        },
        'KEY_PREFIX': 'alakol',
        'TIMEOUT': 300,
    }
}

# Кеширование сессий
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Оптимизация базы данных
DATABASES['default'].update({
    'CONN_MAX_AGE': 600,
    'OPTIONS': {
        'MAX_CONNS': 20,
        'OPTIONS': {
            '-c default_transaction_isolation=read committed'
        }
    }
})

# Логирование с ротацией
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django.log',
            'maxBytes': 50*1024*1024,  # 50MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### 3.2 Оптимизация PostgreSQL

```sql
-- postgresql.conf оптимизации для 8GB RAM
-- /var/lib/postgresql/data/postgresql.conf

# Общие настройки
max_connections = 100
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# Работа с логами
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0

# Индексы для модели Booking
CREATE INDEX CONCURRENTLY idx_booking_dates ON hotel_booking(check_in_date, check_out_date);
CREATE INDEX CONCURRENTLY idx_booking_status ON hotel_booking(payment_status) WHERE payment_status IN ('paid', 'processing', 'pending');
CREATE INDEX CONCURRENTLY idx_booking_active ON hotel_booking(is_active) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_booking_hotel_dates ON hotel_booking(hotel_id, check_in_date, check_out_date);
CREATE INDEX CONCURRENTLY idx_booking_expiry ON hotel_booking(expires_at) WHERE expires_at IS NOT NULL;
```

### 3.3 Интеграция вашего существующего services.py

**Ваш существующий скрипт лучше!** 

**Почему ваш `services.py` превосходит мой `booking_processor.py`:**

1. **Оптимизированные запросы**: Использует массовые обновления (`update()`) вместо циклов
2. **Предотвращение N+1**: Применяет `select_related` и `prefetch_related`
3. **Производительность**: Минимальное количество запросов к БД
4. **Простота**: Чистый и понятный код без избыточной логики

**Интеграция в деплой:**

```python
# management/commands/run_services.py - Wrapper для запуска вашего services.py
import time
import logging
from django.core.management.base import BaseCommand
from hotel.services import handle_bookings_payment_status_processing_to_unpaid

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs hotel services - processes booking status updates continuously'
    
    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, default=60,
                          help='Processing interval in seconds (default: 60)')
    
    def handle(self, *args, **options):
        interval = options['interval']
        logger.info(f"Starting hotel services processor with {interval}s interval")
        
        while True:
            try:
                # Вызываем вашу оптимизированную функцию
                result = handle_bookings_payment_status_processing_to_unpaid()
                logger.info(f"Service result: {result}")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Hotel services processor stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in hotel services processor: {e}")
                time.sleep(10)
```

**Дополнительные метрики для вашего services.py:**

```python
# Добавим в services.py для мониторинга
from django.core.cache import cache
import time

def handle_bookings_payment_status_processing_to_unpaid():
    """
    Улучшенная версия с метриками для Prometheus
    """
    start_time = time.time()
    
    try:
        expired_bookings = Booking.objects.filter(
            payment_status='processing',
            expires_at__lt=timezone.now()
        )
        
        booking_ids = list(expired_bookings.values_list('booking_id', flat=True)[:100])
        count = expired_bookings.update(payment_status='unpaid')
        
        # Метрики для мониторинга
        execution_time = time.time() - start_time
        cache.set('hms_last_booking_process_time', execution_time, 300)
        cache.set('hms_last_booking_process_count', count, 300)
        cache.set('hms_last_booking_process_timestamp', int(time.time()), 300)
        
        if count > 0:
            print(f"unpaid {count} expired bookings: {', '.join(booking_ids[:5])}{'...' if len(booking_ids) > 5 else ''}")
        
        return f"unpaid {count} expired bookings in {execution_time:.2f}s"
        
    except Exception as e:
        cache.set('hms_last_booking_process_error', str(e), 300)
        print(f"Error cleaning expired bookings: {str(e)}")
        return f"Error: {str(e)}"
```

**Обновленный docker-compose.prod.yml:**

```yaml
  services_processor:
    build: 
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      - DJANGO_SETTINGS_MODULE=hms_prj.production_settings
    env_file:
      - .env.prod
    volumes:
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    # Запускаем ваш services.py через wrapper
    command: python manage.py run_services --settings=hms_prj.production_settings --interval 60
```

## 4. Меры безопасности и надежности

### 4.1 Настройки безопасности

```bash
# security_setup.sh
#!/bin/bash

# SSH hardening
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
echo "AllowUsers deploy" >> /etc/ssh/sshd_config
sudo systemctl restart ssh

# Fail2ban setup
sudo apt install fail2ban -y
sudo tee /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 600
bantime = 7200
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 4.2 Стратегия резервного копирования

```bash
# backup_script.sh
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Создание директорий
mkdir -p $BACKUP_DIR/{database,media,logs}

# Backup PostgreSQL
docker-compose -f /opt/alakol-hms/docker-compose.prod.yml exec -T db pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/database/db_backup_$DATE.sql.gz

# Backup media files
rsync -av /opt/alakol-hms/media/ $BACKUP_DIR/media/

# Backup logs
tar -czf $BACKUP_DIR/logs/logs_$DATE.tar.gz /opt/alakol-hms/logs/

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -type f -mtime +7 -delete

# Upload to remote storage (optional)
# aws s3 sync $BACKUP_DIR s3://alakol-backups/
```

### 4.3 Мониторинг с Prometheus + Grafana

#### Конфигурация Prometheus

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

scrape_configs:
  # Системные метрики
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node_exporter:9100']
    scrape_interval: 30s

  # PostgreSQL метрики
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres_exporter:9187']
    scrape_interval: 30s

  # Redis метрики
  - job_name: 'redis'
    static_configs:
      - targets: ['redis_exporter:9121']
    scrape_interval: 30s

  # Django метрики (если добавить django-prometheus)
  - job_name: 'django'
    static_configs:
      - targets: ['web:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # Nginx метрики
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    metrics_path: '/nginx_status'
    scrape_interval: 30s
```

#### Правила алертинга

```yaml
# monitoring/rules.yml
groups:
  - name: system
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[2m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 5 minutes"

      - alert: DiskSpaceLow
        expr: node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100 < 15
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Disk space is below 15%"

  - name: database
    rules:
      - alert: PostgreSQLDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is down"
          description: "PostgreSQL database is not responding"

      - alert: PostgreSQLTooManyConnections
        expr: pg_stat_database_numbackends / pg_settings_max_connections * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL has too many connections"
          description: "PostgreSQL connection usage is above 80%"

  - name: redis
    rules:
      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis is down"
          description: "Redis cache is not responding"

      - alert: RedisMemoryUsage
        expr: redis_memory_used_bytes / redis_memory_max_bytes * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage is high"
          description: "Redis memory usage is above 90%"

  - name: application
    rules:
      - alert: DjangoDown
        expr: up{job="django"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Django application is down"
          description: "Django web application is not responding"

      - alert: HighResponseTime
        expr: django_http_requests_latency_seconds{quantile="0.95"} > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time"
          description: "95th percentile response time is above 2 seconds"
```

#### Grafana Dashboard для Hotel Management System

```json
# monitoring/grafana/dashboards/hms-dashboard.json
{
  "dashboard": {
    "id": null,
    "title": "Alakol HMS Monitoring",
    "tags": ["hms", "django", "hotel"],
    "timezone": "Asia/Yekaterinburg",
    "panels": [
      {
        "title": "System Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "up",
            "legendFormat": "{{job}} Status"
          }
        ]
      },
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[2m])) * 100)",
            "legendFormat": "CPU Usage %"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
            "legendFormat": "Memory Usage %"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "Active Connections"
          }
        ]
      },
      {
        "title": "Redis Memory",
        "type": "graph",
        "targets": [
          {
            "expr": "redis_memory_used_bytes",
            "legendFormat": "Used Memory"
          }
        ]
      },
      {
        "title": "HTTP Requests Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(django_http_requests_total[5m])",
            "legendFormat": "{{method}} {{status}}"
          }
        ]
      },
      {
        "title": "Booking Status Distribution",
        "type": "piechart",
        "targets": [
          {
            "expr": "django_model_objects_total{model=\"booking\"}",
            "legendFormat": "{{status}}"
          }
        ]
      }
    ],
    "refresh": "30s",
    "time": {
      "from": "now-1h",
      "to": "now"
    }
  }
}
```

## 5. Пример рабочего процесса развертывания

### 5.1 Полный workflow развертывания

```bash
#!/bin/bash
# deploy.sh - Main deployment script

set -e

echo "🚀 Starting deployment..."

# 1. Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# 2. Build new images
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# 3. Run database migrations
echo "🗄️ Running migrations..."
docker-compose -f docker-compose.prod.yml run --rm web python manage.py migrate --settings=hms_prj.production_settings

# 4. Collect static files  
echo "📁 Collecting static files..."
docker-compose -f docker-compose.prod.yml run --rm web python manage.py collectstatic --noinput --settings=hms_prj.production_settings

# 5. Start services with zero-downtime
echo "🔄 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# 6. Health check
echo "🏥 Performing health check..."
sleep 30
if curl -f http://localhost:8000/health/; then
    echo "✅ Deployment successful!"
else
    echo "❌ Health check failed, rolling back..."
    docker-compose -f docker-compose.prod.yml down
    exit 1
fi

# 7. Cleanup old images
echo "🧹 Cleaning up..."
docker image prune -f

echo "🎉 Deployment completed successfully!"
```

### 5.2 Откат при ошибках

```bash
#!/bin/bash
# rollback.sh

echo "🔄 Rolling back to previous version..."

# Stop current services
docker-compose -f docker-compose.prod.yml down

# Restore from backup
if [ -f "./docker-compose.backup.yml" ]; then
    mv docker-compose.backup.yml docker-compose.prod.yml
    docker-compose -f docker-compose.prod.yml up -d
    echo "✅ Rollback completed"
else
    echo "❌ No backup found for rollback"
    exit 1
fi
```

## 6. Рекомендации по производительности

### 6.1 Распределение ресурсов

| Сервис | CPU | RAM | Обоснование |
|--------|-----|-----|-------------|
| Django (Gunicorn) | 2.5 vCPU | 3GB | Основное приложение |
| PostgreSQL | 1 vCPU | 2.5GB | База данных с буферами |
| Redis | 0.25 vCPU | 512MB | Кеширование |
| Nginx | 0.25 vCPU | 256MB | Прокси и статика |
| Booking Processor | 0.25 vCPU | 512MB | Фоновые задачи |
| System/Other | - | 1.2GB | ОС и мониторинг |

### 6.2 Оптимизация NVMe storage

```bash
# Настройка файловой системы для NVMe
sudo mkfs.ext4 -F /dev/nvme0n1p1
echo '/dev/nvme0n1p1 /opt ext4 defaults,noatime,discard 0 2' >> /etc/fstab

# Оптимизация I/O scheduler
echo 'none' | sudo tee /sys/block/nvme0n1/queue/scheduler

# Docker оптимизация для NVMe
sudo tee /etc/docker/daemon.json << EOF
{
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "data-root": "/opt/docker"
}
EOF
```

## 7. Заключение

Данная конфигурация обеспечивает:

- **Автоматизированное развертывание** с CI/CD через GitHub Actions
- **Высокую производительность** на заданном железе (4 vCPU/8GB RAM)
- **Безопасность** с HTTPS, файрволлом и мониторингом
- **Надежность** с резервным копированием и системой rollback
- **Масштабируемость** для умеренного трафика отельной системы

**Следующие шаги:**
1. Настроить SSH ключи и доступы
2. Выполнить Ansible playbook для базовой настройки
3. Настроить GitHub Actions с секретами
4. Выполнить первое развертывание
5. Настроить мониторинг и алерты
6. Протестировать backup/restore процедуры

Система готова к обработке бронирований отелей с высокой доступностью и производительностью.