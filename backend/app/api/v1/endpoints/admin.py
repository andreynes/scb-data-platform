# backend/app/api/v1/endpoints/admin.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

# ИСПРАВЛЕНЫ ИМПОРТЫ: убираем 'backend.'
from app.schemas.admin_schemas import (
    ReparseRequestSchema,
    ReparseResponseSchema,
)
from app.schemas.user_schemas import UserSchema
from app.schemas.verification_schemas import (
    VerificationDataSchema,
    VerificationResultSchema,
    VerificationTaskSchema,
)
from app.services.admin_service import AdminService
from app.api.v1.deps import get_admin_service, get_current_admin_user

# Теги уже были добавлены, здесь все в порядке
router = APIRouter()

# --- Эндпоинт для Ручного Репарсинга ---

@router.post(
    "/reparse",
    response_model=ReparseResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Запуск ручного репарсинга документов",
    tags=["admin", "etl"]
)
async def trigger_manual_reparse(
    request: ReparseRequestSchema,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: UserSchema = Depends(get_current_admin_user),
):
    """
    Инициирует ручной репарсинг для списка документов.
    Доступно только для пользователей с правами Администратора/Мейнтейнера.
    """
    trigger_statuses = await admin_service.trigger_manual_reparse(
        request=request, 
        triggered_by_user=current_user.username
    )
    return ReparseResponseSchema(statuses=trigger_statuses)

# --- Эндпоинты для Верификации ---

@router.get(
    "/verification/queue",
    response_model=List[VerificationTaskSchema],
    summary="Получение очереди задач на верификацию",
    tags=["admin", "verification"],
    dependencies=[Depends(get_current_admin_user)]
)
async def get_verification_queue(
    limit: int = Query(50, ge=1, le=200, description="Максимальное количество задач"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Возвращает список задач, ожидающих ручной верификации.
    """
    tasks = await admin_service.get_verification_queue(limit=limit, offset=offset)
    return tasks

@router.get(
    "/verification/{task_id}/data",
    response_model=VerificationDataSchema,
    summary="Получение данных для конкретной задачи верификации",
    tags=["admin", "verification"],
    dependencies=[Depends(get_current_admin_user)]
)
async def get_verification_task_data(
    task_id: str,
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    Возвращает данные (JSON и атомы) для указанной задачи верификации.
    """
    data = await admin_service.verification_service.get_data_for_verification(task_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification data for task ID '{task_id}' not found."
        )
    return data

@router.post(
    "/verification/submit",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отправка результата ручной верификации",
    tags=["admin", "verification"],
    dependencies=[Depends(get_current_admin_user)]
)
async def submit_verification_result(
    result: VerificationResultSchema,
    admin_service: AdminService = Depends(get_admin_service),
    current_user: UserSchema = Depends(get_current_admin_user),
):
    """
    Принимает и сохраняет результат верификации (статус и исправления).
    """
    success = await admin_service.submit_verification(
        result=result, 
        verified_by=current_user.username
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {result.document_id} not found or update failed.",
        )