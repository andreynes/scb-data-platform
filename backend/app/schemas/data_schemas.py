# backend/app/schemas/data_schemas.py
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal # Используем Decimal для точности финансовых данных, если нужно

# Схема для представления одной "атомарной" строки данных из СКЛАДА.
# Основано на ТЗ, Глава 6.2 "Ключевые атрибуты (Измерения), планируемые для MVP".
class AtomicDataRow(BaseModel):
    # Измерения из ТЗ
    indicator_name: str
    periodicity: str
    date_start: date
    date_end: date
    year: Optional[int] = None
    quarter: Optional[int] = None # Например, 1-4
    month: Optional[int] = None # Например, 1-12
    day: Optional[int] = None # Например, 1-31
    geo_country: str
    geo_region_rf: Optional[str] = None # Регион РФ, если применимо
    unit: str # Единица измерения
    adjustment: Optional[str] = None # Тип корректировки
    value_type: Optional[str] = None # Тип значения (факт, прогноз, оценка)

    # Метаданные, связанные с обработкой и происхождением
    source: str # Источник данных (Rosstat, CBR, etc.)
    original_document_id: str # ID исходного документа в ОЗЕРЕ (MongoDB)
    load_timestamp: datetime # Дата и время загрузки/обновления записи в СКЛАД
    ontology_version: str # Версия Онтологии, по которой была создана/обновлена запись

    # Поля, связанные с верификацией (могут быть Optional, если не для всех записей)
    verification_status: Optional[str] = None # Статус верификации
    probability: Optional[float] = None # Рассчитанная вероятность корректности

    # Основное значение показателя
    value: Optional[Decimal] = None # Используем Decimal для точности, можно float если точность не критична

    class Config:
        orm_mode = True
        # extra = "allow" # Если Онтология v1.0 строго фиксирована для MVP, можно не использовать.
                         # Позволяет Pydantic принимать и хранить поля, не описанные в схеме,
                         # что может быть полезно при эволюции онтологии, но для MVP лучше строгость.

# Схема для информации о пагинации (если будет реализовываться)
# В ТЗ указано: "для MVP пагинацию можно опустить", но для DataQueryResponseSchema она Optional.
class PaginationInfo(BaseModel):
    current_page: int
    page_size: int
    total_items: int
    total_pages: int

# Схема для тела POST-запроса на /data/query
# В ТЗ указано: "Поля для MVP: document_id: str (чтобы запросить все атомы для конкретного исходного файла)."
class DataQuerySchema(BaseModel):
    document_id: str

# Схема для ответа API /data/query
class DataQueryResponseSchema(BaseModel):
    data: List[AtomicDataRow]
    pagination: Optional[PaginationInfo] = None # Пагинация опциональна для MVP