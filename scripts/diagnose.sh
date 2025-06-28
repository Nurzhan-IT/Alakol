#!/bin/bash

# Alakol HMS Production Diagnostics Script
# Использование: ./scripts/diagnose.sh

set -e

echo "🔍 Диагностика Alakol HMS Production..."

# Функция для логирования
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Проверка Docker контейнеров
check_containers() {
    log "📦 Проверка Docker контейнеров..."
    
    echo "Статус контейнеров:"
    docker-compose -f docker-compose.prod.yml ps || echo "❌ Не удалось получить статус контейнеров"
    
    echo -e "\nПроцессы внутри контейнеров:"
    docker-compose -f docker-compose.prod.yml top || echo "❌ Не удалось получить процессы"
    
    echo -e "\nИспользование ресурсов:"
    docker stats --no-stream || echo "❌ Не удалось получить статистику"
}

# Проверка сетевых подключений
check_network() {
    log "🌐 Проверка сетевых подключений..."
    
    echo "Открытые порты:"
    netstat -tlnp | grep -E ':(80|443|8000|5432|6379)' || echo "Нет открытых портов"
    
    echo -e "\nDocker сети:"
    docker network ls | grep alakol || echo "Нет Docker сетей"
    
    # Проверка доступности сервисов
    echo -e "\nПроверка внутренних сервисов:"
    
    # Проверка PostgreSQL
    if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ PostgreSQL доступен"
    else
        echo "❌ PostgreSQL недоступен"
    fi
    
    # Проверка Redis
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis доступен"
    else
        echo "❌ Redis недоступен"
    fi
    
    # Проверка Django
    if docker-compose -f docker-compose.prod.yml exec -T web curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
        echo "✅ Django health check успешен"
    else
        echo "❌ Django health check неуспешен"
    fi
    
    # Проверка Nginx
    if curl -f -H "Host: localhost" http://localhost:80/health/ > /dev/null 2>&1; then
        echo "✅ Nginx проксирование работает"
    else
        echo "❌ Nginx проксирование не работает"
    fi
}

# Проверка логов
check_logs() {
    log "📋 Проверка логов (последние 20 строк)..."
    
    echo "=== Логи Django (web) ==="
    docker-compose -f docker-compose.prod.yml logs web --tail=20 || echo "❌ Не удалось получить логи web"
    
    echo -e "\n=== Логи Nginx ==="
    docker-compose -f docker-compose.prod.yml logs nginx --tail=20 || echo "❌ Не удалось получить логи nginx"
    
    echo -e "\n=== Логи PostgreSQL ==="
    docker-compose -f docker-compose.prod.yml logs db --tail=20 || echo "❌ Не удалось получить логи db"
    
    echo -e "\n=== Логи Redis ==="
    docker-compose -f docker-compose.prod.yml logs redis --tail=20 || echo "❌ Не удалось получить логи redis"
    
    echo -e "\n=== Логи Booking Processor ==="
    docker-compose -f docker-compose.prod.yml logs booking_processor --tail=20 || echo "❌ Не удалось получить логи booking_processor"
}

# Проверка конфигурации
check_configuration() {
    log "⚙️  Проверка конфигурации..."
    
    echo "Файлы конфигурации:"
    ls -la docker-compose.prod.yml nginx/nginx.conf .env.prod 2>/dev/null || echo "❌ Некоторые файлы конфигурации отсутствуют"
    
    echo -e "\nПроверка Nginx конфигурации:"
    docker-compose -f docker-compose.prod.yml exec nginx nginx -t 2>&1 || echo "❌ Ошибка в конфигурации Nginx"
    
    echo -e "\nПроверка Django настроек:"
    docker-compose -f docker-compose.prod.yml exec web python manage.py check --settings=hms_prj.production_settings 2>&1 || echo "❌ Ошибка в настройках Django"
    
    echo -e "\nПеременные окружения Django:"
    docker-compose -f docker-compose.prod.yml exec web env | grep -E "(DEBUG|DJANGO_SETTINGS_MODULE|DB_)" || echo "❌ Переменные окружения не найдены"
}

