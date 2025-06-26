# backend/app/services/admin_service.py
from typing import Dict, List

# ИСПРАВЛЕНО: Правильное имя репозитория
from app.repositories.data_lake_repo import DataLakeRepo
# ЗАКОММЕНТИРОВАНО: Клиент Airflow пока не реализован
# from app.clients.airflow_client import AirflowClient 
from app.services.verification_service import VerificationService
from app.schemas.admin_schemas import ReparseRequestSchema
from app.schemas.verification_schemas import VerificationResultSchema, VerificationTaskSchema
from app.utils.logging_utils import get_logger

logger = get_logger(__name__)

class AdminService:
    def __init__(
        self,
        # ИСПРАВЛЕНО: Правильное имя
        data_lake_repo: DataLakeRepo,
        verification_service: VerificationService,
        # ЗАКОММЕНТИРОВАНО: Убираем пока не реализованный клиент
        # airflow_client: AirflowClient, 
    ):
        self.data_lake_repo = data_lake_repo
        # self.airflow_client = airflow_client
        self.verification_service = verification_service

    async def trigger_manual_reparse(
        self, request: ReparseRequestSchema, triggered_by_user: str
    ) -> Dict[str, str]:
        statuses: Dict[str, str] = {}
        for doc_id in request.document_ids:
            document_metadata = await self.data_lake_repo.get_file_metadata_by_id(doc_id)
            if not document_metadata:
                statuses[doc_id] = "NotFound"
                logger.warning(f"Reparse requested for non-existent document_id: {doc_id}")
                continue

            conf = {
                "document_id": doc_id,
                "ontology_version": request.ontology_version,
                "triggered_by": triggered_by_user,
                "is_reparse": True
            }
            
            try:
                logger.info(f"Simulating trigger of 'manual_reparse_dag' for doc {doc_id} with conf: {conf}")
                statuses[doc_id] = "Triggered"
            except Exception as e:
                logger.error(f"Failed to trigger reparse for doc {doc_id}. Error: {e}", exc_info=True)
                statuses[doc_id] = "Error"
        
        return statuses

    async def get_verification_queue(self, limit: int, offset: int) -> List[VerificationTaskSchema]:
        logger.info(f"Fetching verification queue with limit={limit}, offset={offset}")
        return await self.verification_service.get_verification_tasks(limit=limit, offset=offset)

    async def submit_verification(
        self, result: VerificationResultSchema, verified_by: str
    ) -> bool:
        logger.info(f"User '{verified_by}' submitting verification result for doc '{result.document_id}' with status '{result.final_status}'")
        return await self.verification_service.submit_verification_result(
            result=result, 
            verified_by=verified_by
        )