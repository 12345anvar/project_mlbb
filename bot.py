import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from databaze.main import db_start
from handlers import routers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    stream=sys.stdout
)


async def main():
    print("---" * 10)
    print("🚀 Bot ishga tushmoqda...")
    try:
        await db_start()
        print("✅ Ma'lumotlar bazasi bilan aloqa o'rnatildi.")
    except Exception as e:
        logging.error(f"❌ Bazada xatolik: {e}")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    try:
        dp.include_routers(*routers)
        print(f"✅ {len(routers)} ta router muvaffaqiyatli ulandi.")
    except RuntimeError as e:
        logging.error(f"❌ Router ulanishida xato: {e}")
        print("Maslahat: __init__.py ichida bir xil routerni ikki marta yozmaganingizni tekshiring!")
        return

    print("🤖 Bot xabarlarni qabul qilishga tayyor!")
    print("---" * 10)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Bot to'xtatildi!")