import asyncio
import os

import pytest
from async_asgi_testclient import TestClient
from hypothesis import settings
from nextlinegraphql import create_app

if os.getenv('GITHUB_ACTIONS') == 'true':
    settings.register_profile('ci', deadline=None)
    settings.load_profile('ci')


@pytest.fixture
async def client(app):
    async with TestClient(app) as y:
        await asyncio.sleep(0)
        yield y


@pytest.fixture
def app():
    return create_app()
