import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Forces pytest to use a single event loop across all tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
