# backend/app/schemas/common_schemas.py
from typing import Optional, Dict, Any
from pydantic import BaseModel

class Msg(BaseModel):
    detail: str

class DetailMsg(BaseModel):
    detail: str

class SuccessMsg(BaseModel):
    message: str
    
# Можно добавить другие общие схемы по мере необходимости