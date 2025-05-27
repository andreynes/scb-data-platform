# backend/tests/schemas/test_ontology_schemas.py
import pytest
from pydantic import ValidationError
from backend.app.schemas.ontology_schemas import OntologyAttribute, OntologySchema

def test_create_ontology_attribute_valid():
    attr_data = {
        "name": "indicator_name",
        "type": "string",
        "description": "Наименование показателя",
        "role": "dimension",
        "vocabulary": "indicators"
    }
    attribute = OntologyAttribute(**attr_data)
    assert attribute.name == "indicator_name"
    assert attribute.type == "string"
    assert attribute.vocabulary == "indicators"

def test_create_ontology_attribute_missing_required_field():
    attr_data = {
        "type": "string",
        "description": "Наименование показателя",
        "role": "dimension"
    }
    with pytest.raises(ValidationError):
        OntologyAttribute(**attr_data)

def test_create_ontology_schema_valid():
    attr1_data = {
        "name": "year", "type": "integer", "description": "Год", "role": "dimension"
    }
    attr2_data = {
        "name": "value", "type": "float", "description": "Значение", "role": "measure"
    }
    schema_data = {
        "version": "1.0",
        "description": "Тестовая схема онтологии",
        "attributes": [attr1_data, attr2_data],
        "hierarchies": {"time": ["year", "month"]}
    }
    ontology_schema = OntologySchema(**schema_data)
    assert ontology_schema.version == "1.0"
    assert len(ontology_schema.attributes) == 2
    assert ontology_schema.attributes[0].name == "year"
    assert ontology_schema.hierarchies is not None
    assert ontology_schema.hierarchies["time"] == ["year", "month"]

def test_create_ontology_schema_minimal_valid():
    attr_data = {
        "name": "country", "type": "string", "description": "Страна", "role": "dimension"
    }
    schema_data = {
        "version": "1.1",
        "attributes": [attr_data]
        # description и hierarchies опциональны
    }
    ontology_schema = OntologySchema(**schema_data)
    assert ontology_schema.version == "1.1"
    assert ontology_schema.description is None
    assert ontology_schema.hierarchies is None

def test_ontology_schema_attributes_must_be_list():
    schema_data = {
        "version": "1.0",
        "attributes": {"name": "year", "type": "integer", "description": "Год", "role": "dimension"} # не список
    }
    with pytest.raises(ValidationError):
        OntologySchema(**schema_data)

def test_ontology_schema_missing_attributes():
    schema_data = {
        "version": "1.0"
        # attributes отсутствует
    }
    with pytest.raises(ValidationError):
        OntologySchema(**schema_data)

# Дополнительные тесты можно добавить для проверки конкретных типов, ролей и т.д.