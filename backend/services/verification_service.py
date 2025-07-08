# backend/app/services/verification_service.py
from typing import List, Optional

from repositories.data_lake_repo import DataLakeRepo
from repositories.warehouse_repo import WarehouseRepo
from schemas.verification_schemas import (
    VerificationDataSchema,
    VerificationResultSchema,
    VerificationTaskSchema,
)
from utils.logging_utils import get_logger

logger = get_logger(__name__)

class VerificationService:
    def __init__(
        self,
        data_lake_repo: DataLakeRepo,
        warehouse_repo: WarehouseRepo,
    ):
        self.data_lake_repo = data_lake_repo
        self.warehouse_repo = warehouse_repo

    async def get_verification_tasks(self, limit: int, offset: int) -> List[VerificationTaskSchema]:
        logger.info("Fetching verification tasks from data lake.")
        files = await self.data_lake_repo.get_files_for_verification(limit=limit, offset=offset)
        return [VerificationTaskSchema(**file) for file in files]

    async def get_data_for_verification(self, task_id: str) -> Optional[VerificationDataSchema]:
        logger.info(f"Fetching data for verification task: {task_id}")
        json_data = await self.data_lake_repo.get_json_representation_by_id(task_id)
        atomic_data = await self.warehouse_repo.get_atomic_data_by_doc_id(task_id)

        if not json_data and not atomic_data:
            return None

        return VerificationDataSchema(
            document_id=task_id,
            json_representation=json_data,
            atomic_data=atomic_data,
        )

    # <<< НАЧАЛО ИЗМЕНЕНИЙ В МЕТОДЕ >>>
    async def submit_verification_result(self, result: VerificationResultSchema, verified_by: str) -> bool:
        """
        Сохраняет результат верификации, включая применение исправлений.
        """
        logger.info(f"Submitting verification result for doc {result.document_id}")
        
        # Шаг 1: Применяем исправления к данным в СКЛАДЕ, если они есть
        if result.corrections:
            logger.info(f"Found {len(result.corrections)} corrections to apply.")
            success = await self.warehouse_repo.update_atomic_data(result.corrections)
            if not success:
                # Если не удалось применить исправления, не меняем статус и сообщаем об ошибке
                logger.error(f"Failed to apply corrections for doc {result.document_id}. Status will not be updated.")
                return False
        
        # Шаг 2: Обновляем статус в ОЗЕРЕ
        status_success = await self.data_lake_repo.update_processing_status_sync(
            document_id=result.document_id,
            status=result.final_status.value,
            verified_by=verified_by
        )
        return status_success
    # <<< КОНЕЦ ИЗМЕНЕНИЙ В МЕТОДЕ >>>