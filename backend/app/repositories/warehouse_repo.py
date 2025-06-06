# backend/app/repositories/warehouse_repo.py
from typing import List, Dict, Any, Optional
from clickhouse_connect.driver.client import Client as ClickHouseClient # Используем синхронный клиент для простоты MVP

from backend.app.schemas.data_schemas import AtomicDataRow # Наша Pydantic схема для атомарных данных

# Название таблицы в ClickHouse, где хранятся атомарные данные.
# Рекомендуется вынести это в конфигурацию (settings), но для MVP можно и так.
ATOMIC_DATA_TABLE_NAME = "scb_warehouse.atomic_data_warehouse" # Пример: база_данных.имя_таблицы

class WarehouseRepo:
    def __init__(self, ch_client: ClickHouseClient):
        """
        Инициализация репозитория с клиентом ClickHouse.

        :param ch_client: Клиент для подключения к ClickHouse.
        """
        self.client = ch_client

    def get_atomic_data_by_document_id(self, document_id: str) -> List[AtomicDataRow]:
        """
        Получает все атомарные записи из ClickHouse для указанного original_document_id.

        :param document_id: Уникальный ID исходного документа, по которому ищутся атомарные данные.
        :return: Список объектов AtomicDataRow.
        """
        # Запрос для выбора всех полей, соответствующих схеме AtomicDataRow.
        # Важно: Перечислите здесь все поля, которые есть в схеме AtomicDataRow
        # и в таблице ATOMIC_DATA_TABLE_NAME, чтобы порядок был корректным
        # или используйте `SELECT *` если уверены в соответствии.
        # Для большей надежности лучше перечислить поля явно.
        # Однако, для простоты MVP и если схема AtomicDataRow точно соответствует таблице,
        # можно использовать SELECT *.
        # Но это менее надежно при изменениях схемы.

        # Собираем список полей из Pydantic модели AtomicDataRow,
        # чтобы они соответствовали порядку в SELECT и при создании экземпляров AtomicDataRow
        # Это более надежно, чем SELECT *
        fields = ", ".join(AtomicDataRow.__fields__.keys())

        query = f"""
            SELECT {fields}
            FROM {ATOMIC_DATA_TABLE_NAME}
            WHERE original_document_id = %(doc_id)s
        """
        parameters = {"doc_id": document_id}

        try:
            # Используем query_df для получения DataFrame, затем конвертируем в dicts,
            # или query_np для NumPy массива, или直接 client.query и обрабатываем result_rows.
            # query_df удобен, если Pandas уже используется.
            # Для простоты и меньших зависимостей, используем client.query
            # и получаем именованные кортежи или словари.

            # client.query() возвращает результат, у которого есть свойство .named_results
            # Это список словарей, где ключи - имена колонок.
            # Или result.rows_with_columns() -> Tuple[Sequence[Tuple], Sequence[str]]
            # Либо result.result_set -> Sequence[Tuple]

            # client.query_arrow(query, parameters=parameters) -> pyarrow.Table
            # client.query_df(query, parameters=parameters) -> pandas.DataFrame

            # Самый простой способ получить список словарей:
            query_result = self.client.query(query, parameters=parameters)
            
            # query_result.result_set - это список кортежей (tuple)
            # query_result.column_names - список имен колонок
            # Соберем список словарей вручную
            
            data_rows: List[Dict[str, Any]] = []
            if query_result.result_set and query_result.column_names:
                for row_tuple in query_result.result_set:
                    data_rows.append(dict(zip(query_result.column_names, row_tuple)))
            
            # Преобразуем каждый словарь в Pydantic модель AtomicDataRow
            # Это также выполнит валидацию данных по типам
            atomic_data_objects = [AtomicDataRow(**row) for row in data_rows]
            return atomic_data_objects
            
        except Exception as e:
            # Здесь должна быть логика обработки ошибок, например, логирование
            print(f"Error querying ClickHouse: {e}")
            # В реальном приложении можно выбросить кастомное исключение
            # или вернуть пустой список, в зависимости от требований
            return []

# Пример использования (не для FastAPI, а для локального теста):
# if __name__ == '__main__':
#     from backend.app.core.config import settings # Предполагаем, что настройки ClickHouse есть там
#     
#     # Проверьте, что у вас есть переменные окружения для ClickHouse или настройте settings
#     try:
#         client = ClickHouseClient(
#             host=settings.CLICKHOUSE_HOST,
#             port=settings.CLICKHOUSE_PORT,
#             user=settings.CLICKHOUSE_USER,
#             password=settings.CLICKHOUSE_PASSWORD,
#             database=settings.CLICKHOUSE_DB_FOR_SCB_WAREHOUSE # Убедитесь, что эта переменная есть в settings
#         )
#         if not client.is_active: # Проверка соединения
#             client.connect()
#
#         repo = WarehouseRepo(ch_client=client)
#         
#         # Замените 'your_test_document_id' на реальный ID из вашей БД
#         test_doc_id = "your_test_document_id" 
#         results = repo.get_atomic_data_by_document_id(test_doc_id)
#         
#         if results:
#             print(f"Found {len(results)} atomic data rows for document_id {test_doc_id}:")
#             for row_obj in results:
#                 print(row_obj.model_dump_json(indent=2)) # Используем model_dump_json для Pydantic v2+
#         else:
#             print(f"No atomic data found for document_id {test_doc_id}")
#
#     except Exception as e:
#         print(f"An error occurred during example usage: {e}")
#     finally:
#         if 'client' in locals() and client.is_active:
#             client.close()