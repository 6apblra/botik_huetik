#!/bin/bash

# Скрипт для ручного удаления пользователя из v2ray
# Использование: ./remove_user.sh <user_id>

if [ $# -ne 1 ]; then
    echo "Использование: $0 <user_id>"
    exit 1
fi

USER_ID=$1

# Проверяем, установлен ли Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 не установлен"
    exit 1
fi

# Удаляем пользователя из базы данных
echo "Удаляем пользователя $USER_ID из базы данных..."
python3 -c "
import sys
sys.path.append('../db')
from database import update_subscription
update_subscription($USER_ID, None)
print('Статус подписки пользователя обновлен в базе данных')
"

# Перезапускаем v2ray для обновления конфигурации
echo "Перезапускаем V2Ray..."
sudo systemctl restart v2ray

echo "Пользователь $USER_ID успешно удален"
