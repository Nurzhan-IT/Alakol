# ИНСТРУМЕНТЫ МОНИТОРИНГА И ТЕСТИРОВАНИЯ ПРОИЗВОДИТЕЛЬНОСТИ

# 1. Базовые системные инструменты
BASIC_MONITORING = """
# Установка базовых инструментов:
sudo apt update
sudo apt install htop iotop nethogs vnstat sysstat atop glances

# Мониторинг CPU и памяти:
htop                    # Интерактивный мониторинг процессов
glances                 # Комплексный мониторинг системы
atop                    # Детальная статистика системы

# Мониторинг сети:
nethogs                 # Мониторинг трафика по процессам
vnstat                  # Статистика сетевого трафика
ss -tuln               # Активные соединения
netstat -i             # Статистика интерфейсов

# Мониторинг дисков:
iotop                  # I/O операции в реальном времени
iostat 1               # Статистика I/O каждую секунду
df -h                  # Использование дискового пространства
"""

# 2. Специализированные инструменты для Django
DJANGO_MONITORING = """
# Django Debug Toolbar (только для development):
pip install django-debug-toolbar

# В settings.py добавить:
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']

# Django Silk для профилирования:
pip install django-silk

INSTALLED_APPS += ['silk']
MIDDLEWARE += ['silk.middleware.SilkyMiddleware']

# Monitoring с Django Extensions:
pip install django-extensions
INSTALLED_APPS += ['django_extensions']

# Команды для анализа:
python manage.py show_urls           # Показать все URL
python manage.py graph_models        # Граф моделей
python manage.py runprofileserver    # Профилирование сервера
"""

# 3. Инструменты нагрузочного тестирования
LOAD_TESTING = """
# Apache Benchmark (ab):
sudo apt install apache2-utils

# Тестирование главной страницы:
ab -n 1000 -c 10 http://localhost:8000/

# Тестирование с keep-alive:
ab -n 1000 -c 10 -k http://localhost:8000/

# wrk - современная альтернатива ab:
sudo apt install wrk

# Тест на 30 секунд с 12 потоками и 400 соединениями:
wrk -t12 -c400 -d30s http://localhost:8000/

# hey - простой инструмент нагрузочного тестирования:
wget https://storage.googleapis.com/hey-release/hey_linux_amd64
chmod +x hey_linux_amd64
sudo mv hey_linux_amd64 /usr/local/bin/hey

# Тест с 200 запросами и 50 одновременными соединениями:
hey -n 200 -c 50 http://localhost:8000/

# Locust для сложных сценариев тестирования:
pip install locust

# Создать locustfile.py:
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_hotels(self):
        self.client.get("/")
    
    @task(1)
    def view_hotel_detail(self):
        self.client.get("/hotel/test-hotel/")

# Запуск: locust -f locustfile.py --host=http://localhost:8000
"""

# 4. Мониторинг базы данных PostgreSQL
POSTGRESQL_MONITORING = """
# Встроенные инструменты PostgreSQL:

# Просмотр активных запросов:
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

# Статистика по таблицам:
SELECT schemaname,tablename,attname,n_distinct,correlation 
FROM pg_stats 
WHERE tablename = 'hotel_hotel';

# Размеры таблиц:
SELECT 
    tablename, 
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;

# Медленные запросы (если включено логирование):
sudo tail -f /var/log/postgresql/postgresql-14-main.log | grep "duration:"

# pgBadger для анализа логов:
sudo apt install pgbadger
pgbadger /var/log/postgresql/postgresql-14-main.log
"""

# 5. Настройка Prometheus + Grafana
PROMETHEUS_GRAFANA = """
# Установка Prometheus:
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
sudo mv prometheus-*/ /opt/prometheus
sudo useradd --no-create-home --shell /bin/false prometheus
sudo chown -R prometheus:prometheus /opt/prometheus

# Конфигурация Prometheus (/opt/prometheus/prometheus.yml):
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'django-app'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

# Установка Node Exporter:
wget https://github.com/prometheus/node_exporter/releases/download/v1.4.0/node_exporter-1.4.0.linux-amd64.tar.gz
tar xvfz node_exporter-*.tar.gz
sudo mv node_exporter-*/node_exporter /usr/local/bin/

# Systemd сервис для Node Exporter (/etc/systemd/system/node_exporter.service):
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=prometheus
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target

# Установка Grafana:
sudo apt install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt update
sudo apt install grafana

# Запуск сервисов:
sudo systemctl enable --now prometheus node_exporter grafana-server
"""

# 6. Мониторинг приложения Django
APPLICATION_MONITORING = """
# django-prometheus для метрик:
pip install django-prometheus

# В settings.py:
INSTALLED_APPS += ['django_prometheus']

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... остальные middleware ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django_prometheus.db.backends.postgresql',
        # ... остальные настройки ...
    }
}

# В urls.py:
urlpatterns += [
    path('metrics/', include('django_prometheus.urls')),
]

# Кастомные метрики в views.py:
from prometheus_client import Counter, Histogram
import time

REQUEST_COUNT = Counter('hotel_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('hotel_request_duration_seconds', 'Request latency')

def hotel_detail(request, slug):
    start_time = time.time()
    REQUEST_COUNT.labels(method=request.method, endpoint='hotel_detail').inc()
    
    try:
        # ... основная логика ...
        pass
    finally:
        REQUEST_LATENCY.observe(time.time() - start_time)
"""

# 7. Автоматические алерты
ALERTING = """
# Создать скрипт мониторинга alert_system.sh:
#!/bin/bash

# Параметры мониторинга
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=90
EMAIL="admin@alakol.com"

# Проверка CPU
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )); then
    echo "ALERT: CPU usage is ${cpu_usage}%" | mail -s "High CPU Alert" $EMAIL
fi

# Проверка памяти
memory_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $memory_usage -gt $MEMORY_THRESHOLD ]; then
    echo "ALERT: Memory usage is ${memory_usage}%" | mail -s "High Memory Alert" $EMAIL
fi

# Проверка диска
disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $disk_usage -gt $DISK_THRESHOLD ]; then
    echo "ALERT: Disk usage is ${disk_usage}%" | mail -s "High Disk Alert" $EMAIL
fi

# Проверка доступности сайта
if ! curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "ALERT: Website is down" | mail -s "Website Down Alert" $EMAIL
fi

# Добавить в crontab для запуска каждые 5 минут:
# */5 * * * * /path/to/alert_system.sh
"""

print("Эффект: Предотвращение деградации производительности")
print("Время внедрения: 2-3 дня")
print("Сложность: Средняя-Высокая")