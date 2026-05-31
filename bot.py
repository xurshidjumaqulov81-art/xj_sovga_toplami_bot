from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

import asyncio
import asyncpg

from config import BOT_TOKEN, ADMIN_ID, DATABASE_URL
from database import create_tables

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Register(StatesGroup):
    full_name = State()
    xj_id = State()
    qualification = State()
    phone = State()
    address = State()


qual_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ОДДИЙ ҲАМКОР")],
        [KeyboardButton(text="ХЖ МАСТЕР")],
        [KeyboardButton(text="ХЖ МЕНЕЖЕР")],
        [KeyboardButton(text="ХЖ БРОНЗА")],
        [KeyboardButton(text="ХЖ СИЛЬВЕР")]
    ],
    resize_keyboard=True
)
