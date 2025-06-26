# backend/app/schemas/verification_schemas.py

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

# Эта схема остается без изменений
class VerificationTaskSchema(BaseModel):
    """Схема для одной задачи в очереди на верификацию."""
    document_id: str
    filename: str
    source: str
    upload_timestamp: datetime
    reason_for_verification: str
    priority_score: Optional[float] = None

# Эта схема остается без изменений
class VerificationDataSchema(BaseModel):
    """Схема для данных, отображаемых в интерфейсе верификатора."""
    document_id: str
    json_representation: Optional[Dict[str, Any]] = None
    atomic_data: Optional[List[Dict[str, Any]]] = None

# Этот enum остается без изменений
class VerificationStatusEnum(str, Enum):
    """Допустимые финальные статусы верификации."""
    VERIFIED = "Verified"
    NEEDS_FIXING = "NeedsFixing"

# <<< НАЧАЛО ИЗМЕНЕНИЙ >>>

# 1. Определяем детальную схему для одного исправления
class CorrectionInfo(BaseModel):
    """Схема для одного конкретного исправления, сделанного Мейнтейнером."""
    atom_id: str = Field(..., description="Уникальный ID атома (строки) в СКЛАДЕ, который исправляется.")
    field_name: str = Field(..., description="Техническое имя атрибута (колонки), который исправляется.")
    new_value: Any = Field(..., description="Новое значение для ячейки.")
    
    # Опциональные поля для более сложных исправлений в будущем
    new_attribute_name: Optional[str] = Field(None, description="Если Мейнтейнер изменил сопоставление с атрибутом онтологии.")
    is_not_applicable: Optional[bool] = Field(False, description="Если значение помечено как NULL_NOT_APPLICABLE.")
    original_value: Optional[Any] = Field(None, description="Исходное значение (для логирования).")

# 2. Обновляем схему результата, чтобы она включала список исправлений
class VerificationResultSchema(BaseModel):
    """Схема для отправки результата верификации на бэкенд."""
    document_id: str
    final_status: VerificationStatusEnum
    # Теперь это поле обязательно и является списком
    corrections: List[CorrectionInfo] = Field(..., description="Список внесенных исправлений.")

# <<< КОНЕЦ ИЗМЕНЕНИЙ >>>