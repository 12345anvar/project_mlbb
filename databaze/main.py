import asyncpg
# Faqat kerakli o'zgaruvchilarni configdan olamiz
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 1. db_start funksiyasi (bot.py uchun)
async def db_start():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                balance BIGINT DEFAULT 0
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                amount BIGINT,
                item_details TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Ma'lumotlar bazasi va jadvallar tayyor.")
    finally:
        await conn.close()

# 2. create_profile funksiyasi (start.py uchun)
async def create_profile(user_id, username):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute("""
            INSERT INTO users (user_id, username)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO NOTHING
        """, user_id, username)
    finally:
        await conn.close()

# 3. get_user_orders funksiyasi (user.py va wallet.py uchun)
async def get_user_orders(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        return await conn.fetch("""
            SELECT amount, item_details, created_at, status
            FROM orders WHERE user_id = $1 ORDER BY created_at DESC
        """, user_id)
    finally:
        await conn.close()

# 4. update_user_balance funksiyasi (wallet.py uchun)
async def update_user_balance(user_id: int, amount: int):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Balansni yangilash
        await conn.execute("UPDATE users SET balance = balance + $1 WHERE user_id = $2", amount, user_id)
        # To'lov tarixiga yozish
        await conn.execute("""
            INSERT INTO orders (user_id, amount, item_details, status)
            VALUES ($1, $2, 'Balans to\'ldirish', 'completed')
        """, user_id, amount)
    finally:
        await conn.close()

# 5. get_any_user_history (agar kerak bo'lsa)
async def get_any_user_history(target_user_id):
    return await get_user_orders(target_user_id)