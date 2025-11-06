# Быстрый запуск на сервере

## 1. Подключение к серверу

```bash
ssh user@194.150.220.158
```

## 2. Клонирование репозитория

```bash
cd ~
git clone https://github.com/6apblra/botik_huetik.git
cd botik_huetik
```

## 3. Установка зависимостей

```bash
# Создать виртуальное окружение
python3 -m venv venv

# Активировать
source venv/bin/activate

# Установить пакеты
pip install -r requirements.txt
```

## 4. Запуск

```bash
# Активировать venv (если не активировано)
source venv/bin/activate

# Запустить бота
python3 run.py
```

## 5. Запуск в фоне (screen)

```bash
# Установить screen (если не установлен)
sudo apt install screen -y

# Создать сессию
screen -S vpnbot

# Активировать venv и запустить
cd ~/botik_huetik
source venv/bin/activate
python3 run.py

# Отключиться от сессии: Ctrl+A, затем D

# Подключиться обратно
screen -r vpnbot

# Остановить бота: Ctrl+C в сессии screen
```

## 6. Запуск как systemd сервис (рекомендуется)

```bash
# Создать файл сервиса
sudo nano /etc/systemd/system/vpnbot.service
```

Вставьте:

```ini
[Unit]
Description=VPN Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/botik_huetik
ExecStart=/home/YOUR_USERNAME/botik_huetik/venv/bin/python3 /home/YOUR_USERNAME/botik_huetik/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Замените `YOUR_USERNAME` на ваше имя пользователя!**

```bash
# Перезагрузить systemd
sudo systemctl daemon-reload

# Запустить сервис
sudo systemctl start vpnbot

# Добавить в автозагрузку
sudo systemctl enable vpnbot

# Проверить статус
sudo systemctl status vpnbot

# Посмотреть логи
sudo journalctl -u vpnbot -f

# Остановить
sudo systemctl stop vpnbot

# Перезапустить
sudo systemctl restart vpnbot
```

## 7. Обновление кода

```bash
cd ~/botik_huetik

# Остановить бота (если используется systemd)
sudo systemctl stop vpnbot

# Получить обновления
git pull

# Обновить зависимости (если изменились)
source venv/bin/activate
pip install -r requirements.txt

# Запустить снова
sudo systemctl start vpnbot
```

## Проверка работы

1. Откройте бота в Telegram
2. Отправьте `/start`
3. Должно прийти приветствие

## Решение проблем

### Бот не отвечает

```bash
# Проверить логи
sudo journalctl -u vpnbot -n 50

# Проверить статус
sudo systemctl status vpnbot
```

### Ошибка прав доступа

Убедитесь, что в `.env` установлено:
```
MOCK_V2RAY=true
```

### Проверить, что Python 3.10+

```bash
python3 --version
```

Если версия ниже 3.10:

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv -y
```
