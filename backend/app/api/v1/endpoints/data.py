# backend/app/api/v1/endpoints/data.py
import logging
import io
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse

from app.schemas.data_schemas import DataQuerySchema, DataQueryResponseSchema, ExportFormat
from app.schemas.user_schemas import UserSchema
from app.services.data_query_service import DataQueryService
from app.api.v1.deps import get_current_active_user, get_data_query_service

logger = logging.getLogger(__name__)

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

# <<< НАЧАЛО НОВОГО ЭНДПОИНТА ДЛЯ ЭКСПОРТА >>>
@router.post(
    "/export",
    summary="Экспорт данных в файл",
    description="Формирует и возвращает файл (Excel или CSV) с данными по заданным параметрам запроса.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Данные для экспорта по указанным параметрам не найдены"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Внутренняя ошибка сервера при создании файла"},
    },
)
async def export_data(
    query_params: DataQuerySchema,
    format: ExportFormat = Query(..., description="Формат экспорта: 'excel' или 'csv'"),
    data_service: DataQueryService = Depends(get_data_query_service),
    current_user: UserSchema = Depends(get_current_active_user),
):
    """
    Эндпоинт для синхронного экспорта данных.
    """
    try:
        file_bytes = await data_service.prepare_export_data(
            query_params=query_params, format=format
        )
        
        if not file_bytes:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No data to export for the given query.",
            )

        file_extension = "xlsx" if format == ExportFormat.EXCEL else "csv"
        media_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if format == ExportFormat.EXCEL
            else "text/csv"
        )
        
        filename = f"export_{query_params.document_id or 'custom_query'}.{file_extension}"
        
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"Error during data export: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while creating the export file.",
        )
# <<< КОНЕЦ НОВОГО ЭНДПОИНТА ДЛЯ ЭКСПОРТА >>>

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