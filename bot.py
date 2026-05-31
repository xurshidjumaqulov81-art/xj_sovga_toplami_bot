import asyncio
import re

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID
from database import (
    create_tables,
    get_stats,
    add_gifts,
    set_gifts,
    check_user_exists,
    check_xj_id_exists,
    save_user
)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Register(StatesGroup):
    full_name = State()
    xj_id = State()
    qualification = State()
    phone = State()
    address = State()


start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="▶️ СТАРТ")]
    ],
    resize_keyboard=True
)


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


understand_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ ТУШУНАРЛИ")]
    ],
    resize_keyboard=True
)


admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="➕ Совға қўшиш")]
    ],
    resize_keyboard=True
)


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    total, distributed, left = await get_stats()

    text = f"""
Ассалому алайкум!

ХЖ компанияси ҳамкорлари учун махсус БЕПУЛ СОВҒА ТЎПЛАМИ дастурига хуш келибсиз.

Бизнесингизни ривожлантириш ва тизимли ишлашни йўлга қўйишингиз учун ХЖ томонидан дастлабки ҳамкорларга қуйидаги совғалар тақдим этилади:

📘 ХЖ блокнот
📗 ХЖ ҳафталик кундалик
🖊 ХЖ ручка
📖 ХЖ маркетинг ва маҳсулотлар каталоги
📚 Ишлаш учун қўлланмалар

🎁 Қолган бепул совға тўпламлари: {left} та

Рўйхатдан ўтиш учун қуйидаги тугмани босинг.
"""

    await message.answer(text, reply_markup=start_keyboard)


