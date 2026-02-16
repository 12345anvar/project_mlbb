from aiogram import Router, F, types
from databaze.main import get_user_data

router = Router()

@router.message(F.text == "👤 Mening profilim")
async def show_profile(message: types.Message):
    print("DEBUG: Profil tugmasi bosildi!")
    user = await get_user_data(message.from_user.id)

    if user:
        date_str = user['joined_at'].strftime("%d.%m.%Y") if user.get('joined_at') else "Noma'lum"
        await message.answer(f"👤 Profilingiz:\nID: {user['user_id']}\nBalans: {user['balance']} so'm\nSana: {date_str}")
    else:
        await message.answer("Siz bazada topilmadingiz.")
