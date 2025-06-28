# Настройка Production окружения Alakol HMS

## Исправленные проблемы

✅ **Health check**: Теперь проверяет через Nginx на порт 80  
✅ **Nginx конфигурация**: Настроен HTTP сервер для health checks  
✅ **Docker Compose**: Убрано устаревшее предупреждение о version  

## Что нужно сделать перед запуском

### 1. Проверьте файл .env.prod

Убедитесь что у вас есть файл `.env.prod` с правильными настройками:

```bash
# Проверьте что файл существует
ls -la .env.prod

# Если нет, скопируйте из примера
cp .env.prod.example .env.prod
```

### 2. Настройте домен в nginx.conf (опционально)

Если у вас есть реальный домен, замените `YOUR_DOMAIN.com` в `nginx/nginx.conf`:

```bash
sed -i 's/YOUR_DOMAIN.com/your-real-domain.com/g' nginx/nginx.conf
```

### 3. Запустите развертывание

```bash
./scripts/deploy.sh
```

## Настройка HTTPS (после успешного запуска)

### 1. Установите certbot на сервере:

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

### 2. Получите SSL сертификат:

```bash
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com
```

### 3. Раскомментируйте HTTPS блок в nginx.conf:

```bash
# Замените YOUR_DOMAIN.com на ваш реальный домен
sed -i 's/YOUR_DOMAIN.com/your-real-domain.com/g' nginx/nginx.conf

# Раскомментируйте HTTPS блок
sed -i 's/# server {/server {/g' nginx/nginx.conf
sed -i 's/#     /     /g' nginx/nginx.conf
```

### 4. Добавьте HTTP -> HTTPS редирект:

Замените HTTP сервер на редирект:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 5. Перезапустите сервисы:

```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

## Мониторинг

### Проверка статуса:
```bash
./scripts/deploy.sh status
```

### Просмотр логов:
```bash
./scripts/deploy.sh logs
```

### Health check endpoints:
- `http://your-domain.com/health/` - Полная проверка здоровья
- `http://your-domain.com/ready/` - Готовность к трафику  
- `http://your-domain.com/live/` - Проверка что приложение живо

## Troubleshooting

### Если health check все еще не проходит:

1. **Проверьте логи:**
```bash
docker-compose -f docker-compose.prod.yml logs web --tail=50
docker-compose -f docker-compose.prod.yml logs nginx --tail=50
```

2. **Проверьте контейнеры:**
```bash
docker-compose -f docker-compose.prod.yml ps
```

3. **Проверьте доступность напрямую:**
```bash
# Внутри контейнера web
docker-compose -f docker-compose.prod.yml exec web curl http://localhost:8000/health/

# Через nginx
curl -H "Host: localhost" http://localhost:80/health/
```

4. **Проверьте настройки Django:**
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py check --settings=hms_prj.production_settings
```

### Если нужен откат:
```bash
./scripts/deploy.sh rollback
``` 