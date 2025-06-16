# backend/app/api/v1/endpoints/files.py
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status

from app.schemas.file_schemas import FileUploadStatusSchema 
from app.schemas.user_schemas import UserSchema 
from app.services.file_processing_service import FileProcessingService
from app.api.v1.deps import get_current_active_user, get_file_processing_service

router = APIRouter()

@router.post(
    "/files/upload",
    response_model=List[FileUploadStatusSchema], 
    status_code=status.HTTP_202_ACCEPTED,      
    summary="Загрузка одного или нескольких файлов",
    description="Принимает один или несколько файлов, сохраняет их и инициирует ETL-обработку."
)
async def upload_files(
    files: List[UploadFile] = File(..., description="Список файлов для загрузки (Excel, PDF)."),
    current_user: UserSchema = Depends(get_current_active_user),
    file_service: FileProcessingService = Depends(get_file_processing_service)
) -> List[FileUploadStatusSchema]:
    """
    Эндпоинт для загрузки файлов.

    - **files**: Список файлов, переданных в multipart/form-data.
    - **current_user**: Аутентифицированный пользователь (из JWT токена).
    - **file_service**: Экземпляр сервиса для обработки файлов.
    """
    # Простая проверка на тип файла (можно улучшить, проверяя content_type или расширение)
    # Более сложная валидация может быть внутри file_service
    allowed_extensions = {".xlsx", ".xls", ".pdf"}
    for file_item in files:
        if not any(file_item.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неподдерживаемый тип файла: {file_item.filename}. Допустимы: {', '.join(allowed_extensions)}"
            )
    
    try:
        # 
        # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
        # Вместо uploader_id передаем всего пользователя current_user
        # под именем аргумента 'uploader', как того ожидает сервис.
        #
        upload_statuses = await file_service.process_uploaded_files(
            files=files, 
            uploader=current_user 
        )
        return upload_statuses
    except Exception as e:
        # Здесь можно логировать ошибку
        # logger.error(f"Ошибка при загрузке файлов: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера при обработке файлов: {str(e)}"
        )