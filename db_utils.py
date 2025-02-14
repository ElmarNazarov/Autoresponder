import asyncpg, datetime
import asyncio
from config import DATABASE_URL

pool = None

async def connect_db(database_url=DATABASE_URL):
    global pool
    if pool is None:
        try:
            pool = await asyncpg.create_pool(database_url)
            print("Success")
        except Exception as e:
            print(f"Error: {e}")
            return None
    return pool

async def create_tables():
    pool = await connect_db()
    if not pool:
        return
    
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE,
                username TEXT,
                full_name TEXT,
                joined_at TIMESTAMP DEFAULT NOW()
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_broadcasts (
                id SERIAL PRIMARY KEY,
                message TEXT NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                sent BOOLEAN DEFAULT FALSE
            );
        """)

async def add_user(telegram_id, username, full_name):
    pool = await connect_db()
    if not pool:
        return

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (telegram_id, username, full_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) DO NOTHING;
        """, telegram_id, username, full_name)

async def get_all_users():
    pool = await connect_db()
    if not pool:
        return []
    
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT telegram_id FROM users")
        return [row["telegram_id"] for row in rows]

async def get_user_count():
    pool = await connect_db()
    if not pool:
        return 0

    async with pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM users;")
    return count

async def close_db():
    global pool
    if pool:
        await pool.close()

async def add_scheduled_broadcast(message: str, scheduled_time: datetime.datetime):
    pool = await connect_db()
    if not pool:
        return
    
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO scheduled_broadcasts (message, scheduled_time)
            VALUES ($1, $2);
        """, message, scheduled_time)

async def get_scheduled_broadcasts():
    pool = await connect_db()
    if not pool:
        return []
    
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, message, scheduled_time FROM scheduled_broadcasts WHERE sent = FALSE;
        """)
        return rows

async def mark_broadcast_as_sent(broadcast_id: int):
    pool = await connect_db()
    if not pool:
        return
    
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE scheduled_broadcasts SET sent = TRUE WHERE id = $1;
        """, broadcast_id)
