# backend/app/services/data_query_service.py

from typing import List, Optional
import pandas as pd
import io

# Импорт репозиториев
from repositories.warehouse_repo import WarehouseRepo
from repositories.data_lake_repo import DataLakeRepo

# Импорт сервисов
from services.ontology_service import OntologyService

# Импорт схем
from schemas.data_schemas import (
    DataQuerySchema, 
    DataQueryResponseSchema,
    ExportFormat # <<< НОВЫЙ ИМПОРТ
)
from schemas.user_schemas import UserSchema

# Импорт логгера
from utils.logging_utils import get_logger

logger = get_logger(__name__)


class DataQueryService:
    def __init__(
        self,
        warehouse_repo: WarehouseRepo,
        ontology_service: OntologyService,
        data_lake_repo: DataLakeRepo,
    ):
        """
        Инициализирует сервис с необходимыми репозиториями и другими сервисами.
        """
        self.warehouse_repo = warehouse_repo
        self.ontology_service = ontology_service
        self.data_lake_repo = data_lake_repo


    async def execute_query(
        self, query_params: DataQuerySchema
    ) -> Optional[DataQueryResponseSchema]:
        """
        Основной метод для выполнения запроса данных по параметрам.
        """
        if not query_params.document_id:
            return None 

        atomic_data = await self.warehouse_repo.get_atomic_data_by_doc_id(
            document_id=query_params.document_id
        )

        if not atomic_data:
            return DataQueryResponseSchema(data=[])

        return DataQueryResponseSchema(data=atomic_data)
        
    async def flag_document_for_verification(self, document_id: str, user: UserSchema) -> bool:
        """
        Помечает документ как требующий верификации по запросу пользователя ("Тревожная кнопка").
        """
        logger.info(f"User '{user.username}' is flagging document '{document_id}' for verification.")
        
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
        
    # <<< НАЧАЛО НОВОГО МЕТОДА ДЛЯ ЭКСПОРТА >>>
    async def prepare_export_data(
        self, query_params: DataQuerySchema, format: ExportFormat
    ) -> bytes:
        """
        Готовит файл для экспорта (без пагинации).
        Возвращает содержимое файла в виде байтов.
        """
        logger.info(f"Preparing '{format.value}' export for document '{query_params.document_id}'")
        
        if not query_params.document_id:
            logger.warning("No document_id provided for export.")
            return b""
            
        all_atomic_data = await self.warehouse_repo.get_atomic_data_by_doc_id(
            document_id=query_params.document_id
        )
        
        if not all_atomic_data:
            logger.warning(f"No data found for export for document {query_params.document_id}")
            return b""

        df = pd.DataFrame(all_atomic_data)
        
        # Здесь в будущем можно добавить логику для переименования колонок
        # на основе онтологии для более "человекочитаемого" экспорта.
        
        output = io.BytesIO()
        if format == ExportFormat.EXCEL:
            # Используем openpyxl как движок для поддержки .xlsx
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='data')
        elif format == ExportFormat.CSV:
            # utf-8-sig нужен, чтобы Excel корректно открывал CSV с кириллицей
            df.to_csv(output, index=False, sep=';', encoding='utf-8-sig')

        return output.getvalue()
    # <<< КОНЕЦ НОВОГО МЕТОДА >>>