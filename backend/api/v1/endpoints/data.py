# backend/app/api/v1/endpoints/data.py
import logging
import io
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse

from schemas.data_schemas import DataQuerySchema, DataQueryResponseSchema, ExportFormat
from schemas.user_schemas import UserSchema
from services.data_query_service import DataQueryService
from api.v1.deps import get_current_active_user, get_data_query_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Data"])

@router.post(
    "/query",
    response_model=DataQueryResponseSchema,
    summary="Запрос атомарных данных из СКЛАДА",
)
async def query_data(
    query_params: DataQuerySchema,
    data_service: DataQueryService = Depends(get_data_query_service),
    current_user: UserSchema = Depends(get_current_active_user),
) -> DataQueryResponseSchema:
    if not query_params.document_id:
        raise HTTPException(status_code=400, detail="Document ID must be provided.")
    
    try:
        # --- ИЗМЕНЕНИЕ: Убираем await, т.к. вызываем синхронный метод ---
        response = data_service.execute_query(
            query_params=query_params, user=current_user
        )
        # --- КОНЕЦ ИЗМЕНЕНИЯ ---
        
        if response is None or not response.data:
            raise HTTPException(status_code=404, detail="Data not found.")
        return response
    except Exception as e:
        logger.error(f"Error querying data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.post("/export")
async def export_data(
    query_params: DataQuerySchema,
    format: ExportFormat = Query(..., description="Формат экспорта: 'excel' или 'csv'"),
    data_service: DataQueryService = Depends(get_data_query_service),
    current_user: UserSchema = Depends(get_current_active_user),
):
    try:
        # --- ИЗМЕНЕНИЕ: Убираем await ---
        file_bytes = data_service.prepare_export_data(
            query_params=query_params, format=format, user=current_user
        )
        # --- КОНЕЦ ИЗМЕНЕНИЯ ---
        
        if not file_bytes:
            raise HTTPException(status_code=404, detail="No data to export.")

        file_extension = "xlsx" if format == ExportFormat.EXCEL else "csv"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if format == ExportFormat.EXCEL else "text/csv"
        filename = f"export_{query_params.document_id or 'custom'}.{file_extension}"
        
        return StreamingResponse(io.BytesIO(file_bytes), media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception as e:
        logger.error(f"Error during data export: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error creating export file.")

@router.post("/{document_id}/flag-for-verification", status_code=status.HTTP_202_ACCEPTED)
async def flag_for_verification(
    document_id: str,
    data_service: DataQueryService = Depends(get_data_query_service),
    current_user: UserSchema = Depends(get_current_active_user),
):
    # Этот метод асинхронный, т.к. работает с MongoDB
    success = await data_service.flag_document_for_verification(
        document_id=document_id, user=current_user
    )
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": "Document flagged for verification."}