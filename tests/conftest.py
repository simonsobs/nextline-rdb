import asyncio

import pytest
from async_asgi_testclient import TestClient
from nextlinegraphql import create_app


@pytest.fixture
async def client(app):
    async with TestClient(app) as y:
        await asyncio.sleep(0)
        yield y


@pytest.fixture
def app():
    return create_app()
