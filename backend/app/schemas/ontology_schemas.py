# backend/app/schemas/ontology_schemas.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class OntologyAttribute(BaseModel):
    name: str
    type: str
    description: str
    role: str  # e.g., "dimension", "measure", "metadata"
    vocabulary: Optional[str] = None
    # Можно добавить другие поля по мере необходимости, например:
    # is_nullable: bool = True
    # example_values: Optional[List[Any]] = None

class OntologySchema(BaseModel):
    version: str
    description: Optional[str] = None
    attributes: List[OntologyAttribute]
    hierarchies: Optional[Dict[str, List[str]]] = None # e.g., {"time": ["year", "quarter", "month"]}
    # Можно добавить другие поля, например, validation_rules

    class Config:
        from_attributes = True # Для Pydantic v2 (замена orm_mode)
        # orm_mode = True # Для Pydantic v1