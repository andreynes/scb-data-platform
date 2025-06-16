# backend/app/schemas/user_schemas.py

import uuid  
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

# Базовая схема с общими полями
class UserBaseSchema(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    role: str = "user"

# Схема для создания нового пользователя (принимает пароль)
class UserCreateSchema(UserBaseSchema):
    password: str

# Схема для обновления пользователя
class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None

# Базовая схема для пользователя, как он хранится в БД (включает ID)
class UserInDBBase(UserBaseSchema):
    id: uuid.UUID  

    class Config:
        from_attributes = True

# Схема для возврата данных пользователя через API (без пароля)
class UserSchema(UserInDBBase):
    pass

# Полная схема пользователя в БД (включая хэш пароля)
class UserInDB(UserSchema):
    id: str = Field(..., alias="_id") # MongoDB использует _id
    hashed_password: str

    class Config:
        populate_by_name = True # Разрешает использовать и id, и _id