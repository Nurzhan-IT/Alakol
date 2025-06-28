#!/bin/bash

# Alakol HMS Server Setup Script
# Скрипт для первоначальной настройки Ubuntu VPS сервера
# Использование: ./scripts/server_setup.sh

set -e

echo "🚀 Настройка VPS сервера для Alakol HMS..."

# Функция для логирования
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Проверка что скрипт запущен от root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "❌ Этот скрипт должен быть запущен от root"
        echo "Используйте: sudo ./scripts/server_setup.sh"
        exit 1
    fi
}

# Обновление системы
update_system() {
    log "Обновляем систему..."
    apt update && apt upgrade -y
    apt install -y curl wget git unzip software-properties-common
    log "✅ Система обновлена"
}

# Установка Docker
install_docker() {
    log "Устанавливаем Docker..."
    
    # Удаляем старые версии
    apt remove -y docker docker-engine docker.io containerd runc || true
    
    # Устанавливаем Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    
    # Добавляем пользователя в группу docker
    usermod -aG docker $USER
    
    # Устанавливаем Docker Compose
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Проверяем установку
    docker --version
    docker-compose --version
    
    log "✅ Docker установлен"
}

# Установка дополнительных пакетов
install_packages() {
    log "Устанавливаем дополнительные пакеты..."
    
    apt install -y \
        nginx \
        certbot \
        python3-certbot-nginx \
        postgresql-client \
        redis-tools \
        htop \
        fail2ban \
        ufw \
        rsync \
        cron
    
    log "✅ Дополнительные пакеты установлены"
}

# Настройка файрволла
setup_firewall() {
    log "Настраиваем файрволл..."
    
    # Включаем UFW
    ufw --force enable
    
    # Настраиваем правила
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80
    ufw allow 443
    
    # Локальные сервисы
    ufw allow from 127.0.0.1 to any port 5432  # PostgreSQL
    ufw allow from 127.0.0.1 to any port 6379  # Redis
    ufw allow from 127.0.0.1 to any port 8000  # Django
    
    ufw status
    
    log "✅ Файрволл настроен"
}

# Настройка SSH
setup_ssh() {
    log "Настраиваем SSH..."
    
    # Создаем резервную копию
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # # Отключаем root login
    # sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    # sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    
    # # Отключаем аутентификацию по паролю
    # sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    # sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    
    # Перезапускаем SSH
    systemctl restart ssh
    
    log "✅ SSH настроен"
}

# Настройка Fail2Ban
setup_fail2ban() {
    log "Настраиваем Fail2Ban..."
    
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
ignoreip = 127.0.0.1/8

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 600
bantime = 7200
EOF

    systemctl enable fail2ban
    systemctl start fail2ban
    
    log "✅ Fail2Ban настроен"
}

# Создание пользователя для деплоя
create_deploy_user() {
    log "Создаем пользователя для деплоя..."
    
    # Создаем пользователя
    useradd -m -s /bin/bash deploy || true
    usermod -aG docker deploy
    
    # Создаем директорию для SSH ключей
    mkdir -p /home/deploy/.ssh
    chmod 700 /home/deploy/.ssh
    chown deploy:deploy /home/deploy/.ssh
    
    # Создаем директорию для проекта
    mkdir -p /opt/alakol-hms
    chown deploy:deploy /opt/alakol-hms
    
    log "✅ Пользователь deploy создан"
    log "Добавьте ваш SSH ключ в /home/deploy/.ssh/authorized_keys"
}

# Настройка Nginx
setup_nginx() {
    log "Настраиваем Nginx..."
    
    # Удаляем дефолтный сайт
    rm -f /etc/nginx/sites-enabled/default
    
    # Создаем базовую конфигурацию
    cat > /etc/nginx/sites-available/alakol-hms << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}
EOF

    # Включаем сайт
    ln -sf /etc/nginx/sites-available/alakol-hms /etc/nginx/sites-enabled/
    
    # Проверяем конфигурацию
    nginx -t
    
    # Перезапускаем Nginx
    systemctl restart nginx
    systemctl enable nginx
    
    log "✅ Nginx настроен"
}

# Настройка автоматических обновлений
setup_auto_updates() {
    log "Настраиваем автоматические обновления..."
    
    apt install -y unattended-upgrades
    
    # Настраиваем автоматические обновления безопасности
    cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

    # Включаем автоматические обновления
    dpkg-reconfigure -plow unattended-upgrades
    
    log "✅ Автоматические обновления настроены"
}

# Настройка мониторинга
setup_monitoring() {
    log "Настраиваем базовый мониторинг..."
    
    # Создаем скрипт для мониторинга
    cat > /usr/local/bin/system-monitor.sh << 'EOF'
#!/bin/bash
# Простой скрипт мониторинга системы

DATE=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="/var/log/system-monitor.log"

echo "[$DATE] System Monitor Check" >> $LOG_FILE

# Проверка использования диска
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# Проверка использования памяти
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "[$DATE] WARNING: Memory usage is ${MEM_USAGE}%" >> $LOG_FILE
fi

# Проверка Docker сервисов
if command -v docker-compose &> /dev/null; then
    cd /opt/alakol-hms
    if [ -f "docker-compose.prod.yml" ]; then
        if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
            echo "[$DATE] ERROR: Some Docker services are down" >> $LOG_FILE
        fi
    fi
fi
EOF

    chmod +x /usr/local/bin/system-monitor.sh
    
    # Добавляем в cron
    (crontab -l 2>/dev/null; echo "*/15 * * * * /usr/local/bin/system-monitor.sh") | crontab -
    
    log "✅ Базовый мониторинг настроен"
}

# Оптимизация для NVMe
optimize_nvme() {
    log "Оптимизируем для NVMe..."
    
    # Настройка планировщика I/O
    echo 'SUBSYSTEM=="block", KERNEL=="nvme*", ATTR{queue/scheduler}="none"' > /etc/udev/rules.d/60-nvme-scheduler.rules
    
    # Настройка sysctl для производительности
    cat >> /etc/sysctl.conf << 'EOF'

# Alakol HMS Performance Optimizations
vm.swappiness=10
vm.vfs_cache_pressure=50
net.core.somaxconn=1024
net.ipv4.tcp_max_syn_backlog=2048
net.core.netdev_max_backlog=2000
EOF

    sysctl -p
    
    log "✅ NVMe оптимизация применена"
}

# Основная функция
main() {
    log "Начинаем настройку сервера..."
    
    check_root
    update_system
    install_docker
    install_packages
    setup_firewall
    setup_ssh
    setup_fail2ban
    create_deploy_user
    setup_nginx
    setup_auto_updates
    setup_monitoring
    optimize_nvme
    
    log "🎉 Настройка сервера завершена!"
    log ""
    log "Следующие шаги:"
    log "1. Добавьте SSH ключ в /home/deploy/.ssh/authorized_keys"
    log "2. Клонируйте проект в /opt/alakol-hms"
    log "3. Настройте .env.prod файл"
    log "4. Запустите деплой: ./scripts/deploy.sh"
    log "5. Настройте SSL сертификат: certbot --nginx -d your-domain.com"
    log ""
    log "Рекомендуется перезагрузить сервер для применения всех изменений."
}

# Запуск
main "$@" 