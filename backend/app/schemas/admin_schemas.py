# backend/app/schemas/admin_schemas.py
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class ReparseRequestSchema(BaseModel):
    document_ids: List[str] = Field(..., min_length=1, description="Список ID документов для репарсинга")
    ontology_version: Optional[str] = Field(None, description="Версия онтологии для репарсинга (если не указана - активная)")

class ReparseResponseSchema(BaseModel):
    statuses: Dict[str, str] = Field(..., description="Словарь со статусами запуска репарсинга для каждого документа")