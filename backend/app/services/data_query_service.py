# backend/app/services/data_query_service.py

from typing import List, Optional

# Импорт репозиториев
from backend.app.repositories.warehouse_repo import WarehouseRepository
from backend.app.repositories.data_lake_repo import DataLakeRepository

# Импорт сервисов
from backend.app.services.ontology_service import OntologyService

# Импорт схем
from backend.app.schemas.data_schemas import DataQuerySchema, DataQueryResponseSchema
from backend.app.schemas.user_schemas import UserSchema

# Импорт логгера
from backend.app.utils.logging_utils import get_logger

logger = get_logger(__name__)


class DataQueryService:
    def __init__(
        self,
        warehouse_repo: WarehouseRepository,
        ontology_service: OntologyService,
        data_lake_repo: DataLakeRepository, # <<< ДОБАВЛЕНА ЗАВИСИМОСТЬ
    ):
        """
        Инициализирует сервис с необходимыми репозиториями и другими сервисами.
        """
        self.warehouse_repo = warehouse_repo
        self.ontology_service = ontology_service
        self.data_lake_repo = data_lake_repo # <<< ДОБАВЛЕНА ЗАВИСИМОСТЬ


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
        
    # <<< НАЧАЛО НОВОГО МЕТОДА >>>
    async def flag_document_for_verification(self, document_id: str, user: UserSchema) -> bool:
        """
        Помечает документ как требующий верификации по запросу пользователя ("Тревожная кнопка").
        Возвращает True в случае успеха, иначе False.
        """
        logger.info(f"User '{user.username}' is flagging document '{document_id}' for verification.")

        # Этот метод должен обновлять поле статуса в MongoDB
        # и, опционально, записывать причину
        success = await self.data_lake_repo.update_processing_status_sync(
            document_id=document_id,
            status="Needs Verification",
            error_message=f"Flagged for review by user: {user.username}"
        )
        if not success:
            logger.warning(
                f"Could not flag document for verification: Document ID '{document_id}' not found in Data Lake."
            )
        return success
    # <<< КОНЕЦ НОВОГО МЕТОДА >>>