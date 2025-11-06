#!/bin/bash

# Скрипт для ручного создания пользователя в v2ray
# Использование: ./create_user.sh <user_id>

if [ $# -ne 1 ]; then
    echo "Использование: $0 <user_id>"
    exit 1
fi

USER_ID=$1

# Проверяем, установлен ли Python и sqlite3
if ! command -v python3 &> /dev/null; then
    echo "Python3 не установлен"
    exit 1
fi

if ! command -v sqlite3 &> /dev/null; then
    echo "SQLite3 не установлен"
    exit 1
fi

# Добавляем пользователя в базу данных
echo "Добавляем пользователя $USER_ID в базу данных..."
python3 -c "
import sys
sys.path.append('../db')
from database import create_user
from datetime import datetime, timedelta
create_user($USER_ID, (datetime.now() + timedelta(days=30)).isoformat())
print('Пользователь добавлен в базу данных')
"

# Перезапускаем v2ray для обновления конфигурации
echo "Перезапускаем V2Ray..."
sudo systemctl restart v2ray

echo "Пользователь $USER_ID успешно создан"
