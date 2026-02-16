from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Mening profilim"), KeyboardButton(text="💰 Hamyon")],
        [KeyboardButton(text="🛍 Xaridlar tarixi")]
    ],
    resize_keyboard=True
)

def wallet_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Hamyonni to'ldirish")],
            [KeyboardButton(text="⬅️ Ortga")]
        ],
        resize_keyboard=True
    )
    return keyboard

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def check_payment_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ To'ladim")],
            [KeyboardButton(text="⬅️ Ortga")]
        ],
        resize_keyboard=True
    )