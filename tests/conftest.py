# D:\Github\kitchen\backend\tests\conftest.py
import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

os.environ["DATABASE_NAME"] = "pallavis_kitchen_test"

from app.core.database import database
from app.main import app


TEST_DATABASE_NAME = "pallavis_kitchen_test"


@pytest_asyncio.fixture(scope="session")
async def test_client():
    await database.command("ping")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as async_client:
        yield async_client

    await database.client.drop_database(TEST_DATABASE_NAME)
    await database.client.close()