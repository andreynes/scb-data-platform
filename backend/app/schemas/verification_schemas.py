# backend/app/schemas/verification_schemas.py
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

# --- Read-Only Схемы для Этапа 4.3 ---

class VerificationTaskSchema(BaseModel):
    """Схема для одной задачи в очереди на верификацию."""
    document_id: str
    filename: str
    source: str
    upload_timestamp: datetime
    reason_for_verification: str
    priority_score: Optional[float] = None

class VerificationDataSchema(BaseModel):
    """Схема для данных, отображаемых в интерфейсе верификатора."""
    document_id: str
    json_representation: Optional[Dict[str, Any]] = None
    atomic_data: Optional[List[Dict[str, Any]]] = None

class VerificationStatusEnum(str, Enum):
    """Допустимые финальные статусы верификации."""
    VERIFIED = "Verified"
    NEEDS_FIXING = "NeedsFixing"

class VerificationResultSchema(BaseModel):
    """Схема для отправки результата верификации на бэкенд."""
    document_id: str
    final_status: VerificationStatusEnum
    # На этом этапе исправления не отправляются
    # corrections: List[CorrectionInfo] = [] 

# Модель для исправлений, понадобится на Этапе 5
# class CorrectionInfo(BaseModel):
#     atom_id: str
#     field_name: str
#     new_value: Any