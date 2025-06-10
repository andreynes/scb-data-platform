from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.schemas.data_schemas import DataQuerySchema, DataQueryResponseSchema
from backend.app.schemas.user_schemas import UserSchema
from backend.app.services.data_query_service import DataQueryService
from backend.app.api.v1.deps import get_current_active_user, get_data_query_service
# import logging # Рекомендуется для логирования ошибок

# logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/query",
    response_model=DataQueryResponseSchema,
    summary="Запрос атомарных данных из СКЛАДА",
    description=(
        "Принимает ID документа и возвращает все связанные с ним атомарные записи данных из СКЛАДА (ClickHouse).\n\n"
        "Требует аутентификации."
    ),
    tags=["data"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Данные для указанного ID документа не найдены"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"},
        # Статусы 401, 403, 422 будут добавлены в документацию автоматически FastAPI
    }
)
async def query_data(
    query_params: DataQuerySchema,
    data_service: DataQueryService = Depends(get_data_query_service),
    current_user: UserSchema = Depends(get_current_active_user),
) -> DataQueryResponseSchema:
    """
    Эндпоинт для выполнения запроса данных из СКЛАДА по ID документа.
    
    - **query_params**: Тело запроса, содержащее `document_id`.
    - **data_service**: Сервис для выполнения бизнес-логики запроса.
    - **current_user**: Аутентифицированный пользователь.
    """
    try:
        response = await data_service.execute_query(query_params=query_params)
        
        # Сервис может вернуть None или пустой список, если ничего не найдено.
        # Обрабатываем оба случая как 404 Not Found.
        if response is None or not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data for document_id '{query_params.document_id}' not found in Warehouse.",
            )
        return response
    except Exception as e:
        # Логирование ошибки очень важно для отладки в production
        # logger.error(f"Error while querying data for doc_id {query_params.document_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing your request.",
        )