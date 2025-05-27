# backend/app/api/v1/endpoints/ontology.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from backend.app.services.ontology_service import OntologyService
from backend.app.schemas.ontology_schemas import OntologySchema
from backend.app.api.v1.deps import get_ontology_service
# Если эндпоинт будет защищен, раскомментируйте:
# from backend.app.api.v1.deps import get_current_admin_user (или get_current_active_user)
# from backend.app.schemas.user_schemas import UserSchema

router = APIRouter()

@router.get(
    "/schema",
    response_model=OntologySchema,
    summary="Получить текущую активную схему онтологии",
    description="Возвращает полную структуру текущей активной версии онтологии, "
                "включая атрибуты, их типы, описания и иерархии.",
    tags=["ontology"], # Для группировки в Swagger UI
    responses={
        404: {"description": "Активная схема онтологии не найдена"},
        500: {"description": "Внутренняя ошибка сервера"},
        # 401: {"description": "Не аутентифицирован"}, # Если будет get_current_active_user
        # 403: {"description": "Недостаточно прав"},    # Если будет get_current_admin_user
    }
)
async def get_current_ontology_schema(
    ontology_service: OntologyService = Depends(get_ontology_service)
    # Если эндпоинт защищен, добавьте зависимость пользователя:
    # current_user: UserSchema = Depends(get_current_admin_user) # или get_current_active_user
) -> OntologySchema:
    """
    Эндпоинт для получения текущей активной схемы онтологии.
    """
    schema = await ontology_service.get_current_ontology_schema()
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active ontology schema not found",
        )
    return schema

# В будущем здесь могут быть эндпоинты для /ontology/vocabularies и т.д.