import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# PAYPALYCH_API_KEY = os.getenv("PAYPALYCH_API_KEY")  # Закомментируем, т.к. не используется в заглушке
PAYPALYCH_BASE_URL = "https://pally.info/api/v1"  # Не используется в заглушке

# Словарь для хранения симуляции платежей (в реальном приложении используйте БД)
# Формат: {payment_id: {'status': 'pending|completed|failed|cancelled', 'user_id': int}}
_mock_payments = {}

async def create_payment_link(amount: float, currency: str, description: str, user_id: int):
    """
    Создает ссылку для оплаты через PayPalych (заглушка)
    """
    # Генерируем уникальный ID платежа
    import uuid
    payment_id = str(uuid.uuid4())

    # Сохраняем симуляцию платежа
    _mock_payments[payment_id] = {
        'status': 'pending',
        'user_id': user_id,
        'amount': amount,
        'currency': currency
    }

    # Возвращаем фиктивный URL для оплаты
    # В реальном приложении здесь был бы реальный URL от PayPalych
    fake_payment_url = f"https://example.com/mock-payment/{payment_id}"  # Замените на реальный URL, если нужно

    print(f"[DEBUG] Создан фиктивный платеж: ID={payment_id}, Пользователь={user_id}, Сумма={amount} {currency}")

    return {
        "payment_id": payment_id,
        "payment_url": fake_payment_url
    }

async def check_payment_status(payment_id: str):
    """
    Проверяет статус платежа через PayPalych (заглушка)
    Возвращает: 'pending', 'completed', 'failed', 'cancelled'
    """
    payment_info = _mock_payments.get(payment_id)
    if not payment_info:
        print(f"[DEBUG] Платеж с ID {payment_id} не найден в симуляции.")
        return "unknown"

    # В реальном приложении здесь был бы вызов API PayPalych
    # В заглушке мы можем "ручками" изменить статус платежа для тестирования
    # или использовать какую-то логику (например, случайное завершение)
    # Ниже пример с ручной установкой статуса через переменную окружения

    # Проверим, установлен ли статус вручную для тестирования
    # Это нестандартный способ, но позволяет управлять статусом извне
    # Лучше использовать внешний файл или базу данных для этого в реальном приложении
    # Для простоты в заглушке просто возвращаем сохраненный статус
    # Или можно добавить логику: если прошло N времени - считаем оплаченным

    current_status = payment_info['status']
    print(f"[DEBUG] Проверка статуса платежа {payment_id}: {current_status}")

    return current_status

# Функция для ручной установки статуса платежа (для тестирования)
def set_mock_payment_status(payment_id: str, status: str):
    """
    Устанавливает статус платежа вручную (только для тестирования с заглушкой)
    """
    if payment_id in _mock_payments:
        _mock_payments[payment_id]['status'] = status
        print(f"[DEBUG] Статус платежа {payment_id} изменен на '{status}'")
    else:
        print(f"[DEBUG] Платеж {payment_id} не найден для изменения статуса")

# Функция для периодической проверки статуса платежа
async def poll_payment_status(payment_id: str, max_attempts: int = 10):
    """
    Периодически проверяет статус платежа до его завершения
    """
    for attempt in range(max_attempts):
        status = await check_payment_status(payment_id)
        if status in ['completed', 'failed', 'cancelled']:
            return status
        await asyncio.sleep(10)  # Ждем 10 секунд между проверками
    return 'timeout'