@dp.message(F.text == "▶️ СТАРТ")
async def start_register(message: Message, state: FSMContext):
    exists = await check_user_exists(message.from_user.id)

    if exists:
        await message.answer(
            "❌ Сиз ушбу бепул совға тўпламини аввал олгансиз.\n\n"
            "Бир Telegram аккаунт орқали фақат бир марта иштирок этиш мумкин.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    total, distributed, left = await get_stats()

    if left <= 0:
        await message.answer(
            "❌ Ҳозирча бепул совға тўпламлари қолмади.\n\n"
            "Янги ўринлар очилганда қайта уриниб кўринг.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    await message.answer(
        "Илтимос, исм ва фамилиянгизни киритинг.\n\n"
        "Намуна: Абдуллаев Жасур",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Register.full_name)


@dp.message(Register.full_name)
async def get_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    if len(full_name.split()) < 2:
        await message.answer(
            "Илтимос, исм ва фамилиянгизни тўлиқ киритинг.\n\n"
            "Намуна: Абдуллаев Жасур"
        )
        return

    await state.update_data(full_name=full_name)

    await message.answer(
        "ХЖ ID рақамингизни киритинг.\n\n"
        "Намуна: 0012345\n\n"
        "ID рақам 7 хонали бўлиши керак."
    )
    await state.set_state(Register.xj_id)


@dp.message(Register.xj_id)
async def get_xj_id(message: Message, state: FSMContext):
    xj_id = message.text.strip()

    if not re.fullmatch(r"\d{7}", xj_id):
        await message.answer(
            "❌ ID рақам нотўғри киритилди.\n\n"
            "ID 7 хонали рақам бўлиши керак.\n"
            "Намуна: 0012345"
        )
        return

    exists = await check_xj_id_exists(xj_id)

    if exists:
        await message.answer(
            "❌ Ушбу ID рақам бўйича совға тўплами аллақачон расмийлаштирилган.\n\n"
            "Бир ID рақам фақат бир марта иштирок этиши мумкин."
        )
        await state.clear()
        return

    await state.update_data(xj_id=xj_id)

    await message.answer(
        "Квалификациянгизни танланг:",
        reply_markup=qual_keyboard
    )
    await state.set_state(Register.qualification)


@dp.message(Register.qualification)
async def get_qualification(message: Message, state: FSMContext):
    qualification = message.text.strip()

    allowed = [
        "ОДДИЙ ҲАМКОР",
        "ХЖ МАСТЕР",
        "ХЖ МЕНЕЖЕР",
        "ХЖ БРОНЗА",
        "ХЖ СИЛЬВЕР"
    ]

    if qualification not in allowed:
        await message.answer("Илтимос, тугмалардан бирини танланг.", reply_markup=qual_keyboard)
        return

    await state.update_data(qualification=qualification)

    text = """
ХЖ компанияси билан тизимли ва режали ишлаб юқори натижаларга эришишингиз учун ушбу махсус совға тўплами сизга БЕПУЛ тақдим этилади.

Совға тўплами таркиби:

📘 ХЖ блокнот
📗 ХЖ ҳафталик кундалик
🖊 ХЖ ручка
📖 ХЖ маркетинг ва маҳсулотлар каталоги
📚 Ишлаш учун қўлланмалар

Давом этиш учун қуйидаги тугмани босинг.
"""

    await message.answer(text, reply_markup=understand_keyboard)


@dp.message(F.text == "✅ ТУШУНАРЛИ")
async def understood(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state != Register.qualification.state:
        return

    await message.answer(
        "Жўнатма учун телефон рақамингизни киритинг.\n\n"
        "Намуна: +998901234567",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Register.phone)


@dp.message(Register.phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.text.strip()

    if len(phone) < 9:
        await message.answer(
            "Телефон рақам нотўғри киритилди.\n\n"
            "Намуна: +998901234567"
        )
        return

    await state.update_data(phone=phone)

    await message.answer(
        "Совғани етказиб бериш учун тўлиқ манзилингизни киритинг.\n\n"
        "Вилоят, туман ёки шаҳар, маҳалла ва мўлжални ёзинг."
    )
    await state.set_state(Register.address)


@dp.message(Register.address)
async def get_address(message: Message, state: FSMContext):
    address = message.text.strip()

    if len(address) < 5:
        await message.answer("Илтимос, манзилни тўлиқроқ ёзинг.")
        return

    data = await state.get_data()

    telegram_name = message.from_user.full_name
    username = message.from_user.username

    gift_number = await save_user(
        telegram_id=message.from_user.id,
        username=username,
        telegram_name=telegram_name,
        full_name=data["full_name"],
        xj_id=data["xj_id"],
        qualification=data["qualification"],
        phone=data["phone"],
        address=address
    )

    if gift_number is None:
        await message.answer(
            "❌ Ҳозирча бепул совға тўпламлари қолмади.",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        return

    await message.answer(
        f"🎉 Табриклаймиз!\n\n"
        f"Сиз ХЖ компаниясининг бепул совға тўплами учун муваффақиятли рўйхатдан ўтдингиз.\n\n"
        f"📦 Совға рақамингиз: №{gift_number}\n\n"
        f"Сизга ишларингизда улкан зафарлар ва юқори натижалар тилаймиз!",
        reply_markup=ReplyKeyboardRemove()
    )

    username_text = f"@{username}" if username else "Йўқ"

    admin_text = f"""
📥 ЯНГИ РЎЙХАТДАН ЎТГАН ҲАМКОР

🎁 Совға рақами: №{gift_number}

👤 Исм-фамилия: {data["full_name"]}
🆔 ID рақами: {data["xj_id"]}
🏅 Квалификация: {data["qualification"]}
📞 Телефон: {data["phone"]}
📍 Манзил: {address}

🆔 Telegram ID: {message.from_user.id}
📱 Username: {username_text}
👤 Telegram исми: {telegram_name}
"""

    await bot.send_message(ADMIN_ID, admin_text)

    await state.clear()


@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("🔐 Админ меню", reply_markup=admin_keyboard)


@dp.message(F.text == "📊 Статистика")
async def admin_stats_button(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    total, distributed, left = await get_stats()

    await message.answer(
        f"📊 СТАТИСТИКА\n\n"
        f"🎁 Жами совға тўпламлари: {total} та\n"
        f"✅ Тарқатилган: {distributed} та\n"
        f"📦 Қолган: {left} та"
    )


@dp.message(Command("stats"))
async def admin_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    total, distributed, left = await get_stats()

    await message.answer(
        f"📊 СТАТИСТИКА\n\n"
        f"🎁 Жами совға тўпламлари: {total} та\n"
        f"✅ Тарқатилган: {distributed} та\n"
        f"📦 Қолган: {left} та"
    )


@dp.message(Command("add"))
async def admin_add_gifts(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Намуна:\n/add 20")
        return

    count = int(parts[1])
    await add_gifts(count)

    total, distributed, left = await get_stats()

    await message.answer(
        f"✅ {count} та совға тўплами қўшилди.\n\n"
        f"🎁 Жами: {total} та\n"
        f"✅ Тарқатилган: {distributed} та\n"
        f"📦 Қолган: {left} та"
    )


@dp.message(Command("setgifts"))
async def admin_set_gifts(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()

    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Намуна:\n/setgifts 50")
        return

    count = int(parts[1])
    await set_gifts(count)

    total, distributed, left = await get_stats()

    await message.answer(
        f"✅ Совға лимити ўзгартирилди.\n\n"
        f"🎁 Жами: {total} та\n"
        f"✅ Тарқатилган: {distributed} та\n"
        f"📦 Қолган: {left} та"
    )


@dp.message(F.text == "➕ Совға қўшиш")
async def add_gift_info(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "Совға қўшиш учун шундай ёзинг:\n\n"
        "/add 20"
    )


async def main():
    await create_tables()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
