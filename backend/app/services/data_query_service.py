from typing import List, Optional
from backend.app.repositories.warehouse_repo import WarehouseRepo
from backend.app.schemas.data_schemas import DataQuerySchema, DataQueryResponseSchema, AtomicDataRow
from backend.app.services.ontology_service import OntologyService # Мы создадим его позже, сейчас просто импортируем

class DataQueryService:
    def __init__(self, warehouse_repo: WarehouseRepo, ontology_service: OntologyService):
        """
        Инициализирует сервис с необходимыми репозиториями и другими сервисами.
        """
        self.warehouse_repo = warehouse_repo
        self.ontology_service = ontology_service # Пока не используется, но задел на будущее

    async def execute_query(
        self, query_params: DataQuerySchema
    ) -> Optional[DataQueryResponseSchema]:
        """
        Основной метод для выполнения запроса данных по параметрам.
        В MVP он просто получает данные по ID документа.
        """
        # В будущем здесь будет сложная логика:
        # 1. Получить текущую онтологию через self.ontology_service
        # 2. Сформировать SQL на основе query_params и онтологии
        # 3. Выполнить SQL через self.warehouse_repo

        # --- Логика для MVP ---
        if not query_params.document_id:
            # На случай, если пришел пустой запрос
            return None 

        atomic_data = await self.warehouse_repo.get_atomic_data_by_doc_id(
            document_id=query_params.document_id
        )

        if not atomic_data:
            # Если для этого документа нет данных в СКЛАДЕ
            return DataQueryResponseSchema(data=[])

        # Формируем и возвращаем ответ в соответствии с нашей Pydantic схемой
        return DataQueryResponseSchema(data=atomic_data)