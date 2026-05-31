import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN, ADMIN_ID
from states import Registration
from keyboards import qualification_kb, confirm_kb
from database import (
    check_user,
    check_xj_id,
    get_count,
    get_limit,
    set_limit,
    add_limit,
    add_user
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def left_gifts():
    return get_limit() - get_count()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    if check_user(tg_id):
        await message.answer(
            "⚠️ Сиз ушбу акцияда олдин иштирок этгансиз.\n\n"
            "1 та Telegram аккаунт фақат 1 марта бепул совға тўпламини олиши мумкин."
        )
        return

    if left_gifts() <= 0:
        await message.answer(
            "⛔ Афсуски, ҳозирча бепул совға тўпламлари тугади.\n\n"
            "Янги лимит ажратилса, бот орқали рўйхатдан ўтиш қайта давом этади."
        )
        return

    await state.clear()

    await message.answer(
        "👋 Ассалому алайкум!\n\n"
        "🎁 XJ совға тўплами ботига хуш келибсиз.\n\n"
        "XJ компанияси томонидан ҳамкорларнинг бизнесини тизимли "
        "ривожлантириш ва режали ишлашини қўллаб-қувватлаш мақсадида "
        "махсус совға тўплами тақдим этилмоқда.\n\n"
        f"📊 Ҳозирда қолган совғалар сони: {left_gifts()} та\n\n"
        "Илтимос, рўйхатдан ўтиш учун исм ва фамилиянгизни ёзинг.\n\n"
        "📝 Намуна: Алиев Али"
    )

    await state.set_state(Registration.full_name)


@dp.message(Registration.full_name)
async def get_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    if len(full_name.split()) < 2:
        await message.answer(
            "⚠️ Илтимос, исм ва фамилиянгизни тўлиқ ёзинг.\n\n"
            "📝 Намуна: Алиев Али"
        )
        return

    await state.update_data(full_name=full_name)

    await message.answer(
        "🆔 XJ ID рақамингизни киритинг.\n\n"
        "ID рақам 7 хонали бўлиши керак.\n\n"
        "📝 Намуна: 0012345"
    )

    await state.set_state(Registration.xj_id)


@dp.message(Registration.xj_id)
async def get_xj_id(message: Message, state: FSMContext):
    xj_id = message.text.strip()

    if not xj_id.isdigit() or len(xj_id) != 7:
        await message.answer(
            "⚠️ ID рақам нотўғри киритилди.\n\n"
            "Илтимос, 7 хонали ID рақам ёзинг.\n\n"
            "📝 Намуна: 0012345"
        )
        return

    if check_xj_id(xj_id):
        await message.answer(
            "⚠️ Бу XJ ID рақам орқали совға тўплами олдин расмийлаштирилган.\n\n"
            "1 та XJ ID фақат 1 марта иштирок этиши мумкин."
        )
        await state.clear()
        return

    await state.update_data(xj_id=xj_id)

    await message.answer(
        "⭐ Квалификациянгизни танланг:",
        reply_markup=qualification_kb
    )

    await state.set_state(Registration.qualification)


@dp.message(Registration.qualification)
async def get_qualification(message: Message, state: FSMContext):
    qualifications = [
        "ОДДИЙ ҲАМКОР",
        "XJ MASTER",
        "XJ MANAGER",
        "XJ BRONZE",
        "XJ SILVER"
    ]

    if message.text not in qualifications:
        await message.answer(
            "⚠️ Илтимос, қуйидаги тугмалардан бирини танланг.",
            reply_markup=qualification_kb
        )
        return

    await state.update_data(qualification=message.text)

    await message.answer(
        "🎁 Табриклаймиз!\n\n"
        "XJ компанияси билан тизимли ва режали ишлаб, юқори натижаларга "
        "эришишингиз учун ушбу махсус тўплам сизга БЕПУЛ юборилади.\n\n"
        "📦 Тўплам таркиби:\n"
        "🔹 XJ блокнот\n"
        "🔹 XJ ҳафталик кундалик\n"
        "🔹 XJ ручка\n"
        "🔹 XJ маркетинг ва маҳсулотлар каталоги\n\n"
        "Давом этиш учун қуйидаги тугмани босинг.",
        reply_markup=confirm_kb
    )

    await state.set_state(Registration.phone)


@dp.message(Registration.phone, F.text == "ТУШУНАРЛИ ✅")
async def ask_phone(message: Message, state: FSMContext):
    await message.answer(
        "📞 Жўнатмани расмийлаштириш учун телефон рақамингизни киритинг.\n\n"
        "📝 Намуна: +998901234567",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(Registration.phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.text.strip()

    if len(phone) < 9:
        await message.answer(
            "⚠️ Телефон рақам нотўғри киритилди.\n\n"
            "📝 Намуна: +998901234567"
        )
        return

    await state.update_data(phone=phone)

    await message.answer(
        "📍 Жўнатма етказилиши учун тўлиқ манзилингизни ёзинг.\n\n"
        "📝 Намуна: Тошкент шаҳри, Чилонзор тумани, 10-мавзе, 25-уй"
    )

    await state.set_state(Registration.address)


@dp.message(Registration.address)
async def get_address(message: Message, state: FSMContext):
    address = message.text.strip()

    if len(address) < 10:
        await message.answer(
            "⚠️ Манзил жуда қисқа киритилди.\n\n"
            "Илтимос, тўлиқ манзилингизни ёзинг."
        )
        return

    tg_id = message.from_user.id

    if check_user(tg_id):
        await message.answer(
            "⚠️ Сиз ушбу акцияда олдин иштирок этгансиз.\n\n"
            "1 та Telegram аккаунт фақат 1 марта иштирок этиши мумкин."
        )
        await state.clear()
        return

    if left_gifts() <= 0:
        await message.answer(
            "⛔ Афсуски, ҳозирча бепул совға тўпламлари тугади."
        )
        await state.clear()
        return

    data = await state.get_data()
    gift_number = get_count() + 1

    add_user(
        tg_id=tg_id,
        full_name=data["full_name"],
        xj_id=data["xj_id"],
        qualification=data["qualification"],
        phone=data["phone"],
        address=address,
        gift_number=gift_number
    )

    username = message.from_user.username
    telegram_name = message.from_user.full_name

    admin_text = (
        "🎁 Янги XJ совға аризаси\n\n"
        f"📌 Совға рақами: {gift_number}\n\n"
        f"👤 Исм фамилия: {data['full_name']}\n"
        f"🆔 XJ ID: {data['xj_id']}\n"
        f"⭐ Квалификация: {data['qualification']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"📍 Манзил: {address}\n\n"
        "Telegram маълумотлари:\n"
        f"🆔 Telegram ID: {tg_id}\n"
        f"👤 Username: @{username if username else 'username йўқ'}\n"
        f"📛 Telegram исми: {telegram_name}\n\n"
        f"📊 Қолган совғалар: {left_gifts()} та"
    )

    await bot.send_message(ADMIN_ID, admin_text)

    await message.answer(
        "✅ Аризангиз муваффақиятли қабул қилинди!\n\n"
        f"🎁 Сизнинг совға рақамингиз: {gift_number}\n\n"
        "XJ жамоаси сизга бизнесингизда ўсиш, тизимли ишлаш "
        "ва юқори натижалар тилайди.\n\n"
        "Тез орада масъул ходимлар сиз билан боғланади."
    )

    await state.clear()


@dp.message(Command("setlimit"))
async def admin_set_limit(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        limit = int(message.text.split()[1])
    except:
        await message.answer("⚠️ Намуна: /setlimit 50")
        return

    set_limit(limit)

    await message.answer(
        f"✅ Совға лимити {limit} та қилиб белгиланди.\n\n"
        f"📊 Олинган: {get_count()} та\n"
        f"🎁 Қолган: {left_gifts()} та"
    )


@dp.message(Command("addgifts"))
async def admin_add_gifts(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        count = int(message.text.split()[1])
    except:
        await message.answer("⚠️ Намуна: /addgifts 20")
        return

    add_limit(count)

    await message.answer(
        f"✅ {count} та совға қўшилди.\n\n"
        f"📦 Жами лимит: {get_limit()} та\n"
        f"📊 Олинган: {get_count()} та\n"
        f"🎁 Қолган: {left_gifts()} та"
    )


@dp.message(Command("stats"))
async def admin_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "📊 XJ совға тўплами статистикаси\n\n"
        f"📦 Жами лимит: {get_limit()} та\n"
        f"✅ Олинган: {get_count()} та\n"
        f"🎁 Қолган: {left_gifts()} та"
    )


async def main():
    print("Бот ишга тушди...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
