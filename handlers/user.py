from aiogram import Router, F, types
from databaze.main import get_user_orders

router = Router()


@router.message(F.text == "🛍 Xaridlar tarixi")
async def show_history(message: types.Message):
    orders = await get_user_orders(message.from_user.id)

    if not orders:
        await message.answer("Sizda hali xaridlar mavjud emas. 🛒")
        return

    text = "🛍 **Sizning xaridlar tarixingiz:**\n\n"

    for i, order in enumerate(orders, 1):
        date = order['created_at'].strftime("%d.%m.%Y | %H:%M")
        text += (
            f"{i}. **{order['item_name']}**\n"
            f"   💰 Narxi: {order['price']} so'm\n"
            f"   📅 Vaqti: {date}\n"
            f"   -------------------\n"
        )

    await message.answer(text, parse_mode="Markdown")