from typing import List, Dict, Any, Optional

# 1. ИСПРАВЛЕННЫЙ ИМПОРТ
from clickhouse_connect.driver import AsyncClient 
# 2. УДАЛИЛ ЛИШНИЙ `backend.` ИЗ ПУТИ, ТАК КАК МЫ ВНУТРИ ПРИЛОЖЕНИЯ
from app.schemas.data_schemas import AtomicDataRow

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
        # 3. ДОБАВИЛ ПРОВЕРКУ, ЧТО КЛИЕНТ ЖИВ
        if not self.client or not self.client.connected:
            raise Exception("ClickHouse client is not available or not connected")

        query = f"SELECT * FROM {self.table_name} WHERE original_document_id = %(doc_id)s"
        params = {"doc_id": document_id}
        
        # Выполняем запрос. query_df возвращает результат в виде Pandas DataFrame
        result_df = await self.client.query_df(query, parameters=params)
        
        if result_df.empty:
            return []

        # Преобразуем DataFrame в список Pydantic моделей AtomicDataRow
        # В Pydantic v2 используется model_validate вместо from_orm для словарей
        atomic_rows = [
            AtomicDataRow.model_validate(row) for row in result_df.to_dict('records')
        ]
        
        return atomic_rows