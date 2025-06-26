# 🚀 Руководство по развертыванию Alakol HMS

Это руководство поможет вам развернуть проект Alakol Hotel Management System на вашем VPS сервере с использованием Docker.

## 📋 Требования

- **VPS сервер**: Ubuntu 20.04/22.04
- **Ресурсы**: минимум 4 vCPU, 8GB RAM, 100GB SSD
- **Домен**: настроенный домен с A-записью на ваш сервер
- **SSH доступ**: к серверу с правами sudo

## 🛠 Быстрый старт

### 1. Настройка сервера (выполняется один раз)

```bash
# Подключитесь к серверу
ssh root@your-server-ip

<<<<<<< dev
# Поскольку репозиторий приватный, создайте скрипт вручную:
nano server_setup.sh

# Скопируйте содержимое из scripts/server_setup.sh вашего локального репозитория
# Затем сделайте файл исполняемым и запустите:
=======
# Скачайте и запустите скрипт настройки
wget https://raw.githubusercontent.com/12farit21/Alakol/main/scripts/server_setup.sh
>>>>>>> main
chmod +x server_setup.sh
sudo ./server_setup.sh
```

### 2. Настройка SSH ключей

```bash
# На локальной машине сгенерируйте SSH ключ (если его нет)
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Скопируйте публичный ключ на сервер
ssh-copy-id deploy@your-server-ip

# Или добавьте ключ вручную
ssh root@your-server-ip
echo "YOUR_PUBLIC_KEY" >> /home/deploy/.ssh/authorized_keys
chown deploy:deploy /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys
```

### 2.1. Настройка SSH ключей для GitHub (приватный репозиторий)

```bash
# На сервере как пользователь deploy
ssh deploy@your-server-ip

# Сгенерируйте SSH ключ для GitHub
ssh-keygen -t rsa -b 4096 -C "deploy@your-server"

# Выведите публичный ключ
cat ~/.ssh/id_rsa.pub

# Скопируйте вывод и добавьте в GitHub:
# Settings → SSH and GPG keys → New SSH key
```

### 3. Клонирование проекта

```bash
# Подключитесь как пользователь deploy
ssh deploy@your-server-ip

# Перейдите в директорию проекта
cd /opt/alakol-hms

<<<<<<< dev
# Для приватного репозитория используйте SSH или Personal Access Token:

# Вариант 1: SSH (рекомендуется)
git clone git@github.com:12farit21/Alakol.git .

# Вариант 2: HTTPS с Personal Access Token
# git clone https://ghp_YOUR_TOKEN@github.com/12farit21/Alakol.git .
=======
# Клонируйте репозиторий
git clone https://github.com/12farit21/Alakol.git .
>>>>>>> main
```

### 4. Настройка переменных окружения

```bash
# Скопируйте пример файла окружения
cp env.prod.example .env.prod

# Отредактируйте переменные
nano .env.prod
```

**Обязательные переменные для изменения:**
```bash
# Сгенерируйте секретный ключ
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Вставьте в .env.prod
SECRET_KEY=generated_secret_key_here
DOMAIN_NAME=ekol.kz

# Настройте базу данных
DB_NAME=alakol_hms_prod
DB_USER=alakol_user
DB_PASSWORD=strong_password_here

# Настройки Robokassa (получите в личном кабинете)
ROBOKASSA_MERCHANT_LOGIN=your_login
ROBOKASSA_MERCHANT_PASSWORD_1=password1
ROBOKASSA_MERCHANT_PASSWORD_2=password2
```

### 5. Развертывание

```bash
# Сделайте скрипт исполняемым
chmod +x scripts/deploy.sh

# Запустите развертывание
./scripts/deploy.sh
```

### 6. Настройка SSL сертификата

```bash
# Обновите nginx конфигурацию с вашим доменом
sudo nano /opt/alakol-hms/nginx/nginx.conf
# Замените YOUR_DOMAIN.com на ваш домен

# Перезапустите nginx
sudo systemctl restart nginx

# Получите SSL сертификат
sudo certbot --nginx -d ekol.kz -d www.ekol.kz
```

## 🔧 Конфигурационные файлы

### Основные файлы для редактирования:

1. **`.env.prod`** - переменные окружения
2. **`nginx/nginx.conf`** - конфигурация веб-сервера
3. **`docker-compose.prod.yml`** - конфигурация Docker сервисов

### Важные директории:

- `/opt/alakol-hms/logs/` - логи приложения
- `/opt/alakol-hms/backups/` - резервные копии
- `/opt/alakol-hms/media/` - загруженные файлы

