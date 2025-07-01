# backend/app/services/data_query_service.py

from typing import List, Optional
import pandas as pd
import io

from repositories.warehouse_repo import WarehouseRepo
from repositories.data_lake_repo import DataLakeRepo
from services.ontology_service import OntologyService
from schemas.data_schemas import DataQuerySchema, DataQueryResponseSchema, ExportFormat
from schemas.user_schemas import UserSchema
from utils.logging_utils import get_logger

logger = get_logger(__name__)

class DataQueryService:
    def __init__(
        self,
        warehouse_repo: WarehouseRepo,
        ontology_service: OntologyService,
        data_lake_repo: DataLakeRepo,
    ):
        self.warehouse_repo = warehouse_repo
        self.ontology_service = ontology_service
        self.data_lake_repo = data_lake_repo

    # --- ИЗМЕНЕНИЕ: Метод становится СИНХРОННЫМ ---
    def execute_query(
        self, query_params: DataQuerySchema, user: UserSchema
    ) -> Optional[DataQueryResponseSchema]:
        logger.info(f"User '{user.username}' querying data for document '{query_params.document_id}'")
        
        if not query_params.document_id:
            return None 

        # --- ИЗМЕНЕНИЕ: Убираем await ---
        atomic_data = self.warehouse_repo.get_atomic_data_by_doc_id(
            document_id=query_params.document_id
        )

        if not atomic_data:
            return DataQueryResponseSchema(data=[])

        return DataQueryResponseSchema(data=atomic_data)
        
    async def flag_document_for_verification(self, document_id: str, user: UserSchema) -> bool:
        # Этот метод работает с MongoDB (async), поэтому остается async
        logger.info(f"User '{user.username}' is flagging document '{document_id}' for verification.")
        
        success = await self.data_lake_repo.update_processing_status( # Предполагаем, что есть async-версия
            document_id=document_id,
            status="Needs Verification",
            error_message=f"Flagged for review by user: {user.username}"
        )
        if not success:
            logger.warning(f"Could not flag for verification: Document ID '{document_id}' not found.")
        return success
        
    # --- ИЗМЕНЕНИЕ: Метод становится СИНХРОННЫМ ---
    def prepare_export_data(
        self, query_params: DataQuerySchema, format: ExportFormat, user: UserSchema
    ) -> bytes:
        logger.info(f"User '{user.username}' exporting '{format.value}' for document '{query_params.document_id}'")
        
        if not query_params.document_id:
            logger.warning("No document_id provided for export.")
            return b""
            
        # --- ИЗМЕНЕНИЕ: Убираем await ---
        all_atomic_data = self.warehouse_repo.get_atomic_data_by_doc_id(
            document_id=query_params.document_id
        )
        
        if not all_atomic_data:
            logger.warning(f"No data found for export for document {query_params.document_id}")
            return b""

        df = pd.DataFrame(all_atomic_data)
        
        output = io.BytesIO()
        if format == ExportFormat.EXCEL:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='data')
        elif format == ExportFormat.CSV:
            df.to_csv(output, index=False, sep=';', encoding='utf-8-sig')

        return output.getvalue()