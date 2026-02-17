from aiogram import Router, F, types
from databaze.main import get_user_orders

router = Router()


@router.message(F.text == "🛍 Xaridlar tarixi")  # Yoki sizda qanday nomlangan bo'lsa
async def show_history(message: types.Message):
    orders = await get_user_orders(message.from_user.id)

    if not orders:
        return await message.answer("📭 Sizda hali xaridlar mavjud emas.")

    res = "📜 <b>Sizning xaridlaringiz:</b>\n\n"
    for i, order in enumerate(orders, 1):
        # Ustun nomlari aynan bazadagi kabi bo'lishi shart:
        res += (f"{i}. 📦 <b>{order['item_details']}</b>\n"
                f"   💰 Narxi: {order['amount']:,} so'm\n"
                f"   📅 Sana: {order['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n")

    await message.answer(res, parse_mode="HTML")
    return None