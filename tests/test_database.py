import pytest
import pytest_asyncio
import asyncio
from db_utils import connect_db, add_user, get_user_count


@pytest_asyncio.fixture(scope="session")
async def db_pool(event_loop):
    pool = await connect_db(database_url="postgresql://bot_db_user:bot_db_password@localhost:5432/telegram_bot")
    if not pool:
        pytest.skip("Skipping tests: Database connection failed")
    yield pool
    await pool.close()

@pytest.mark.asyncio
async def test_database_connection(db_pool):
    assert db_pool is not None, "DB connection error"

@pytest.mark.asyncio
async def test_add_user(db_pool):
    await add_user(123456789, "testuser", "Test User")
    count = await get_user_count()
    assert count > 0, "Error: user not added"

@pytest.mark.asyncio
async def test_get_user_count(db_pool):
    count = await get_user_count()
    assert isinstance(count, int), "User count should be an integer"
    assert count >= 0, "User count should not be negative"