## 🚀 GitHub Actions (Автоматический деплой)

### Настройка секретов в GitHub:

1. Перейдите в Settings → Secrets and variables → Actions
2. Добавьте следующие секреты:

```
HOST=your-server-ip
SSH_USER=deploy
DEPLOY_PATH=/opt/alakol-hms
DOMAIN_NAME=ekol.kz
SSH_PRIVATE_KEY=содержимое_приватного_ключа
```

### Получение приватного ключа:

```bash
# На локальной машине
cat ~/.ssh/id_rsa
# Скопируйте весь вывод в SSH_PRIVATE_KEY
```

После настройки каждый push в ветку `main` будет автоматически деплоить изменения.

## 📊 Мониторинг и управление

### Полезные команды:

```bash
# Статус сервисов
./scripts/deploy.sh status

# Просмотр логов
./scripts/deploy.sh logs

# Остановка сервисов
./scripts/deploy.sh stop

# Запуск сервисов
./scripts/deploy.sh start

# Откат к предыдущей версии
./scripts/deploy.sh rollback
```

### Проверка работоспособности:

```bash
# Health check
curl http://localhost:8000/health/

# Статус Docker контейнеров
docker-compose -f docker-compose.prod.yml ps

# Логи конкретного сервиса
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs booking_processor
```

## 🔒 Безопасность

### Настройки выполняемые автоматически:

- ✅ SSH настроен только с ключами
- ✅ Firewall (UFW) настроен
- ✅ Fail2Ban защита от брутфорса
- ✅ Автоматические обновления безопасности
- ✅ SSL сертификаты

### Рекомендации:

1. **Регулярные обновления**: система обновляется автоматически
2. **Бэкапы**: создаются автоматически при каждом деплое
3. **Мониторинг логов**: проверяйте `/var/log/system-monitor.log`

## 📋 Резервное копирование

### Автоматическое резервное копирование:

Создается при каждом деплое:
- База данных: `backups/db_backup_YYYYMMDD_HHMMSS.sql.gz`
- Конфигурация: `docker-compose.backup.yml`

### Ручное создание бэкапа:

```bash
# Бэкап базы данных
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U $DB_USER $DB_NAME | gzip > backup_$(date +%Y%m%d).sql.gz

# Бэкап медиа файлов
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

### Восстановление из бэкапа:

```bash
# Восстановление базы данных
gunzip -c backup_file.sql.gz | docker-compose -f docker-compose.prod.yml exec -T db psql -U $DB_USER -d $DB_NAME
```

## 🐛 Устранение неисправностей

### Часто встречающиеся проблемы:

1. **Контейнер не запускается**
   ```bash
   docker-compose -f docker-compose.prod.yml logs service_name
   ```

2. **Ошибка подключения к базе данных**
   ```bash
   # Проверьте переменные в .env.prod
   # Убедитесь что PostgreSQL контейнер работает
   docker-compose -f docker-compose.prod.yml ps db
   ```

3. **SSL сертификат не работает**
   ```bash
   sudo certbot certificates
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. **Booking processor не работает**
   ```bash
   # Проверьте логи
   docker-compose -f docker-compose.prod.yml logs booking_processor
   
   # Проверьте health check
   curl http://localhost:8000/health/
   ```

### Получение помощи:

- Логи приложения: `/opt/alakol-hms/logs/`
- Логи системы: `/var/log/system-monitor.log`
- Логи nginx: `/var/log/nginx/`

## 📈 Производительность

### Оптимизации для VPS 8GB RAM:

- **PostgreSQL**: настроен для 2GB shared_buffers
- **Redis**: лимит памяти 512MB
- **Gunicorn**: 4 воркера, 2 потока на воркер
- **Nginx**: сжатие gzip, кеширование статики

### Мониторинг ресурсов:

```bash
# Использование ресурсов контейнерами
docker stats

# Системные ресурсы
htop

# Дисковое пространство
df -h
```

## 🔄 Обновления

### Автоматические обновления:

Через GitHub Actions при push в `main`.

### Ручное обновление:

```bash
cd /opt/alakol-hms
git pull origin main
./scripts/deploy.sh
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи в `/opt/alakol-hms/logs/`
2. Запустите `./scripts/deploy.sh status`
3. Проверьте health endpoint: `curl http://localhost:8000/health/`

## 🎉 Готово!

После выполнения всех шагов ваш сайт будет доступен по адресу `https://ekol.kz`

- **Админка**: `https://ekol.kz/admin/`
- **API здоровья**: `https://ekol.kz/health/`
- **Готовность**: `https://ekol.kz/ready/` 