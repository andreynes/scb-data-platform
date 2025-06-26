# backend/app/schemas/data_schemas.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import date
import uuid

# --- Это просто примеры, их можно будет удалить или доработать ---
class FilterCondition(BaseModel):
    field: str
    operator: str
    value: Any

class AggregationRule(BaseModel):
    field: str
    function: Optional[str] = None

class SortRule(BaseModel):
    field: str
    direction: str = 'asc'

class PaginationParams(BaseModel):
    page: int = 1
    pageSize: int = 50

# --- > ВАЖНОЕ ИЗМЕНЕНИЕ ЗДЕСЬ < ---
# Упрощаем AtomicDataRow, чтобы избежать ошибок при динамическом создании
# Теперь это просто словарь, который принимает любые ключи
class AtomicDataRow(BaseModel):
    original_document_id: str
    ontology_version: str
    
    class Config:
        extra = 'allow' # Разрешаем любые другие поля

class PaginationInfo(BaseModel):
    currentPage: int
    pageSize: int
    totalItems: int
    totalPages: int

# Схема для тела запроса /data/query
class DataQuerySchema(BaseModel):
    document_id: Optional[str] = None
    filters: Optional[List[FilterCondition]] = []
    aggregations: Optional[List[AggregationRule]] = []
    columns: Optional[List[str]] = []
    sort: Optional[List[SortRule]] = []
    pagination: Optional[PaginationParams] = None

# Схема для ответа API /data/query
class DataQueryResponseSchema(BaseModel):
    data: List[AtomicDataRow]
    pagination: Optional[PaginationInfo] = None

class ExportFormat(str, Enum):
    EXCEL = "excel"
    CSV = "csv"

class ExportResponseSchema(BaseModel):
    task_id: str
    message: str