import logging
from typing import List, Dict, Any, Optional

from clickhouse_connect.driver import AsyncClient
from app.schemas.data_schemas import AtomicDataRow

logger = logging.getLogger(__name__)

class WarehouseRepo:
    def __init__(self, ch_client: AsyncClient):
        """
        Инициализирует репозиторий с активным клиентом ClickHouse.
        """
        self.client = ch_client
        self.table_name = "scb_warehouse.atomic_data_warehouse"

    async def get_atomic_data_by_doc_id(self, document_id: str) -> List[AtomicDataRow]:
        """
        Извлекает все атомарные записи, связанные с конкретным ID исходного документа.
        """
        # УБИРАЕМ ПРОВЕРКУ .connected.
        # Если клиент не создан, приложение упадет раньше, в session.py.
        if not self.client:
            logger.error("WarehouseRepo: ClickHouse client is not available.")
            raise Exception("ClickHouse client is not available")

        query = f"SELECT * FROM {self.table_name} WHERE original_document_id = %(doc_id)s"
        params = {"doc_id": document_id}
        
        #
        # ВАЖНОЕ ИСПРАВЛЕНИЕ: query_df - СИНХРОННЫЙ МЕТОД, await НЕ НУЖЕН
        #
        result_df = self.client.query_df(query, parameters=params)
        
        if result_df.empty:
            return []

        atomic_rows = [
            AtomicDataRow.model_validate(row) for row in result_df.to_dict('records')
        ]
        
        return atomic_rows