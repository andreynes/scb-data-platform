# backend/app/repositories/ontology_repo.py
from typing import Optional, Dict, Any
from pymongo.database import Database # Используем синхронный Pymongo для простоты на этом этапе
# Если вы планируете использовать Motor для асинхронности, импорт будет другим:
# from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings 

# Имена коллекций можно вынести в конфигурацию или определить здесь
ONTOLOGY_STATUS_COLLECTION = "ontology_status"
ONTOLOGY_SCHEMAS_COLLECTION = "ontology_schemas"
# ONTOLOGY_VOCABULARIES_COLLECTION = "ontology_vocabularies" # Для будущих этапов

class OntologyRepo:
    _db: Database # Или AsyncIOMotorDatabase

    def __init__(self, db: Database): # Или AsyncIOMotorDatabase
        self._db = db

    async def _get_active_ontology_version_id(self) -> Optional[str]:
        """
        Приватный метод для получения ID активной версии онтологии.
        В MVP это может быть просто чтение документа с известным ID.
        """
        # В MVP, документ статуса может иметь фиксированный _id, например, "active_ontology_config"
        # И содержать поле "active_version"
        status_doc = await self._db[ONTOLOGY_STATUS_COLLECTION].find_one({"_id": "active_ontology_config"})
        if status_doc:
            return status_doc.get("active_version")
        return None

    async def get_ontology_schema_by_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает документ схемы онтологии по ее ID (версии).
        """
        # Предполагается, что документы схем хранятся с _id равным их версии
        schema_doc = await self._db[ONTOLOGY_SCHEMAS_COLLECTION].find_one({"_id": version_id})
        return schema_doc