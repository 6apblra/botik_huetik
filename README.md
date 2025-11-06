# VPN-сервис с Telegram-ботом и оплатой через PayPalych

Этот проект реализует полный функционал VPN-сервиса с автоматизированным управлением подписками через Telegram-бота и систему оплаты через PayPalych (pally.info).

## Особенности

- Автоматическая активация VPN-доступа после оплаты
- Управление пользователями через Telegram-бота
- Интеграция с PayPalych для обработки платежей
- Автоматическое отключение пользователей по окончании подписки
- Поддержка QR-кодов и конфигурационных файлов для подключения
- Режим тестирования (MOCK) без реального V2Ray

## Требования

- Ubuntu 24.04 (или другой Linux)
- Python 3.10+
- V2Ray (опционально, для реального VPN)
- Доступ к API PayPalych (pally.info)

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/6apblra/botik_huetik.git
cd botik_huetik
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Отредактируйте файл `.env` (используйте `.env.example` как шаблон):

```bash
# Токен Telegram-бота от @BotFather
BOT_TOKEN=ваш_токен

# API-ключ PayPalych (pally.info)
PAYPALYCH_API_KEY=ваш_ключ

# IP-адрес VPN-сервера
VPN_SERVER_IP=ваш_ip

# ID администратора (ваш Telegram ID)
ADMIN_ID=ваш_id

# Режим тестирования (без реального V2Ray)
MOCK_V2RAY=true
```

### 5. (Опционально) Установка V2Ray

Если хотите использовать реальный VPN (уберите `MOCK_V2RAY=true` из .env):

```bash
# Установка V2Ray
bash <(curl -L https://raw.githubusercontent.com/v2fly/fhs-install-v2ray/master/install-release.sh)

# Проверка
v2ray version

# Настройка прав доступа
sudo mkdir -p /etc/v2ray
sudo chown $USER:$USER /etc/v2ray
```

## Запуск

### Режим тестирования (MOCK)

```bash
source venv/bin/activate
python3 run.py
```

### Реальный режим (с V2Ray)

Уберите `MOCK_V2RAY=true` из .env и запустите с sudo:

```bash
sudo python3 run.py
```

Или настройте sudo без пароля:

```bash
sudo visudo
# Добавьте:
your_user ALL=(ALL) NOPASSWD: /bin/systemctl restart v2ray
```

## Использование

### Команды бота

- `/start` - Приветствие и список команд
- `/buy` - Купить подписку
- `/status` - Проверить статус подписки
- `/renew` - Продлить подписку

## Решение проблем

### Ошибка: "Permission denied" при записи в /etc/v2ray

**Решение:**
```bash
# Вариант 1: Запуск с sudo
sudo python3 run.py

# Вариант 2: Использовать MOCK режим
# Добавьте в .env:
MOCK_V2RAY=true
```

### Ошибка: "systemctl: command not found"

**Решение:**
```bash
# Используйте MOCK режим
MOCK_V2RAY=true
```

### Просмотр логов

```bash
python3 run.py 2>&1 | tee bot.log
```

## Структура проекта

```
botik_huetik/
├── bot/              # Логика Telegram-бота
│   ├── bot.py        # Основной файл бота
│   ├── handlers.py   # Обработчики команд
│   └── paypalych_api.py  # Интеграция с PayPalych
├── db/               # Работа с базой данных
│   └── database.py   # SQLite база
├── vpn/              # Управление V2Ray
│   └── vpn_manager.py # Логика V2Ray
├── scripts/          # Скрипты развертывания
├── run.py            # Точка входа
├── requirements.txt  # Зависимости
├── .env              # Переменные окружения
└── README.md         # Документация
```

## Безопасность

⚠️ **Важно:** Не коммитьте файл `.env` с реальными токенами!

```bash
# Удалить .env из репозитория
git rm --cached .env
git commit -m "Remove .env from repository"
git push
```

## Лицензия

MIT License
