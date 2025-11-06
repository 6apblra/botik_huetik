import json
import os
import subprocess
import asyncio
import logging
from datetime import datetime
from db.database import get_user
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

VPN_SERVER_IP = os.getenv("VPN_SERVER_IP", "127.0.0.1")
V2RAY_CONFIG_PATH = os.getenv("V2RAY_CONFIG_PATH", "/etc/v2ray/config.json")
MOCK_MODE = os.getenv("MOCK_V2RAY", "false").lower() == "true"  # Режим тестирования

# Шаблон конфигурации для v2ray
V2RAY_CONFIG_TEMPLATE = {
    "log": {
        "access": "/var/log/v2ray/access.log",
        "error": "/var/log/v2ray/error.log",
        "loglevel": "info"
    },
    "inbounds": [
        {
            "port": 443,
            "protocol": "vless",
            "settings": {
                "clients": []
            },
            "streamSettings": {
                "network": "tcp",
                "security": "tls",
                "tlsSettings": {
                    "certificates": [
                        {
                            "certificateFile": "/path/to/certificate.crt",
                            "keyFile": "/path/to/private.key"
                        }
                    ]
                }
            }
        }
    ],
    "outbounds": [
        {
            "protocol": "freedom",
            "settings": {}
        }
    ]
}

async def initialize_v2ray_server():
    """
    Инициализирует v2ray сервер с начальной конфигурацией
    """
    if MOCK_MODE:
        logger.info("V2Ray: режим тестирования (MOCK), инициализация пропущена")
        return
    
    try:
        # Создаем директорию для конфигов, если не существует
        config_dir = os.path.dirname(V2RAY_CONFIG_PATH)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
            logger.info(f"Создана директория: {config_dir}")
        
        # Проверяем, существует ли конфигурация, если нет - создаем базовую
        if not os.path.exists(V2RAY_CONFIG_PATH):
            with open(V2RAY_CONFIG_PATH, 'w') as f:
                json.dump(V2RAY_CONFIG_TEMPLATE, f, indent=2)
            logger.info(f"Создана базовая конфигурация V2Ray: {V2RAY_CONFIG_PATH}")
        
        # Перезапускаем v2ray сервис
        result = subprocess.run(
            ["systemctl", "restart", "v2ray"], 
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("V2Ray сервер успешно инициализирован")
        
    except PermissionError as e:
        logger.error(f"Нет прав для записи в {V2RAY_CONFIG_PATH}. Запустите с sudo или измените права: {e}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при запуске V2Ray: {e.stderr}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при инициализации V2Ray: {e}", exc_info=True)

async def create_v2ray_user(user_id: int):
    """
    Добавляет нового пользователя в конфигурацию v2ray
    """
    if MOCK_MODE:
        import uuid
        user_uuid = str(uuid.uuid4())
        from db.database import save_user_v2ray_id
        save_user_v2ray_id(user_id, user_uuid)
        logger.info(f"V2Ray (MOCK): пользователь {user_id} создан с UUID {user_uuid}")
        return
    
    try:
        # Генерируем UUID для пользователя
        import uuid
        user_uuid = str(uuid.uuid4())
        
        # Читаем текущую конфигурацию
        if not os.path.exists(V2RAY_CONFIG_PATH):
            logger.error(f"Конфигурация V2Ray не найдена: {V2RAY_CONFIG_PATH}")
            return
            
        with open(V2RAY_CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        # Добавляем нового клиента
        new_client = {
            "id": user_uuid,
            "flow": "xtls-rprx-vision",
            "level": 0,
            "email": f"user_{user_id}@vpn.example.com"
        }
        
        # Проверяем, что пользователь не существует
        existing_clients = config['inbounds'][0]['settings']['clients']
        client_exists = any(client.get('email') == new_client['email'] for client in existing_clients)
        
        if not client_exists:
            existing_clients.append(new_client)
        
        # Сохраняем конфигурацию
        with open(V2RAY_CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Сохраняем UUID пользователя в базе данных
        from db.database import save_user_v2ray_id
        save_user_v2ray_id(user_id, user_uuid)
        
        # Перезапускаем v2ray
        subprocess.run(["systemctl", "restart", "v2ray"], check=True, capture_output=True)
        logger.info(f"Пользователь {user_id} успешно добавлен в V2Ray")
        
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя {user_id} в V2Ray: {e}", exc_info=True)

async def remove_v2ray_user(user_id: int):
    """
    Удаляет пользователя из конфигурации v2ray
    """
    if MOCK_MODE:
        logger.info(f"V2Ray (MOCK): пользователь {user_id} удален")
        return
    
    try:
        # Получаем UUID пользователя из базы
        from db.database import get_user_v2ray_id
        user_uuid = get_user_v2ray_id(user_id)
        
        if not user_uuid:
            logger.warning(f"UUID для пользователя {user_id} не найден")
            return
        
        # Читаем текущую конфигурацию
        with open(V2RAY_CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        # Удаляем клиента
        clients = config['inbounds'][0]['settings']['clients']
        updated_clients = [client for client in clients if client['id'] != user_uuid]
        config['inbounds'][0]['settings']['clients'] = updated_clients
        
        # Сохраняем конфигурацию
        with open(V2RAY_CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Перезапускаем v2ray
        subprocess.run(["systemctl", "restart", "v2ray"], check=True, capture_output=True)
        logger.info(f"Пользователь {user_id} удален из V2Ray")
        
    except Exception as e:
        logger.error(f"Ошибка при удалении пользователя {user_id}: {e}", exc_info=True)

def generate_v2ray_config(user_id: int):
    """
    Генерирует конфигурационный файл для конкретного пользователя
    """
    try:
        user = get_user(user_id)
        if not user:
            raise ValueError(f"Пользователь {user_id} не найден")
        
        # Получаем UUID пользователя из базы
        from db.database import get_user_v2ray_id
        user_uuid = get_user_v2ray_id(user_id)
        
        if not user_uuid:
            raise ValueError(f"UUID для пользователя {user_id} не найден")
        
        # Создаем конфигурацию для клиента
        client_config = {
            "remarks": f"VPN Config for User {user_id}",
            "v": "2",
            "ps": f"VPN for User {user_id}",
            "add": VPN_SERVER_IP,
            "port": "443",
            "id": user_uuid,
            "aid": "0",
            "net": "tcp",
            "type": "none",
            "host": "",
            "path": "",
            "tls": "tls"
        }
        
        # Сохраняем конфигурацию в файл
        config_dir = "configs"
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, f"user_{user_id}_config.json")
        
        with open(config_path, 'w') as f:
            json.dump(client_config, f, indent=2)
        
        logger.info(f"Конфигурация для пользователя {user_id} создана: {config_path}")
        
        return {
            "file_path": config_path,
            "config": client_config
        }
    except Exception as e:
        logger.error(f"Ошибка при генерации конфигурации для {user_id}: {e}", exc_info=True)
        raise

def generate_v2ray_qr(user_id: int):
    """
    Генерирует QR-код для подключения к VPN
    """
    try:
        import qrcode
        from io import BytesIO
        
        user = get_user(user_id)
        if not user:
            raise ValueError(f"Пользователь {user_id} не найден")
        
        # Получаем UUID пользователя из базы
        from db.database import get_user_v2ray_id
        user_uuid = get_user_v2ray_id(user_id)
        
        if not user_uuid:
            raise ValueError(f"UUID для пользователя {user_id} не найден")
        
        # Формируем vless URL
        vless_url = f"vless://{user_uuid}@{VPN_SERVER_IP}:443?security=tls&type=tcp#VPN-User-{user_id}"
        
        # Создаем QR-код
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(vless_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')
        
        # Сохраняем QR-код
        qr_dir = "qrcodes"
        os.makedirs(qr_dir, exist_ok=True)
        qr_path = os.path.join(qr_dir, f"user_{user_id}_qr.png")
        img.save(qr_path)
        
        logger.info(f"QR-код для пользователя {user_id} создан: {qr_path}")
        
        return qr_path
    except Exception as e:
        logger.error(f"Ошибка при генерации QR-кода для {user_id}: {e}", exc_info=True)
        raise
