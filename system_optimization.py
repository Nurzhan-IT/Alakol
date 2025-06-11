# ОПТИМИЗАЦИЯ СИСТЕМЫ UBUNTU 22.04

# 1. Настройка сетевых параметров ядра
KERNEL_NETWORK_TUNING = """
# /etc/sysctl.conf

# TCP оптимизация
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr

# Увеличение лимитов соединений
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 8096
net.ipv4.ip_local_port_range = 1024 65535

# Оптимизация TIME_WAIT
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30

# Быстрое освобождение памяти
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# Применить изменения:
# sudo sysctl -p
"""

# 2. Настройка лимитов файловых дескрипторов
FILE_LIMITS = """
# /etc/security/limits.conf

* soft nofile 65536
* hard nofile 65536
* soft nproc 65536  
* hard nproc 65536

# /etc/systemd/system.conf
DefaultLimitNOFILE=65536
DefaultLimitNPROC=65536

# Для текущего пользователя:
ulimit -n 65536
"""

# 3. Настройка Receive Packet Steering (RPS)
RPS_CONFIGURATION = """
#!/bin/bash
# rps_setup.sh - Настройка RPS для распределения сетевых прерываний

# Получаем количество CPU
cpu_count=$(nproc)
rps_mask=$((2**cpu_count - 1))

# Настраиваем RPS для всех сетевых интерфейсов
for interface in /sys/class/net/*/queues/rx-*/rps_cpus; do
    if [ -f "$interface" ]; then
        echo $rps_mask | sudo tee "$interface" > /dev/null
        echo "RPS настроен для $interface: $rps_mask"
    fi
done

# Настройка XPS (Transmit Packet Steering)
for interface in /sys/class/net/*/queues/tx-*/xps_cpus; do
    if [ -f "$interface" ]; then
        echo $rps_mask | sudo tee "$interface" > /dev/null
        echo "XPS настроен для $interface: $rps_mask"
    fi
done

# Добавить в /etc/rc.local для автоматического запуска:
# /path/to/rps_setup.sh
"""

# 4. Настройка памяти и swap
MEMORY_OPTIMIZATION = """
# Создание и настройка swap файла
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Добавить в /etc/fstab:
# /swapfile none swap sw 0 0

# Настройка параметров памяти в /etc/sysctl.conf:
vm.swappiness = 10                    # Минимальное использование swap
vm.vfs_cache_pressure = 50           # Сохранение кэша файловой системы
vm.dirty_ratio = 15                  # Процент "грязной" памяти
vm.dirty_background_ratio = 5        # Фоновая запись на диск
vm.overcommit_memory = 1             # Разрешить overcommit памяти
"""

# 5. Настройка планировщика I/O
IO_SCHEDULER = """
# Проверить текущий планировщик:
cat /sys/block/sda/queue/scheduler

# Установить mq-deadline для SSD (рекомендуется):
echo mq-deadline | sudo tee /sys/block/sda/queue/scheduler

# Сделать постоянным в /etc/udev/rules.d/60-ioschedulers.rules:
ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="0", ATTR{queue/scheduler}="mq-deadline"
ACTION=="add|change", KERNEL=="sd[a-z]", ATTR{queue/rotational}=="1", ATTR{queue/scheduler}="bfq"
"""

# 6. Настройка CPU governor
CPU_GOVERNOR = """
# Установить производительный режим CPU:
sudo apt install cpufrequtils

# Установить performance governor:
sudo cpufreq-set -g performance

# Сделать постоянным в /etc/default/cpufrequtils:
GOVERNOR="performance"

# Или использовать ondemand для баланса:
GOVERNOR="ondemand"
"""

# 7. Мониторинг системных ресурсов
MONITORING_SETUP = """
# Установить инструменты мониторинга:
sudo apt update
sudo apt install htop iotop nethogs vnstat sysstat

# Настроить сбор статистики (sar):
sudo systemctl enable sysstat

# Создать скрипт мониторинга performance_monitor.sh:
#!/bin/bash

while true; do
    echo "=== $(date) ==="
    echo "CPU Load:"
    uptime
    echo ""
    
    echo "Memory Usage:"
    free -h
    echo ""
    
    echo "Network Connections:"
    ss -tuln | wc -l
    echo ""
    
    echo "Top Processes:"
    ps aux --sort=-%cpu | head -6
    echo ""
    
    sleep 30
done >> /var/log/performance.log 2>&1
"""

print("Эффект: Увеличение RPS на 20-40%")
print("Время внедрения: 0.5-1 день")
print("Сложность: Низкая-Средняя")