#!/bin/bash

# Alakol HMS Production Deployment Script
# Использование: ./scripts/deploy.sh

set -e

echo "🚀 Начинаем развертывание Alakol HMS..."

# Функция для логирования
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Функция для проверки требований
check_requirements() {
    log "Проверяем требования..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker не установлен!"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose не установлен!"
        exit 1
    fi
    
    if [ ! -f ".env.prod" ]; then
        echo "❌ Файл .env.prod не найден!"
        echo "Скопируйте env.prod.example в .env.prod и настройте переменные"
        exit 1
    fi
    
    log "✅ Все требования выполнены"
}

# Функция для резервного копирования
backup() {
    log "Создаем резервную копию..."
    
    # Создаем директорию для бэкапов
    mkdir -p backups
    
    # Сохраняем текущую конфигурацию
    if [ -f "docker-compose.prod.yml" ]; then
        cp docker-compose.prod.yml docker-compose.backup.yml
        log "✅ Конфигурация сохранена"
    fi
    
    # Бэкап базы данных (если контейнер запущен)
    if docker-compose -f docker-compose.prod.yml ps db | grep -q "Up"; then
        log "Создаем бэкап базы данных..."
        BACKUP_NAME="db_backup_$(date +%Y%m%d_%H%M%S).sql"
        docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U $DB_USER $DB_NAME | gzip > backups/$BACKUP_NAME.gz
        log "✅ Бэкап базы данных создан: backups/$BACKUP_NAME.gz"
    fi
}

# Функция для развертывания
deploy() {
    log "Начинаем развертывание..."
    
    # Создаем необходимые директории
    mkdir -p logs media/static
    
    # Останавливаем текущие контейнеры
    log "Останавливаем текущие контейнеры..."
    docker-compose -f docker-compose.prod.yml down || true
    
    # Собираем новые образы
    log "Собираем образы..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    # Запускаем сервисы
    log "Запускаем сервисы..."
    docker-compose -f docker-compose.prod.yml up -d
    
    log "✅ Сервисы запущены"
}

# Функция для проверки работоспособности
health_check() {
    log "Проверяем работоспособность..."
    
    # Ждем запуска
    log "Ожидание запуска сервисов (60 секунд)..."
    sleep 60
    
    # Проверяем статус контейнеров
    if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        echo "❌ Некоторые контейнеры не запустились!"
        docker-compose -f docker-compose.prod.yml ps
        echo "Логи:"
        docker-compose -f docker-compose.prod.yml logs --tail=20
        return 1
    fi
    
    # Проверяем health endpoint
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "Попытка $attempt/$max_attempts проверки health endpoint..."
        
        # Сначала пробуем через Nginx на порт 80
        if curl -f -H "Host: localhost" http://localhost:80/health/ > /dev/null 2>&1; then
            log "✅ Health check прошел успешно через Nginx!"
            return 0
        fi
        
        # Если не получилось, пробуем напрямую к Django (для отладки)
        if docker-compose -f docker-compose.prod.yml exec -T web curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
            log "✅ Health check прошел успешно напрямую к Django!"
            log "⚠️  Но Nginx может быть недоступен - проверьте конфигурацию"
            return 0
        fi
        
        sleep 10
        ((attempt++))
    done
    
    echo "❌ Health check не прошел после $max_attempts попыток!"
    echo "Логи Nginx:"
    docker-compose -f docker-compose.prod.yml logs nginx --tail=10
    echo "Логи Django:"
    docker-compose -f docker-compose.prod.yml logs web --tail=10
    return 1
}

# Функция для отката
rollback() {
    log "Выполняем откат..."
    
    docker-compose -f docker-compose.prod.yml down || true
    
    if [ -f "docker-compose.backup.yml" ]; then
        mv docker-compose.backup.yml docker-compose.prod.yml
        docker-compose -f docker-compose.prod.yml up -d
        log "✅ Откат выполнен"
    else
        log "❌ Файл для отката не найден"
    fi
}

# Функция для отображения статуса
show_status() {
    log "Статус сервисов:"
    docker-compose -f docker-compose.prod.yml ps
    
    log "Использование ресурсов:"
    docker stats --no-stream
    
    log "Последние логи:"
    docker-compose -f docker-compose.prod.yml logs --tail=10
}

# Основная функция
main() {
    case "${1:-deploy}" in
        "deploy")
            check_requirements
            backup
            deploy
            
            if health_check; then
                log "🎉 Развертывание завершено успешно!"
                show_status
                
                # Очистка старых образов
                log "Очистка старых образов..."
                docker image prune -f
                
                # Удаляем файл бэкапа конфигурации
                rm -f docker-compose.backup.yml
            else
                log "❌ Развертывание не удалось, выполняем откат..."
                rollback
                exit 1
            fi
            ;;
        "rollback")
            rollback
            ;;
        "status")
            show_status
            ;;
        "logs")
            docker-compose -f docker-compose.prod.yml logs -f
            ;;
        "stop")
            docker-compose -f docker-compose.prod.yml down
            log "✅ Сервисы остановлены"
            ;;
        "start")
            docker-compose -f docker-compose.prod.yml up -d
            log "✅ Сервисы запущены"
            ;;
        *)
            echo "Использование: $0 {deploy|rollback|status|logs|stop|start}"
            echo ""
            echo "Команды:"
            echo "  deploy   - Полное развертывание (по умолчанию)"
            echo "  rollback - Откат к предыдущей версии"
            echo "  status   - Показать статус сервисов"
            echo "  logs     - Показать логи в реальном времени"
            echo "  stop     - Остановить все сервисы"
            echo "  start    - Запустить все сервисы"
            exit 1
            ;;
    esac
}

# Запуск основной функции
main "$@" 