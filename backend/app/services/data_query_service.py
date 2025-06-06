# backend/app/services/data_query_service.py
from typing import List, Optional

from backend.app.repositories.warehouse_repo import WarehouseRepo
from backend.app.schemas.data_schemas import (
    DataQuerySchema,
    DataQueryResponseSchema,
    AtomicDataRow,
    # PaginationInfo # Раскомментируйте, если будете реализовывать пагинацию
)
from backend.app.schemas.user_schemas import UserSchema # Для логирования или авторизации на уровне данных в будущем

# Если в будущем понадобится работа с онтологией для формирования запросов
# from backend.app.repositories.ontology_repo import OntologyRepo
# from backend.app.schemas.ontology_schemas import OntologySchema

class DataQueryService:
    def __init__(
        self,
        warehouse_repo: WarehouseRepo,
        # ontology_repo: OntologyRepo # Раскомментируйте, если понадобится онтология
    ):
        """
        Инициализация сервиса запроса данных.

        :param warehouse_repo: Репозиторий для взаимодействия со СКЛАДом (ClickHouse).
        # :param ontology_repo: Репозиторий для взаимодействия с Онтологией (MongoDB).
        """
        self.warehouse_repo = warehouse_repo
        # self.ontology_repo = ontology_repo

    async def execute_query(
        self, query_params: DataQuerySchema, current_user: UserSchema
    ) -> DataQueryResponseSchema:
        """
        Выполняет запрос данных из СКЛАДА на основе переданных параметров.
        Для MVP просто извлекает все атомы по document_id.

        :param query_params: Параметры запроса (содержит document_id).
        :param current_user: Текущий аутентифицированный пользователь (для аудита/авторизации).
        :return: Объект DataQueryResponseSchema с результатами запроса.
        """
        # TODO: Логирование запроса от current_user (можно использовать LogRepo в будущем)
        # print(f"User {current_user.username} requested data for document_id: {query_params.document_id}")

        # Для MVP мы просто получаем все атомарные данные по document_id
        # В будущем здесь может быть более сложная логика:
        # 1. Получение актуальной онтологии (через self.ontology_repo)
        # 2. Формирование SQL запроса на основе query_params и онтологии
        #    (например, выбор конкретных колонок, применение фильтров, агрегаций, сортировки)
        # 3. Выполнение запроса через self.warehouse_repo
        # 4. Обработка пагинации (если есть)

        atomic_data_rows: List[AtomicDataRow] = self.warehouse_repo.get_atomic_data_by_document_id(
            document_id=query_params.document_id
        )

        # Для MVP пагинацию не реализуем, но схема ответа ее поддерживает как Optional
        # pagination_info: Optional[PaginationInfo] = None
        # if query_params.pagination:
        #     # Логика для вычисления пагинации, если бы она была
        #     pass

        return DataQueryResponseSchema(
            data=atomic_data_rows,
            # pagination=pagination_info # Раскомментируйте, если пагинация будет
        )

# Пример использования (не для FastAPI, а для локального теста, если бы методы были синхронными):
# if __name__ == '__main__':
#     from unittest.mock import MagicMock
#
#     # Мокируем зависимости
#     mock_ch_client = MagicMock(spec=ClickHouseClient)
#     mock_warehouse_repo = WarehouseRepo(ch_client=mock_ch_client)
#     
#     # Пример возвращаемых данных из репозитория
#     mock_atomic_data = [
#         AtomicDataRow(indicator_name="Test Indicator", periodicity="Annual", date_start="2023-01-01", date_end="2023-12-31", 
#                       geo_country="RU", unit="%", source="Test", original_document_id="test_doc_1", 
#                       load_timestamp="2023-10-27T10:00:00", ontology_version="1.0", value=Decimal("10.5"))
#     ]
#     mock_warehouse_repo.get_atomic_data_by_document_id = MagicMock(return_value=mock_atomic_data)
#
#     service = DataQueryService(warehouse_repo=mock_warehouse_repo)
#     
#     # Мок пользователя и параметров запроса
#     mock_user = UserSchema(id="user1", username="testuser", email="test@example.com", is_active=True, role="user")
#     mock_query_params = DataQuerySchema(document_id="test_doc_1")
#     
#     # Для асинхронного выполнения в тесте:
#     # import asyncio
#     # async def run_test():
#     #     response = await service.execute_query(query_params=mock_query_params, current_user=mock_user)
#     #     print(response.model_dump_json(indent=2))
#     # asyncio.run(run_test())
#
#     # Для синхронного примера (если бы execute_query был синхронным):
#     # response = service.execute_query(query_params=mock_query_params, current_user=mock_user)
#     # print(response.model_dump_json(indent=2))