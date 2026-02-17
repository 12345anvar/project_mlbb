import os
from dotenv import load_dotenv
from aiogram import Bot, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from aiogram.filters import Command

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID"))
CARD_NUMBER = os.getenv("CARD_NUMBER")
CARD_OWNER = os.getenv("CARD_OWNER")

router = Router()


class DepositMoney(StatesGroup):
    amount = State()
    waiting_photo = State()


def admin_kb(user_id: int, amount: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"adm_confirm:{user_id}:{amount}")
    builder.button(text="❌ Rad etish", callback_data=f"adm_reject:{user_id}")
    builder.adjust(2)
    return builder.as_markup()


@router.message(Command("deposit"))
async def start_deposit(message: types.Message, state: FSMContext):
    await message.answer("💰 To'ldirmoqchi bo'lgan summani kiriting (masalan: 25000):")
    await state.set_state(DepositMoney.amount)


@router.message(DepositMoney.amount)
async def process_amount(message: types.Message, state: FSMContext):
    amount_text = message.text.strip().replace(" ", "").replace(",", "")
    if not amount_text.isdigit():
        return await message.answer("❌ Faqat raqam kiriting!")

    amount = int(amount_text)
    await state.update_data(amount=amount)

    await message.answer(
        f"💳 <b>To'lov ma'lumotlari:</b>\n\n"
        f"Karta: <code>{CARD_NUMBER}</code>\n"
        f"Ega: {CARD_OWNER}\n"
        f"Summa: {amount:,} so'm\n\n"
        "To'lovni amalga oshiring va <b>chek rasmini</b> (skrinshot) shu yerga yuboring.",
        parse_mode="HTML"
    )
    await state.set_state(DepositMoney.waiting_photo)
    return None


@router.message(DepositMoney.waiting_photo, F.photo)
async def handle_receipt(message: types.Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    amount = user_data.get("amount")

    caption = (f"🔔 Yangi to'lov!\n\n"
               f"👤 Foydalanuvchi: @{message.from_user.username} (ID: {message.from_user.id})\n"
               f"💰 Summa: {amount:,} so'm")

    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=caption,
        reply_markup=admin_kb(message.from_user.id, amount)
    )

    await message.answer("✅ Rahmat! Chek adminga yuborildi. Tasdiqlashni kuting.")
    await state.clear()


@router.message(DepositMoney.waiting_photo)
async def waiting_photo_wrong(message: types.Message):
    await message.answer("⚠️ Iltimos, to'lov chekini rasm ko'rinishida yuboring.")