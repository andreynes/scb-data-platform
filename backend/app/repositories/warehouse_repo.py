from typing import List, Dict, Any, Optional
from clickhouse_connect.driver.client import AsyncClient
from backend.app.schemas.data_schemas import AtomicDataRow

class WarehouseRepo:
    def __init__(self, ch_client: AsyncClient):
        """
        Инициализирует репозиторий с активным клиентом ClickHouse.
        """
        self.client = ch_client
        # Название таблицы может быть вынесено в конфигурацию в будущем
        self.table_name = "scb_warehouse.atomic_data_warehouse"

    async def get_atomic_data_by_doc_id(self, document_id: str) -> List[AtomicDataRow]:
        """
        Извлекает все атомарные записи, связанные с конкретным ID исходного документа.
        """
        query = f"SELECT * FROM {self.table_name} WHERE original_document_id = %(doc_id)s"
        params = {"doc_id": document_id}
        
        # Выполняем запрос. query_df возвращает результат в виде Pandas DataFrame
        result_df = await self.client.query_df(query, parameters=params)
        
        if result_df.empty:
            return []

        # Преобразуем DataFrame в список Pydantic моделей AtomicDataRow
        # Pydantic автоматически валидирует каждую строку
        atomic_rows = [
            AtomicDataRow.from_orm(row) for row in result_df.to_dict('records')
        ]
        
        return atomic_rows