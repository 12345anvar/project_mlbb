import asyncio
from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import CARD_NUMBER, CARD_OWNER
from databaze.main import (
    get_user_data,
    check_if_amount_is_busy,
    save_active_payment,
    delete_payment_after_delay
)
from keyboards.main_menu import wallet_menu, main_menu_keyboard, check_payment_kb


class DepositMoney(StatesGroup):
    amount = State()
    waiting_pay = State()


router = Router()


@router.message(F.text == "💰 Hamyon")
async def show_wallet(message: types.Message):
    user = await get_user_data(message.from_user.id)
    balance = user['balance'] if user else 0
    await message.answer(
        f"💰 Sizning hisobingiz: {balance} so'm\n\n"
        "Pastdagi tugmalar orqali hamyoningizni boshqarishingiz mumkin:",
        reply_markup=wallet_menu()
    )


@router.message(F.text == "➕ Hamyonni to'ldirish")
async def start_deposit(message: types.Message, state: FSMContext):
    await message.answer(
        "💵 Qancha to'ldirmoqchisiz?\n\n"
        "Iltimos, summani nuqta bilan kiriting.\n"
        "Masalan: `20.000` yoki `50.000`",
        parse_mode="Markdown"
    )
    await state.set_state(DepositMoney.amount)


@router.message(DepositMoney.amount)
async def process_amount(message: types.Message, state: FSMContext):
    amount_text = message.text.strip()
    amount_digits = amount_text.replace(".", "")

    if not amount_digits.isdigit():
        await message.answer("❌ Xato! Summani faqat raqamlarda va namunadagidek kiriting: `20.000`",
                             parse_mode="Markdown")
        return

    amount = int(amount_digits)

    is_busy = await check_if_amount_is_busy(amount)

    if is_busy:
        await message.answer(
            f"⚠️ Kechirasiz, `{amount_text}` so'm miqdordagi to'lov hozirda band.\n\n"
            f"Iltimos, boshqa biror summa kiriting (Chalkashlik bo'lmasligi uchun).\n"
            f"Masalan: `{amount + 100:,}` so'm kiriting.",
            parse_mode="Markdown"
        )
        return

    await save_active_payment(message.from_user.id, amount)
    await state.update_data(deposit_amount=amount)
    await state.set_state(DepositMoney.waiting_pay)

    await message.answer(
        f"✅ To'lov buyurtmasi yaratildi!\n\n"
        f"💰 To'lanadigan summa: **{amount_text} so'm**\n"
        f"💳 Karta raqami: `{CARD_NUMBER}`\n"
        f"👤 Karta egasi: **{CARD_OWNER}**\n\n"
        f"⚠️ **MUHIM:** To'lovni amalga oshirish uchun 20 daqiqa vaqtingiz bor. "
        f"Aynan kiritilgan summani o'zgarishsiz o'tkazing! "
        f"Aks holda to'lov tizim tomonidan aniqlanmasligi mumkin.",
        reply_markup=check_payment_kb(),
        parse_mode="Markdown"
    )

    asyncio.create_task(delete_payment_after_delay(amount, 1200))


@router.message(DepositMoney.waiting_pay, F.text == "✅ To'ladim")
async def confirm_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("deposit_amount")

    await message.answer(
        f"⏳ To'lovingiz tekshirilmoqda...\n\n"
        f"Siz kiritgan {amount:,} so'm tushganligi haqida SMS kelishi bilan balansingiz to'ldiriladi.",
        reply_markup=main_menu_keyboard()
    )
    await state.clear()


@router.message(F.text == "⬅️ Ortga")
async def back_button(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=main_menu_keyboard())