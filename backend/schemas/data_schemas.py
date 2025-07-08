# Файл: backend/app/schemas/data_schemas.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import date
import uuid

# --- Схемы для параметров запроса ---

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

# Схема для тела запроса /data/query
class DataQuerySchema(BaseModel):
    # -> ИЗМЕНЕНО: Поле стало обязательным. Убираем Optional и значение по умолчанию.
    document_id: str 
    filters: Optional[List[FilterCondition]] = []
    aggregations: Optional[List[AggregationRule]] = []
    columns: Optional[List[str]] = []
    sort: Optional[List[SortRule]] = []
    pagination: Optional[PaginationParams] = None

# --- Схемы для ответов API ---

# Используем extra = 'allow' для гибкости, чтобы новые поля в онтологии не ломали схему.
class AtomicDataRow(BaseModel):
    original_document_id: str
    ontology_version: str
    
    class Config:
        extra = 'allow'

class PaginationInfo(BaseModel):
    currentPage: int
    pageSize: int
    totalItems: int
    totalPages: int

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