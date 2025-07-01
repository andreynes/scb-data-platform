# backend/tests/api/v1/test_ontology_api.py
import pytest
from httpx import AsyncClient
from fastapi import status

# Предполагаем, что фикстура `client` доступна из conftest.py и это AsyncClient
# Также нужна фикстура для мокирования OntologyService или его зависимостей

# Для MVP можно пока не защищать эндпоинт, поэтому user_token_headers не нужен
# from backend.app.tests.utils.user import user_token_headers # Если эндпоинт защищен

from core.config import settings
from schemas.ontology_schemas import OntologySchema # Для проверки типа ответа

# Путь к эндпоинту
ONTOLOGY_SCHEMA_ENDPOINT = f"{settings.API_V1_STR}/ontology/schema"

@pytest.mark.asyncio
async def test_get_current_ontology_schema_success(
    client: AsyncClient, mocker # mocker из pytest-mock
):
    # --- Setup ---
    # Мокируем OntologyService.get_current_ontology_schema
    # Предполагаем, что зависимость get_ontology_service будет мокирована
    # или мы мокируем сам метод сервиса, если он будет внедрен напрямую.
    # Для простоты, мокируем метод репозитория, который в итоге вызывается.

    mock_schema_data = {
        "version": "1.0-active",
        "description": "Active test schema",
        "attributes": [
            {"name": "country", "type": "string", "description": "Country Name", "role": "dimension"}
        ]
    }
    # Мокаем метод, который будет вызван сервисом
    # Это проще, чем мокировать всю цепочку зависимостей FastAPI для теста API
    # Предполагаем, что OntologyService.get_current_ontology_schema в итоге вернет Pydantic модель
    # или словарь, который будет преобразован FastAPI в JSON на основе response_model
    
    # Мокаем get_ontology_service, чтобы он вернул мок-сервис
    mock_ontology_service_instance = mocker.AsyncMock()
    mock_ontology_service_instance.get_current_ontology_schema.return_value = OntologySchema(**mock_schema_data)

    # Переопределяем зависимость в приложении для этого теста
    # Это продвинутая техника, требующая понимания FastAPI dependency overrides.
    # Проще мокировать на уровне сервиса или репозитория, который он вызывает.
    # Если мы не используем dependency_overrides, то нужно мокировать сам OntologyService
    # или его зависимости (OntologyRepo) на уровне модуля перед импортом в эндпоинт.

    # Для этого теста предположим, что OntologyService.get_current_ontology_schema
    # уже мокирован так, чтобы вернуть Pydantic модель OntologySchema(**mock_schema_data)
    # Это можно сделать через mocker.patch('backend.app.services.ontology_service.OntologyService.get_current_ontology_schema')
    # или через dependency_overrides, если вы используете фикстуру, которая это делает.
    
    # Давайте мокнем сервис через `app.dependency_overrides` (требует фикстуры `app`)
    # Это более сложный вариант для начала.
    # Вместо этого, предположим, что мы будем мокировать OntologyRepo, как это делается в тестах сервисов
    # и сервис будет использовать этот мок.
    # Но для API теста, мы обычно проверяем интеграцию, поэтому мокируем только внешние вызовы (БД).
    # Поскольку у нас уже есть OntologyService, который мокирует OntologyRepo,
    # мы можем мокировать сам OntologyService.get_current_ontology_schema

    mocker.patch(
        'backend.app.services.ontology_service.OntologyService.get_current_ontology_schema',
        return_value=OntologySchema(**mock_schema_data)
    )


    # --- Action ---
    # Если эндпоинт защищен, нужны headers=user_token_headers
    response = await client.get(ONTOLOGY_SCHEMA_ENDPOINT)

    # --- Assert ---
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["version"] == "1.0-active"
    assert len(response_data["attributes"]) == 1
    assert response_data["attributes"][0]["name"] == "country"

@pytest.mark.asyncio
async def test_get_current_ontology_schema_not_found(
    client: AsyncClient, mocker
):
    # Мокируем сервис, чтобы он вернул None
    mocker.patch(
        'backend.app.services.ontology_service.OntologyService.get_current_ontology_schema',
        return_value=None
    )

    response = await client.get(ONTOLOGY_SCHEMA_ENDPOINT)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Active ontology schema not found"