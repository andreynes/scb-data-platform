# backend/app/schemas/file_schemas.py
from typing import Optional
from pydantic import BaseModel, Field
import uuid # Для генерации document_id по умолчанию, если это будет происходить в схеме

class FileUploadStatusSchema(BaseModel):
    """
    Схема для статуса загрузки одного файла.
    Возвращается API как часть списка после запроса на загрузку файлов.
    """
    filename: str = Field(..., description="Имя загруженного файла")
    document_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), # Генерируем UUID, если ID не присвоен раньше
        description="Уникальный ID, присвоенный документу в системе (ОЗЕРЕ)"
    )
    status: str = Field(
        ..., 
        description="Начальный статус обработки файла (например, 'Accepted', 'Processing', 'Error')"
    )
    error_message: Optional[str] = Field(
        default=None, 
        description="Сообщение об ошибке, если что-то пошло не так на этапе приема файла"
    )

    class Config:
        # orm_mode = True # Для Pydantic v1, если создается из ORM-объекта
        from_attributes = True # Для Pydantic v2, если создается из ORM-объекта
                               # (здесь маловероятно, но полезно для консистентности)
        # Пример использования в коде:
        # return [FileUploadStatusSchema(filename="report.xlsx", document_id="xyz", status="Accepted")]