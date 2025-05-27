# backend/tests/repositories/test_ontology_repo.py
import pytest
from mongomock_motor import AsyncMongoMockClient # Для асинхронного mongomock
# Если синхронно: from mongomock import MongoClient

from backend.app.repositories.ontology_repo import (
    OntologyRepo,
    ONTOLOGY_STATUS_COLLECTION,
    ONTOLOGY_SCHEMAS_COLLECTION
)

@pytest.fixture
async def mock_motor_db(): # Асинхронная фикстура
    client = AsyncMongoMockClient()
    # Для синхронного: client = MongoClient()
    db = client.test_db # Или имя вашей тестовой БД
    # Очистка перед каждым тестом (опционально, но хорошо для изоляции)
    await db[ONTOLOGY_STATUS_COLLECTION].delete_many({})
    await db[ONTOLOGY_SCHEMAS_COLLECTION].delete_many({})
    return db

@pytest.fixture
def ontology_repo(mock_motor_db): # mock_motor_db теперь асинхронная фикстура
    return OntologyRepo(db=mock_motor_db)

@pytest.mark.asyncio
async def test_get_active_ontology_version_id_found(ontology_repo: OntologyRepo, mock_motor_db):
    # Setup: добавляем документ статуса
    await mock_motor_db[ONTOLOGY_STATUS_COLLECTION].insert_one(
        {"_id": "active_ontology_config", "active_version": "v1.1"}
    )

    active_version = await ontology_repo._get_active_ontology_version_id()
    assert active_version == "v1.1"

@pytest.mark.asyncio
async def test_get_active_ontology_version_id_not_found(ontology_repo: OntologyRepo):
    active_version = await ontology_repo._get_active_ontology_version_id()
    assert active_version is None

@pytest.mark.asyncio
async def test_get_ontology_schema_by_version_found(ontology_repo: OntologyRepo, mock_motor_db):
    test_schema = {
        "_id": "v1.0",
        "version": "1.0",
        "description": "Test Schema v1.0",
        "attributes": [{"name": "country", "type": "string", "description": "Страна", "role": "dimension"}]
    }
    await mock_motor_db[ONTOLOGY_SCHEMAS_COLLECTION].insert_one(test_schema)

    schema_doc = await ontology_repo.get_ontology_schema_by_version("v1.0")
    assert schema_doc is not None
    assert schema_doc["version"] == "v1.0"
    assert len(schema_doc["attributes"]) == 1
    assert schema_doc["attributes"][0]["name"] == "country"

@pytest.mark.asyncio
async def test_get_ontology_schema_by_version_not_found(ontology_repo: OntologyRepo):
    schema_doc = await ontology_repo.get_ontology_schema_by_version("v0.9-nonexistent")
    assert schema_doc is None