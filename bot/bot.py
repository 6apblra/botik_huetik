import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.database import get_user, create_user, update_subscription, get_active_users
from bot.paypalych_api import create_payment_link, check_payment_status
from vpn.vpn_manager import generate_v2ray_config, create_v2ray_user, remove_v2ray_user
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PAYPALYCH_API_KEY = os.getenv("PAYPALYCH_API_KEY")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FSM состояния
class BuyStates(StatesGroup):
    waiting_for_payment = State()

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "Привет! Это VPN-сервис.\n\n"
        "Доступные команды:\n"
        "/buy - купить подписку\n"
        "/status - проверить статус подписки\n"
        "/renew - продлить подписку"
    )
    await message.answer(welcome_text)

@dp.message(Command("buy"))
async def cmd_buy(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    existing_user = get_user(user_id)
    
    if existing_user and existing_user['end_date'] and datetime.now() < datetime.fromisoformat(existing_user['end_date']):
        await message.answer("У вас уже есть активная подписка!")
        return

    # Создаем платеж через PayPalych
    amount = 5.00  # Пример цены
    currency = "USD"
    description = "VPN-подписка на 30 дней"
    
    payment_data = await create_payment_link(
        amount=amount,
        currency=currency,
        description=description,
        user_id=user_id
    )
    
    if payment_data and 'payment_url' in payment_data:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url=payment_data['payment_url'])]
        ])
        await message.answer(
            f"Для покупки подписки нажмите кнопку ниже. Стоимость: {amount} USD",
            reply_markup=keyboard
        )
        
        # Сохраняем информацию о платеже в FSM
        await state.update_data(
            payment_id=payment_data['payment_id'],
            amount=amount
        )
        await state.set_state(BuyStates.waiting_for_payment)
    else:
        await message.answer("Ошибка при создании платежа. Попробуйте позже.")

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if not user:
        await message.answer("Вы не зарегистрированы в системе. Купите подписку сначала.")
        return

    if user['end_date']:
        end_date = datetime.fromisoformat(user['end_date'])
        if datetime.now() < end_date:
            remaining = end_date - datetime.now()
            days = remaining.days
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            await message.answer(f"Ваша подписка активна. Осталось: {days} дней {hours} часов {minutes} минут")
        else:
            await message.answer("Ваша подписка истекла.")
    else:
        await message.answer("У вас нет активной подписки.")

@dp.message(Command("renew"))
async def cmd_renew(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if not user:
        await message.answer("Вы не зарегистрированы в системе. Купите подписку сначала.")
        return

    # Создаем платеж через PayPalych
    amount = 5.00  # Пример цены
    currency = "USD"
    description = "Продление VPN-подписки на 30 дней"
    
    payment_data = await create_payment_link(
        amount=amount,
        currency=currency,
        description=description,
        user_id=user_id
    )
    
    if payment_data and 'payment_url' in payment_data:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url=payment_data['payment_url'])]
        ])
        await message.answer(
            f"Для продления подписки нажмите кнопку ниже. Стоимость: {amount} USD",
            reply_markup=keyboard
        )
        
        # Сохраняем информацию о платеже в FSM
        await state.update_data(
            payment_id=payment_data['payment_id'],
            amount=amount
        )
        await state.set_state(BuyStates.waiting_for_payment)
    else:
        await message.answer("Ошибка при создании платежа. Попробуйте позже.")

@dp.message(BuyStates.waiting_for_payment)
async def handle_payment_check(message: types.Message, state: FSMContext):
    data = await state.get_data()
    payment_id = data.get('payment_id')
    
    if not payment_id:
        await message.answer("Ошибка: нет информации о платеже.")
        return
    
    status = await check_payment_status(payment_id)
    
    if status == 'completed':
        user_id = message.from_user.id
        # Обновляем или создаем пользователя
        user = get_user(user_id)
        if user:
            # Продлеваем подписку
            if user['end_date']:
                current_end = datetime.fromisoformat(user['end_date'])
                new_end = current_end + timedelta(days=30)
            else:
                new_end = datetime.now() + timedelta(days=30)
            update_subscription(user_id, new_end.isoformat())
        else:
            # Создаем нового пользователя
            create_user(user_id, (datetime.now() + timedelta(days=30)).isoformat())
        
        # Создаем пользователя в v2ray
        await create_v2ray_user(user_id)
        
        # Отправляем конфигурацию
        config = generate_v2ray_config(user_id)
        await message.answer_document(
            types.FSInputFile(config['file_path']),
            caption="Ваша конфигурация VPN. Сохраните файл и импортируйте в клиент v2ray."
        )
        
        await message.answer("Подписка успешно оформлена!")
        await state.clear()
    elif status == 'pending':
        await message.answer("Платеж еще не завершен. Пожалуйста, завершите оплату и повторите попытку.")
    else:
        await message.answer("Платеж не найден или не был завершен. Попробуйте снова.")

async def check_subscriptions():
    """Фоновая задача для проверки истекших подписок"""
    users = get_active_users()
    for user in users:
        if user['end_date']:
            end_date = datetime.fromisoformat(user['end_date'])
            if datetime.now() >= end_date:
                # Удаляем пользователя из v2ray
                await remove_v2ray_user(user['user_id'])
                
                # Обновляем статус в БД
                update_subscription(user['user_id'], None)
                
                # Уведомляем пользователя
                try:
                    await bot.send_message(
                        user['user_id'],
                        "Ваша подписка VPN истекла. Для продолжения использования, пожалуйста, продлите подписку командой /buy"
                    )
                except Exception as e:
                    logger.error(f"Не удалось уведомить пользователя {user['user_id']}: {e}")

async def main():
    from vpn.vpn_manager import initialize_v2ray_server
    await initialize_v2ray_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
