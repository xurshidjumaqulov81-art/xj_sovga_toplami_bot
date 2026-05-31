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

    exists = await conn.fetchrow(
        "SELECT * FROM settings LIMIT 1"
    )

    if not exists:
        await conn.execute("""
        INSERT INTO settings
        (total_gifts, distributed_gifts)
        VALUES (50,0)
        """)

    await conn.close()
