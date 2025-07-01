# backend/app/repositories/warehouse_repo.py
from typing import List, Dict, Any, Optional
from clickhouse_connect.driver.client import Client as SyncClient
from schemas.verification_schemas import CorrectionInfo
from utils.logging_utils import get_logger

logger = get_logger(__name__)

class WarehouseRepo: 
    def __init__(self, ch_client: SyncClient):
        self.client = ch_client
        self.table_name = "scb_warehouse.atomic_data_warehouse"

    # Функция уже синхронная, все верно
    def get_atomic_data_by_doc_id(self, document_id: str) -> Optional[List[Dict[str, Any]]]:
        """Получает все атомарные данные для указанного ID документа."""
        logger.info(f"Querying warehouse for document_id: {document_id}")
        query = f"SELECT * FROM {self.table_name} WHERE original_document_id = %(doc_id)s"
        
        try:
            result_df = self.client.query_df(query, parameters={"doc_id": document_id})
            records = result_df.to_dict('records')
            logger.info(f"Found {len(records)} records for document_id: {document_id}")
            return records
        except Exception as e:
            logger.error(f"Error querying warehouse for doc_id {document_id}: {e}", exc_info=True)
            # В случае ошибки возвращаем None или пустой список, или пробрасываем ошибку
            raise e


    # Функция уже синхронная, все верно
    def update_atomic_data(self, corrections: List[CorrectionInfo]) -> bool:
        """Применяет исправления к атомарным данным."""
        if not corrections:
            return True

        logger.info(f"Applying {len(corrections)} corrections to the warehouse.")
        
        for correction in corrections:
            # ClickHouse ALTER UPDATE - асинхронная операция на сервере.
            # Для надежности лучше добавить `SETTINGS mutations_sync = 1`
            update_query = (
                f"ALTER TABLE {self.table_name} "
                f"UPDATE `{correction.field_name}` = %(new_value)s "
                f"WHERE _id = %(atom_id)s"
            )
            try:
                self.client.command(
                    update_query, 
                    parameters={
                        "new_value": correction.new_value, 
                        "atom_id": correction.atom_id
                    },
                    settings={'mutations_sync': 1} # Ждем завершения мутации
                )
            except Exception as e:
                logger.error(
                    f"Failed to apply correction for atom_id {correction.atom_id} "
                    f"on field {correction.field_name}. Error: {e}", exc_info=True
                )
                return False
        
        logger.info("Successfully applied corrections.")
        return True