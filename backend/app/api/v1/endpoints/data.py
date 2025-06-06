# backend/app/api/v1/endpoints/data.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.schemas.data_schemas import (
    DataQuerySchema,
    DataQueryResponseSchema,
    # ExportFormat, # Если будете реализовывать экспорт в этом же файле
    # ExportResponseSchema # Если будете реализовывать экспорт в этом же файле
)
from backend.app.schemas.user_schemas import UserSchema
from backend.app.services.data_query_service import DataQueryService
from backend.app.api.v1.deps import (
    get_current_active_user,
    get_data_query_service,
    # get_optional_data_query_service # Пример, если сервис может быть опциональным
)
# from fastapi import BackgroundTasks # Если будете реализовывать экспорт с фоновыми задачами

router = APIRouter()

@router.post(
    "/query",
    response_model=DataQueryResponseSchema,
    summary="Запрос данных из СКЛАДА",
    description=(
        "Принимает структурированный запрос (фильтры, агрегации, выбор колонок, "
        "сортировку, пагинацию - в будущем) и выполняет его к СКЛАДУ данных (ClickHouse).\n\n"
        "Для MVP принимает только `document_id` для получения всех связанных атомов.\n\n"
        "Требует аутентификации."
    ),
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Невалидные параметры запроса"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Пользователь не аутентифицирован"},
        status.HTTP_403_FORBIDDEN: {"description": "Недостаточно прав для выполнения запроса (если применимо)"},
        status.HTTP_404_NOT_FOUND: {"description": "Данные не найдены для указанного document_id (если применимо)"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера при выполнении запроса к данным"},
    }
)
async def query_data(
    query_params: DataQuerySchema, # Тело запроса будет валидироваться этой схемой
    data_service: DataQueryService = Depends(get_data_query_service),
    current_user: UserSchema = Depends(get_current_active_user),
) -> DataQueryResponseSchema:
    """
    Эндпоинт для выполнения запроса данных из СКЛАДА.
    - Принимает параметры запроса **DataQuerySchema**.
    - Вызывает сервис **DataQueryService** для выполнения запроса.
    - Возвращает результат **DataQueryResponseSchema**, содержащий данные и, возможно, информацию о пагинации.
    - Требует аутентификации пользователя.
    """
    try:
        # В будущем здесь может быть проверка прав доступа current_user к данным
        response_data = await data_service.execute_query(
            query_params=query_params, current_user=current_user
        )
        # Если сервис возвращает пустой список данных, и это считается "не найдено" для API
        # if not response_data.data:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"No data found for document_id: {query_params.document_id}"
        #     )
        return response_data
    except ValueError as ve: # Пример обработки специфической ошибки от сервиса
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        # TODO: Логирование реальной ошибки e
        # logger.error(f"Error querying data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while querying data.",
        )

# TODO: В будущем здесь может быть эндпоинт для экспорта данных /data/export
# @router.post("/export", ...)
# async def export_data(...): ...