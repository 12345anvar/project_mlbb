import os
from aiogram import Bot, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

# Config ma'lumotlari
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CARD_NUMBER = os.getenv("CARD_NUMBER")
CARD_OWNER = os.getenv("CARD_OWNER")

router = Router()


# State (Holat) larni e'lon qilamiz
class DepositMoney(StatesGroup):
    amount = State()
    waiting_photo = State()


# Admin uchun tasdiqlash tugmalari
def admin_kb(user_id: int, amount: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash", callback_data=f"adm_confirm:{user_id}:{amount}")
    builder.button(text="❌ Rad etish", callback_data=f"adm_reject:{user_id}")
    builder.adjust(2)
    return builder.as_markup()


# 1. Hamyon bosh menyusi (Sizning keyboardingizdagi tugmaga moslangan)
@router.message(F.text == "💰 Hamyon")
async def wallet_main_menu(message: types.Message):
    print("DEBUG: Hamyon tugmasi bosildi")
    user = await get_user_data(message.from_user.id)
    balance = user['balance'] if user else 0

    builder = ReplyKeyboardBuilder()
    builder.button(text="➕ Hamyonni to'ldirish")  # Sizning keyboardingizdagi nom
    builder.button(text="⬅️ Ortga")  # Sizning keyboardingizda 'Ortga' ekan
    builder.adjust(1)

    await message.answer(
        f"💳 <b>Sizning hamyoningiz</b>\n\n"
        f"💰 Balans: {balance:,} so'm\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
        "Hisobni to'ldirish uchun pastdagi tugmani bosing:",
        reply_markup=builder.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )


# 2. To'ldirishni boshlash
# handlers/wallet.py

@router.message(F.text == "➕ Hamyonni to'ldirish")  # Keyboarddagi matn bilan 100% bir xil
async def start_deposit(message: types.Message, state: FSMContext):
    print("DEBUG: To'ldirish tugmasi bosildi!")  # Terminalda buni ko'rishingiz kerak

    await message.answer(
        "💰 To'ldirmoqchi bo'lgan summani kiriting (masalan: 20000):",
        reply_markup=types.ReplyKeyboardRemove()  # Summa kiritishda xalaqit bermasligi uchun menyuni yopamiz
    )
    await state.set_state(DepositMoney.amount)

# 3. Summani qabul qilish
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
        "To'lovni amalga oshiring va <b>chek rasmini</b> yuboring.",
        parse_mode="HTML"
    )
    await state.set_state(DepositMoney.waiting_photo)
    return None


# 4. Chek rasmini qabul qilish va adminga yuborish
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


# 5. Rasm o'rniga boshqa narsa yuborsa
@router.message(DepositMoney.waiting_photo)
async def waiting_photo_wrong(message: types.Message):
    await message.answer("⚠️ Iltimos, to'lov chekini rasm ko'rinishida yuboring.")


# 6. Admin tasdiqlashi (Callback)
@router.callback_query(F.data.startswith("adm_confirm:"))
async def admin_confirm(callback: types.CallbackQuery, bot: Bot):
    _, user_id, amount = callback.data.split(":")

    # Bazada balansni oshiramiz
    await update_user_balance(int(user_id), int(amount))

    await bot.send_message(user_id, f"✅ To'lovingiz tasdiqlandi! +{int(amount):,} so'm")
    await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n✅ TASDIQLANDI")
    await callback.answer("Tasdiqlandi!")


from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from databaze.main import get_user_data, update_user_balance
from keyboards.main_menu import main_menu_keyboard  # Asosiy menyu keyboardi

router = Router()


# --- FOYDALANUVCHI QISMI ---

# "Ortga" tugmasi ishlamayotgan edi, mana yechimi:
@router.message(F.text == "⬅️ Ortga")
async def back_to_main_handler(message: types.Message, state: FSMContext):
    print("DEBUG: Ortga bosildi")
    await state.clear()  # Har qanday holatni bekor qilamiz
    await message.answer(
        "Asosiy menyuga qaytdingiz.",
        reply_markup=main_menu_keyboard  # Shunda asosiy keyboard chiqadi
    )


# --- ADMIN PANEL QISMI (CALLBACKS) ---

# Tasdiqlash (Confirm)
@router.callback_query(F.data.startswith("adm_confirm:"))
async def admin_confirm(callback: types.CallbackQuery, bot: Bot):
    _, user_id, amount = callback.data.split(":")

    # Balansni yangilash
    await update_user_balance(int(user_id), int(amount))

    # Foydalanuvchiga xabar
    await bot.send_message(user_id, f"✅ To'lovingiz tasdiqlandi! +{int(amount):,} so'm")

    # Admin xabarini yangilash (Tugmalarni olib tashlash)
    await callback.message.edit_caption(
        caption=f"{callback.message.caption}\n\n✅ TASDIQLANDI",
        reply_markup=None
    )
    await callback.answer("Muvaffaqiyatli tasdiqlandi!")


# Rad etish (Reject) - Sizda ishlamayotgan qism:
@router.callback_query(F.data.startswith("adm_reject:"))
async def admin_reject(callback: types.CallbackQuery, bot: Bot):
    _, user_id = callback.data.split(":")

    # Foydalanuvchiga xabar
    await bot.send_message(user_id,
                           "❌ Kechirasiz, siz yuborgan to'lov cheki rad etildi. Ma'lumotlarni tekshirib qayta yuboring.")

    # Admin xabarini yangilash
    await callback.message.edit_caption(
        caption=f"{callback.message.caption}\n\n❌ RAD ETILDI",
        reply_markup=None
    )
    await callback.answer("To'lov rad etildi.")


