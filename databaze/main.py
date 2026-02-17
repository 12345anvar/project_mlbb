import asyncpg
# Faqat kerakli o'zgaruvchilarni configdan olamiz
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 1. db_start funksiyasi (bot.py uchun)
async def db_start():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Users jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                balance BIGINT DEFAULT 0
            )
        """)
        # Orders jadvali
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                amount BIGINT DEFAULT 0,
                item_details TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                balance BIGINT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Bu yerga qo'shildi
            )
        """)
        print("✅ Ma'lumotlar bazasi va jadvallar to'liq tayyor.")
    finally:
        await conn.close()
# 2. create_profile funksiyasi (start.py uchun)
# databaze/main.py ichida

async def create_profile(user_id, username, full_name): # full_name qo'shildi
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # ON CONFLICT qismida profil bor bo'lsa, ismini yangilab qo'yishni ham qo'shdik
        await conn.execute("""
            INSERT INTO users (user_id, username, full_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE 
            SET username = EXCLUDED.username, 
                full_name = EXCLUDED.full_name
        """, user_id, username, full_name)
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

# 5. get_any_user_history (agar kerak bo'lsa)
async def get_any_user_history(target_user_id):
    return await get_user_orders(target_user_id)

# Foydalanuvchi ma'lumotlarini (balans, ID va h.k.) olish uchun
async def get_user_data(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        return await conn.fetchrow("""
            SELECT user_id, username, full_name, balance, created_at 
            FROM users 
            WHERE user_id = $1
        """, user_id)
    finally:
        await conn.close()


# databaze/main.py ichida

async def update_user_balance(user_id: int, amount: int):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # 1. Foydalanuvchi balansini yangilash
        await conn.execute(
            "UPDATE users SET balance = balance + $1 WHERE user_id = $2",
            amount, user_id
        )

        # 2. Orders jadvaliga muvaffaqiyatli to'lovni yozish
        # DIQQAT: 'to''ldirish' deb ikkita tirnoq ishlating yoki so'zni o'zgartiring
        await conn.execute("""
            INSERT INTO orders (user_id, amount, item_details, status)
            VALUES ($1, $2, 'Balans toldirish', 'completed')
        """, user_id, amount)

        print(f"✅ Balans yangilandi: User {user_id}, +{amount}")
    finally:
        await conn.close()