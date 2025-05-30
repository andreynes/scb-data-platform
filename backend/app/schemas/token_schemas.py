# backend/app/schemas/token_schemas.py
from typing import Optional
from pydantic import BaseModel

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class TokenDataSchema(BaseModel):
    username: Optional[str] = None
    # или user_id: Optional[int] = None, или другой идентификатор