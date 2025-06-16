# backend/app/api/v1/endpoints/data.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.data_schemas import DataQuerySchema, DataQueryResponseSchema
from app.schemas.user_schemas import UserSchema
from app.services.data_query_service import DataQueryService
from app.api.v1.deps import get_current_active_user, get_data_query_service

logger = logging.getLogger(__name__)

# УБИРАЕМ `tags=["data"]` ОТСЮДА
router = APIRouter()

@router.post(
    "/query",
    response_model=DataQueryResponseSchema,
    summary="Запрос атомарных данных из СКЛАДА",
    description=(
        "Принимает ID документа и возвращает все связанные с ним атомарные записи данных из СКЛАДА (ClickHouse).\n\n"
        "Требует аутентификации."
    ),
    # УБИРАЕМ `tags=["data"]` И ОТСЮДА
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Данные для указанного ID документа не найдены"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"},
    }
)
async def query_data(
    query_params: DataQuerySchema,
    data_service: DataQueryService = Depends(get_data_query_service),
    current_user: UserSchema = Depends(get_current_active_user),
) -> DataQueryResponseSchema:
    try:
        response = await data_service.execute_query(query_params=query_params)
        
        if response is None or not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data for document_id '{query_params.document_id}' not found in Warehouse.",
            )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error while querying data for doc_id {query_params.document_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing your request.",
        )