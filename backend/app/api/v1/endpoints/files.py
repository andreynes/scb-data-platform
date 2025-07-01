# backend/app/api/v1/endpoints/files.py

from typing import List
from fastapi import APIRouter, Depends, UploadFile, File

# --- ИСПРАВЛЕННЫЕ ИМПОРТЫ ---
# Используем абсолютные пути от корня проекта (/app)
from schemas.file_schemas import FileUploadStatusSchema
from schemas.user_schemas import UserSchema
from services.file_processing_service import FileProcessingService
from api.v1.deps import get_current_active_user, get_file_processing_service

router = APIRouter()

@router.post(
    "/upload",
    response_model=List[FileUploadStatusSchema],
    status_code=202, # Accepted
    summary="Загрузка одного или нескольких файлов для обработки",
    tags=["files"]
)
async def upload_files(
    files: List[UploadFile] = File(..., description="Один или несколько файлов для загрузки"),
    file_service: FileProcessingService = Depends(get_file_processing_service),
    current_user: UserSchema = Depends(get_current_active_user),
) -> List[FileUploadStatusSchema]:
    """
    Принимает файлы от пользователя, сохраняет их и инициирует ETL-обработку.
    """
    # Делегируем всю сложную логику сервисному слою
    upload_statuses = await file_service.process_uploaded_files(
        files=files, uploader=current_user
    )
    return upload_statuses