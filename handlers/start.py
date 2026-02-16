from aiogram import Router, types
from aiogram.filters import CommandStart
from databaze.main import create_profile
from keyboards.main_menu import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await create_profile(
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )

    await message.answer(
        f"Xush kelibsiz!",
        reply_markup=main_menu_keyboard
    )