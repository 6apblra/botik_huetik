# handlers.py - дополнительные обработчики команд для бота
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.database import get_user, create_user, update_subscription
from bot.paypalych_api import create_payment_link, check_payment_status
from vpn.vpn_manager import generate_v2ray_config, create_v2ray_user
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

router = Router()

class BuyStates(StatesGroup):
    waiting_for_payment = State()

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "Список доступных команд:\n"
        "/start - начать работу с ботом\n"
        "/buy - купить VPN-подписку\n"
        "/status - проверить статус вашей подписки\n"
        "/renew - продлить подписку\n"
        "/help - показать это сообщение"
    )
    await message.answer(help_text)

@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
    if message.from_user.id == ADMIN_ID:
        # Добавляем админские команды
        admin_text = "Вы вошли в режим администратора. Доступны команды управления."
        await message.answer(admin_text)
    else:
        await message.answer("У вас нет прав администратора.")