# Проверка дискового пространства
check_disk_space() {
    log "💾 Проверка дискового пространства..."
    
    echo "Использование диска:"
    df -h | head -n 1
    df -h | grep -E "(/$|/opt|/var)"
    
    echo -e "\nРазмер Docker образов:"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep -E "(alakol|postgres|redis|nginx)" || echo "Нет образов Alakol"
    
    echo -e "\nРазмер Docker volumes:"
    docker system df
}

# Тест health endpoints
test_health_endpoints() {
    log "🏥 Тестирование health endpoints..."
    
    endpoints=("/health/" "/ready/" "/live/")
    
    for endpoint in "${endpoints[@]}"; do
        echo "Тестирование $endpoint:"
        
        # Через Nginx
        if curl -f -H "Host: localhost" "http://localhost:80$endpoint" > /dev/null 2>&1; then
            echo "  ✅ Через Nginx: OK"
        else
            echo "  ❌ Через Nginx: FAIL"
        fi
        
        # Напрямую к Django
        if docker-compose -f docker-compose.prod.yml exec -T web curl -f "http://localhost:8000$endpoint" > /dev/null 2>&1; then
            echo "  ✅ Напрямую к Django: OK"
        else
            echo "  ❌ Напрямую к Django: FAIL"
        fi
    done
}

# Рекомендации по исправлению
show_recommendations() {
    log "💡 Рекомендации по исправлению проблем..."
    
    echo "1. Если контейнеры не запускаются:"
    echo "   - Проверьте логи: docker-compose -f docker-compose.prod.yml logs"
    echo "   - Проверьте .env.prod файл"
    echo "   - Проверьте доступность портов: netstat -tlnp"
    
    echo -e "\n2. Если health check не проходит:"
    echo "   - Убедитесь что nginx конфигурация правильная"
    echo "   - Проверьте доступность Django: curl -H 'Host: localhost' http://localhost:80/health/"
    echo "   - Проверьте Django settings: docker-compose -f docker-compose.prod.yml exec web python manage.py check"
    
    echo -e "\n3. Если проблемы с базой данных:"
    echo "   - Проверьте подключение: docker-compose -f docker-compose.prod.yml exec db pg_isready"
    echo "   - Проверьте переменные окружения DB_*"
    echo "   - Выполните миграции: docker-compose -f docker-compose.prod.yml exec web python manage.py migrate"
    
    echo -e "\n4. Если проблемы с производительностью:"
    echo "   - Проверьте использование ресурсов: docker stats"
    echo "   - Проверьте дисковое пространство: df -h"
    echo "   - Очистите старые образы: docker image prune"
}

# Основная функция
main() {
    case "${1:-all}" in
        "containers")
            check_containers
            ;;
        "network")
            check_network
            ;;
        "logs")
            check_logs
            ;;
        "config")
            check_configuration
            ;;
        "disk")
            check_disk_space
            ;;
        "health")
            test_health_endpoints
            ;;
        "recommendations")
            show_recommendations
            ;;
        "all")
            check_containers
            echo -e "\n" && check_network
            echo -e "\n" && check_configuration
            echo -e "\n" && test_health_endpoints
            echo -e "\n" && check_disk_space
            echo -e "\n" && show_recommendations
            ;;
        *)
            echo "Использование: $0 {all|containers|network|logs|config|disk|health|recommendations}"
            echo ""
            echo "Команды:"
            echo "  all            - Полная диагностика (по умолчанию)"
            echo "  containers     - Проверка Docker контейнеров"
            echo "  network        - Проверка сетевых подключений"
            echo "  logs           - Показать последние логи"
            echo "  config         - Проверка конфигурации"
            echo "  disk           - Проверка дискового пространства"
            echo "  health         - Тестирование health endpoints"
            echo "  recommendations - Рекомендации по исправлению"
            exit 1
            ;;
    esac
}

# Запуск
main "$@" 