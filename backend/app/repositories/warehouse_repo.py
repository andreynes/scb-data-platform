# backend/app/repositories/warehouse_repo.py

from typing import List, Dict, Any, Optional
# Используем СИНХРОННЫЙ клиент
from clickhouse_connect.driver.client import Client as SyncClient
from app.schemas.verification_schemas import CorrectionInfo
from app.utils.logging_utils import get_logger

logger = get_logger(__name__)

# Переименовал класс для консистентности с другими репозиториями
class WarehouseRepo: 
    def __init__(self, ch_client: SyncClient):
        self.client = ch_client
        self.table_name = "scb_warehouse.atomic_data_warehouse"

    # Убираем 'async'
    def get_atomic_data_by_doc_id(self, document_id: str) -> Optional[List[Dict[str, Any]]]:
        """Получает все атомарные данные для указанного ID документа."""
        query = f"SELECT * FROM {self.table_name} WHERE original_document_id = %(doc_id)s"
        
        # Убираем 'await'
        result_df = self.client.query_df(query, parameters={"doc_id": document_id})
        
        return result_df.to_dict('records') if not result_df.empty else []

    # Убираем 'async'
    def update_atomic_data(self, corrections: List[CorrectionInfo]) -> bool:
        """
        Применяет исправления к атомарным данным.
        """
        if not corrections:
            return True

        logger.info(f"Applying {len(corrections)} corrections to the warehouse.")
        
        for correction in corrections:
            update_query = (
                f"ALTER TABLE {self.table_name} "
                f"UPDATE `{correction.field_name}` = %(new_value)s "
                f"WHERE _id = %(atom_id)s"
            )
            try:
                # Убираем 'await'
                self.client.command(
                    update_query, 
                    parameters={
                        "new_value": correction.new_value, 
                        "atom_id": correction.atom_id
                    }
                )
            except Exception as e:
                logger.error(
                    f"Failed to apply correction for atom_id {correction.atom_id} "
                    f"on field {correction.field_name}. Error: {e}", exc_info=True
                )
                return False
        
        logger.info("Successfully applied corrections.")
        return True