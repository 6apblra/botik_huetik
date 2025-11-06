#!/bin/bash

# Скрипт развертывания VPN-сервиса на Ubuntu 24.04
# Запускать с правами sudo

set -e  # Выход при ошибке

echo "Начинаем установку VPN-сервиса..."

# Обновляем систему
apt update && apt upgrade -y

# Устанавливаем Python 3.10+ и pip
apt install -y python3 python3-pip python3-venv

# Устанавливаем Git
apt install -y git

# Устанавливаем v2ray
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)

# Включаем автозапуск v2ray
systemctl enable v2ray
systemctl start v2ray

# Устанавливаем ufw и настраиваем
apt install -y ufw
ufw allow ssh
ufw allow 443/tcp
ufw --force enable

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости Python
pip install -r requirements.txt

# Создаем директории для конфигов и логов
mkdir -p /var/log/v2ray
mkdir -p configs
mkdir -p qrcodes

# Копируем пример .env файла, если он не существует
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Создан файл .env. Пожалуйста, настройте его с вашими токенами."
fi

# Создаем базу данных
python3 -c "
import sys
sys.path.append('db')
from database import init_db
init_db()
print('База данных инициализирована')
"

# Делаем скрипты исполняемыми
chmod +x scripts/*.sh

echo "Установка завершена!"
echo "Пожалуйста, настройте .env файл с вашими токенами и запустите бота командой:"
echo "source venv/bin/activate && python bot/bot.py"
