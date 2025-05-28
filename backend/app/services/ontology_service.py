# backend/app/services/ontology_service.py
from typing import Optional, Dict, Any
from fastapi import Depends # Если будете использовать FastAPI Depends для внедрения репозитория

from app.repositories.ontology_repo import OntologyRepo
from app.schemas.ontology_schemas import OntologySchema 
# Если репозиторий синхронный, а сервис асинхронный, может понадобиться run_in_threadpool
# from fastapi.concurrency import run_in_threadpool

class OntologyService:
    _ontology_repo: OntologyRepo

    # Репозиторий внедряется через конструктор.
    # В FastAPI это обычно делается через систему зависимостей.
    def __init__(self, ontology_repo: OntologyRepo):
        self._ontology_repo = ontology_repo

    async def get_current_ontology_schema(self) -> Optional[OntologySchema]:
        """
        Получает ID активной версии онтологии, затем саму схему
        и преобразует ее в Pydantic модель.
        """
        active_version_id = await self._ontology_repo._get_active_ontology_version_id()
        if not active_version_id:
            # Логирование: Активная версия не найдена
            # Можно добавить logging.warning(...)
            return None

        schema_dict = await self._ontology_repo.get_ontology_schema_by_version(active_version_id)
        if not schema_dict:
            # Логирование: Схема для активной версии не найдена
            # logging.error(f"Ontology schema for active version '{active_version_id}' not found.")
            return None

        try:
            # Преобразуем словарь из БД в Pydantic модель для валидации и типизации
            return OntologySchema(**schema_dict)
        except Exception as e: # Более конкретно можно ловить pydantic.ValidationError
            # Логирование: Ошибка преобразования/валидации схемы
            # logging.error(f"Error validating ontology schema version '{active_version_id}': {e}")
            return None

# Пример функции зависимости для FastAPI (если будете размещать ее в deps.py)
# def get_ontology_service(ontology_repo: OntologyRepo = Depends(get_ontology_repo)) -> OntologyService:
#     return OntologyService(ontology_repo=ontology_repo)