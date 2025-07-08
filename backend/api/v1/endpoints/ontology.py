# backend/app/api/v1/endpoints/ontology.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from services.ontology_service import OntologyService 
from schemas.ontology_schemas import OntologySchema
from api.v1.deps import get_ontology_service

# УБИРАЕМ `tags` ОТСЮДА
router = APIRouter()

@router.get(
    "/schema",
    response_model=OntologySchema,
    summary="Получить текущую активную схему онтологии",
    description="Возвращает полную структуру текущей активной версии онтологии, "
                "включая атрибуты, их типы, описания и иерархии.",
    # УБИРАЕМ `tags=["ontology"]` И ОТСЮДА
    responses={
        404: {"description": "Активная схема онтологии не найдена"},
        500: {"description": "Внутренняя ошибка сервера"},
    }
)
async def get_current_ontology_schema(
    ontology_service: OntologyService = Depends(get_ontology_service)
) -> OntologySchema:
    schema = await ontology_service.get_current_ontology_schema()
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active ontology schema not found",
        )
    return schema