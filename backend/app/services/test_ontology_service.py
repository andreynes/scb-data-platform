# backend/tests/services/test_ontology_service.py
import pytest
from unittest.mock import AsyncMock # Для мокирования асинхронных методов
# Если синхронно: from unittest.mock import Mock

from backend.app.services.ontology_service import OntologyService
from backend.app.repositories.ontology_repo import OntologyRepo # Нужен для type hinting мока
from backend.app.schemas.ontology_schemas import OntologySchema, OntologyAttribute

@pytest.mark.asyncio
async def test_get_current_ontology_schema_success():
    # --- Setup ---
    mock_ontology_repo = AsyncMock(spec=OntologyRepo) # Создаем мок репозитория

    # Настраиваем, что вернет _get_active_ontology_version_id
    mock_ontology_repo._get_active_ontology_version_id.return_value = "v1.2"

    # Настраиваем, что вернет get_ontology_schema_by_version
    test_schema_dict_from_db = {
        "_id": "v1.2", # MongoDB обычно имеет _id
        "version": "v1.2",
        "description": "Ontology v1.2",
        "attributes": [
            {"name": "country", "type": "string", "description": "Country", "role": "dimension"},
            {"name": "population", "type": "integer", "description": "Population", "role": "measure"}
        ],
        "hierarchies": {"geo": ["country_group", "country"]}
    }
    mock_ontology_repo.get_ontology_schema_by_version.return_value = test_schema_dict_from_db

    ontology_service = OntologyService(ontology_repo=mock_ontology_repo)

    # --- Action ---
    result_schema = await ontology_service.get_current_ontology_schema()

    # --- Assert ---
    assert result_schema is not None
    assert isinstance(result_schema, OntologySchema)
    assert result_schema.version == "v1.2"
    assert result_schema.description == "Ontology v1.2"
    assert len(result_schema.attributes) == 2
    assert result_schema.attributes[0].name == "country"
    assert result_schema.attributes[1].type == "integer"
    assert result_schema.hierarchies is not None
    assert result_schema.hierarchies["geo"] == ["country_group", "country"]

    # Проверяем, что методы репозитория были вызваны с правильными аргументами
    mock_ontology_repo._get_active_ontology_version_id.assert_called_once()
    mock_ontology_repo.get_ontology_schema_by_version.assert_called_once_with("v1.2")

@pytest.mark.asyncio
async def test_get_current_ontology_schema_no_active_version():
    mock_ontology_repo = AsyncMock(spec=OntologyRepo)
    mock_ontology_repo._get_active_ontology_version_id.return_value = None # Нет активной версии

    ontology_service = OntologyService(ontology_repo=mock_ontology_repo)
    result_schema = await ontology_service.get_current_ontology_schema()

    assert result_schema is None
    mock_ontology_repo.get_ontology_schema_by_version.assert_not_called() # Не должен вызываться

@pytest.mark.asyncio
async def test_get_current_ontology_schema_no_schema_for_active_version():
    mock_ontology_repo = AsyncMock(spec=OntologyRepo)
    mock_ontology_repo._get_active_ontology_version_id.return_value = "v1.3"
    mock_ontology_repo.get_ontology_schema_by_version.return_value = None # Схема не найдена

    ontology_service = OntologyService(ontology_repo=mock_ontology_repo)
    result_schema = await ontology_service.get_current_ontology_schema()

    assert result_schema is None
    mock_ontology_repo.get_ontology_schema_by_version.assert_called_once_with("v1.3")

@pytest.mark.asyncio
async def test_get_current_ontology_schema_pydantic_validation_error():
    mock_ontology_repo = AsyncMock(spec=OntologyRepo)
    mock_ontology_repo._get_active_ontology_version_id.return_value = "v1.4"
    # Невалидная схема (например, отсутствует обязательное поле 'attributes')
    invalid_schema_dict = {"_id": "v1.4", "version": "v1.4"}
    mock_ontology_repo.get_ontology_schema_by_version.return_value = invalid_schema_dict

    ontology_service = OntologyService(ontology_repo=mock_ontology_repo)
    result_schema = await ontology_service.get_current_ontology_schema()

    assert result_schema is None # Ожидаем None при ошибке валидации Pydantic