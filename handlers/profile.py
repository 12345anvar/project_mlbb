from aiogram import Router, F, types
from databaze.main import get_user_data

router = Router()


@router.message(F.text == "👤 Mening profilim")
async def profile_handler(message: types.Message):
    print(f"DEBUG: Profil tugmasi bosildi! User ID: {message.from_user.id}")  # Terminalda tekshirish uchun

    # 1. Bazadan foydalanuvchi ma'lumotlarini olamiz
    user_info = await get_user_data(message.from_user.id)

    # 2. Agar foydalanuvchi bazada mavjud bo'lsa
    if user_info:
        try:
            # created_at ustuni borligini va None emasligini tekshiramiz
            if user_info['created_at']:
                reg_date = user_info['created_at'].strftime("%Y-%m-%d %H:%M")
            else:
                reg_date = "Noma'lum"

            # Matnni shakllantiramiz
            # user_info['ustun_nomi'] bazadagi ustun nomlari bilan bir xil bo'lishi shart
            text = (
                f"👤 <b>Sizning profilingiz:</b>\n\n"
                f"🆔 ID: <code>{user_info['user_id']}</code>\n"
                f"👤 Ism: {user_info['full_name'] or 'Kiritilmagan'}\n"
                f"💰 Balans: {user_info['balance']:,} so'm\n"
                f"📅 Ro'yxatdan o'tilgan: {reg_date}"
            )

            await message.answer(text, parse_mode="HTML")

        except Exception as e:
            print(f"Xato yuz berdi: {e}")
            await message.answer("❌ Profil ma'lumotlarini chiqarishda xatolik yuz berdi.")

    # 3. Agar foydalanuvchi bazada topilmasa
    else:
        await message.answer("❌ Profil topilmadi. Iltimos, /start buyrug'ini bosing.")