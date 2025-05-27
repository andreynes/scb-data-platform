# backend/tests/conftest.py
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi.testclient import TestClient # Если вы предпочитаете TestClient

from backend.app.main import app # Импортируем ваше FastAPI приложение

@pytest.fixture(scope="session") # или "module"
def event_loop():
    # Эта фикстура нужна для pytest-asyncio
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Асинхронный клиент для тестирования API эндпоинтов.
    """
    async with AsyncClient(app=app, base_url=f"http://testserver") as ac:
        yield ac

# Если вы предпочитаете TestClient для синхронных вызовов (менее предпочтительно для async FastAPI)
# @pytest.fixture
# def sync_client() -> TestClient:
#     return TestClient(app)