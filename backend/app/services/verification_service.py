# backend/app/services/verification_service.py
from typing import List, Optional

from backend.app.repositories.data_lake_repo import DataLakeRepository
from backend.app.repositories.warehouse_repo import WarehouseRepository
from backend.app.schemas.verification_schemas import (
    VerificationDataSchema,
    VerificationResultSchema,
    VerificationTaskSchema,
)
from backend.app.utils.logging_utils import get_logger

logger = get_logger(__name__)

class VerificationService:
    def __init__(
        self,
        data_lake_repo: DataLakeRepository,
        warehouse_repo: WarehouseRepository,
    ):
        self.data_lake_repo = data_lake_repo
        self.warehouse_repo = warehouse_repo

    async def get_verification_tasks(self, limit: int, offset: int) -> List[VerificationTaskSchema]:
        """Получает список задач на верификацию."""
        logger.info("Fetching verification tasks from data lake.")
        # TODO: Добавить логику приоритизации на основе логов или вероятности
        files = await self.data_lake_repo.get_files_for_verification(limit=limit, offset=offset)
        return [VerificationTaskSchema(**file) for file in files]

    async def get_data_for_verification(self, task_id: str) -> Optional[VerificationDataSchema]:
        """Получает данные для одной задачи верификации."""
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

    async def submit_verification_result(self, result: VerificationResultSchema, verified_by: str) -> bool:
        """
        Сохраняет результат верификации (только статус, без исправлений).
        """
        logger.info(f"Submitting verification status for doc {result.document_id}")
        # На этом этапе мы только обновляем статус в метаданных
        # Обновление данных в СКЛАДЕ будет на Этапе 5
        success = await self.data_lake_repo.update_processing_status_sync(
            document_id=result.document_id,
            status=result.final_status.value,
            verified_by=verified_by
        )
        return success