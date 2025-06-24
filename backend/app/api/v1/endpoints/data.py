# backend/app/api/v1/endpoints/data.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response

from backend.app.schemas.data_schemas import DataQuerySchema, DataQueryResponseSchema
from backend.app.schemas.user_schemas import UserSchema
from backend.app.services.data_query_service import DataQueryService
from backend.app.api.v1.deps import get_current_active_user, get_data_query_service

logger = logging.getLogger(__name__)

# <<< ДОБАВЛЕН ТЕГ ДЛЯ ГРУППИРОВКИ >>>
router = APIRouter(tags=["Data"])


@router.post(
    "/query",
    response_model=DataQueryResponseSchema,
    summary="Запрос атомарных данных из СКЛАДА",
    description=(
        "Принимает ID документа и возвращает все связанные с ним атомарные записи данных из СКЛАДА (ClickHouse).\n\n"
        "Требует аутентификации."
    ),
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Данные для указанного ID документа не найдены"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера"},
    },
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


# <<< НАЧАЛО НОВОГО ЭНДПОИНТА >>>
@router.post(
    "/{document_id}/flag-for-verification",
    status_code=status.HTTP_202_ACCEPTED,
    summary='Пометить документ для ручной верификации ("Тревожная кнопка")',
    description=(
        "Устанавливает документу статус 'Needs Verification', чтобы он появился "
        "в очереди на проверку у Мейнтейнера. Требует аутентификации."
    ),
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Документ с указанным ID не найден"},
    }
)
async def flag_for_verification(
    document_id: str,
    data_service: DataQueryService = Depends(get_data_query_service),
    current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Эндпоинт для "тревожной кнопки" пользователя.
    """
    try:
        success = await data_service.flag_document_for_verification(
            document_id=document_id,
            user=current_user
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{document_id}' not found.",
            )
        return {"message": "Document has been successfully flagged for verification."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error flagging document {document_id} for verification: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while flagging the document.",
        )
# <<< КОНЕЦ НОВОГО ЭНДПОИНТА >>>