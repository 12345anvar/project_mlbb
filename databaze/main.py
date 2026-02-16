import asyncio

import asyncpg
from config import DB_NAME, DB_USER, DB_HOST, DB_PASS, DB_PORT

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


async def db_start():
    """Jadvallarni yaratish va bazani tayyorlash"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)

        # 1. Foydalanuvchilar jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                balance FLOAT DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Buyurtmalar jadvali (orders)
        # Kelajakda to'lov bo'limida ishlatamiz
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                user_id BIGINT,
                amount FLOAT,
                item_details TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)

        await conn.close()
        print("✅ PostgreSQL: Barcha jadvallar muvaffaqiyatli yaratildi.")
    except Exception as e:
        print(f"❌ Bazani yaratishda xato: {e}")


async def create_profile(user_id, full_name, username):
    """Yangi foydalanuvchini bazaga qo'shish"""
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute("""
            INSERT INTO users (user_id, full_name, username) 
            VALUES ($1, $2, $3) 
            ON CONFLICT (user_id) DO UPDATE 
            SET full_name = $2, username = $3
        """, user_id, full_name, username)
    finally:
        await conn.close()


async def get_user_data(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        return await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
    finally:
        await conn.close()
async def get_user_orders(user_id):
    """Foydalanuvchining barcha xaridlarini ro'yxat ko'rinishida olish"""
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = await conn.fetch("""
            SELECT item_name, price, created_at 
            FROM orders 
            WHERE user_id = $1 
            ORDER BY created_at DESC
        """, user_id)
        return rows
    finally:
        await conn.close()

async def get_any_user_history(target_user_id):
    """Admin uchun: Ixtiyoriy foydalanuvchi tarixini olish"""
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = await conn.fetch("""
            SELECT item_name, price, created_at 
            FROM orders 
            WHERE user_id = $1 
            ORDER BY created_at DESC
        """, target_user_id)
        return rows
    finally:
        await conn.close()

async def check_if_amount_is_busy(amount):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        res = await conn.fetchval("SELECT amount FROM active_payments WHERE amount = $1", amount)
        return res is not None
    finally:
        await conn.close()

async def save_active_payment(user_id, amount):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute("INSERT INTO active_payments (user_id, amount) VALUES ($1, $2)", user_id, amount)
    finally:
        await conn.close()

async def delete_payment_after_delay(amount, delay):
    await asyncio.sleep(delay)
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute("DELETE FROM active_payments WHERE amount = $1", amount)
        print(f"DEBUG: {amount} so'mlik so'rov muddati tugagani uchun o'chirildi.")
    finally:
        await conn.close()