import asyncpg
from config import DATABASE_URL


async def connect_db():
    return await asyncpg.connect(DATABASE_URL)


async def create_tables():
    conn = await connect_db()

    await conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE,
        username TEXT,
        telegram_name TEXT,
        full_name TEXT,
        xj_id TEXT UNIQUE,
        qualification TEXT,
        phone TEXT,
        address TEXT,
        gift_number INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    await conn.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id SERIAL PRIMARY KEY,
        total_gifts INTEGER DEFAULT 50,
        distributed_gifts INTEGER DEFAULT 0
    );
    """)

    exists = await conn.fetchrow("SELECT * FROM settings LIMIT 1")

    if not exists:
        await conn.execute("""
        INSERT INTO settings (total_gifts, distributed_gifts)
        VALUES (50, 0)
        """)

    await conn.close()


async def get_stats():
    conn = await connect_db()
    row = await conn.fetchrow("SELECT total_gifts, distributed_gifts FROM settings LIMIT 1")
    await conn.close()

    total = row["total_gifts"]
    distributed = row["distributed_gifts"]
    left = total - distributed

    return total, distributed, left


async def add_gifts(count: int):
    conn = await connect_db()
    await conn.execute("UPDATE settings SET total_gifts = total_gifts + $1 WHERE id = 1", count)
    await conn.close()


async def set_gifts(count: int):
    conn = await connect_db()
    await conn.execute("UPDATE settings SET total_gifts = $1 WHERE id = 1", count)
    await conn.close()


async def check_user_exists(telegram_id: int):
    conn = await connect_db()
    user = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
    await conn.close()
    return user


async def check_xj_id_exists(xj_id: str):
    conn = await connect_db()
    user = await conn.fetchrow("SELECT * FROM users WHERE xj_id = $1", xj_id)
    await conn.close()
    return user


async def save_user(
    telegram_id,
    username,
    telegram_name,
    full_name,
    xj_id,
    qualification,
    phone,
    address
):
    conn = await connect_db()

    settings = await conn.fetchrow("SELECT total_gifts, distributed_gifts FROM settings LIMIT 1")

    total = settings["total_gifts"]
    distributed = settings["distributed_gifts"]

    if distributed >= total:
        await conn.close()
        return None

    gift_number = distributed + 1

    await conn.execute("""
    INSERT INTO users (
        telegram_id, username, telegram_name, full_name,
        xj_id, qualification, phone, address, gift_number
    )
    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
    """, telegram_id, username, telegram_name, full_name, xj_id, qualification, phone, address, gift_number)

    await conn.execute("UPDATE settings SET distributed_gifts = distributed_gifts + 1 WHERE id = 1")

    await conn.close()
    return gift_number
