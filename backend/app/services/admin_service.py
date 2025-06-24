# backend/app/services/admin_service.py
from typing import Dict, List

from backend.app.repositories.data_lake_repo import DataLakeRepository
from backend.app.clients.airflow_client import AirflowClient # Предполагаем, что клиент Airflow будет здесь
from backend.app.services.verification_service import VerificationService
from backend.app.schemas.admin_schemas import ReparseRequestSchema
from backend.app.schemas.verification_schemas import VerificationResultSchema, VerificationTaskSchema
from backend.app.utils.logging_utils import get_logger

logger = get_logger(__name__)

class AdminService:
    """
    Сервис для обработки административных задач, таких как ручной репарсинг
    и управление процессом верификации.
    """
    def __init__(
        self,
        data_lake_repo: DataLakeRepository,
        airflow_client: AirflowClient,
        verification_service: VerificationService,
        # user_repo: UserRepo # Может понадобиться для управления пользователями
    ):
        self.data_lake_repo = data_lake_repo
        self.airflow_client = airflow_client
        self.verification_service = verification_service
        # self.user_repo = user_repo

    async def trigger_manual_reparse(
        self, request: ReparseRequestSchema, triggered_by_user: str
    ) -> Dict[str, str]:
        """
        Инициирует ручной репарсинг для списка документов.
        Проверяет существование каждого документа перед запуском DAG.
        """
        statuses: Dict[str, str] = {}
        for doc_id in request.document_ids:
            # 1. Проверяем, существует ли документ в ОЗЕРЕ
            document_metadata = await self.data_lake_repo.get_file_metadata_by_id(doc_id)
            if not document_metadata:
                statuses[doc_id] = "NotFound"
                logger.warning(f"Reparse requested for non-existent document_id: {doc_id}")
                continue

            # 2. Формируем конфигурацию для DAG
            conf = {
                "document_id": doc_id,
                "ontology_version": request.ontology_version,
                "triggered_by": triggered_by_user,
                "is_reparse": True
            }
            
            # 3. Пытаемся запустить DAG
            try:
                # TODO: Когда AirflowClient будет реализован, раскомментировать и адаптировать
                # dag_run_id = await self.airflow_client.trigger_dag(
                #     dag_id="manual_reparse_dag", # ID DAG'а, который запускаем
                #     conf=conf
                # )
                # logger.info(f"Triggered reparse for doc {doc_id} with DAG run ID: {dag_run_id}")
                
                # --- ЗАГЛУШКА ---
                logger.info(f"Simulating trigger of 'manual_reparse_dag' for doc {doc_id} with conf: {conf}")
                # --- КОНЕЦ ЗАГЛУШКИ ---

                statuses[doc_id] = "Triggered"
            except Exception as e:
                logger.error(f"Failed to trigger reparse for doc {doc_id}. Error: {e}", exc_info=True)
                statuses[doc_id] = "Error"
        
        return statuses

    async def get_verification_queue(self, limit: int, offset: int) -> List[VerificationTaskSchema]:
        """
        Делегирует получение очереди верификации в VerificationService.
        """
        logger.info(f"Fetching verification queue with limit={limit}, offset={offset}")
        # Логика приоритизации и выборки находится в VerificationService
        return await self.verification_service.get_verification_tasks(limit=limit, offset=offset)

    async def submit_verification(
        self, result: VerificationResultSchema, verified_by: str
    ) -> bool:
        """
        Делегирует отправку результатов верификации в VerificationService.
        """
        logger.info(f"User '{verified_by}' submitting verification result for doc '{result.document_id}' with status '{result.final_status}'")
        return await self.verification_service.submit_verification_result(
            result=result, 
            verified_by=verified_by
        )