# backend/app/schemas/user_schemas.py
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
import uuid

# Базовая схема с общими полями
class UserBaseSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None

# Схема для создания пользователя (принимается API)
class UserCreateSchema(UserBaseSchema):
    password: str = Field(..., min_length=8)

# Схема для пользователя, хранящегося в БД (включая хэш пароля)
# ЭТО И ЕСТЬ UserInDB или его база
class UserInDBBase(UserBaseSchema):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    hashed_password: str
    is_active: bool = True
    role: str = "user"

    class Config:
        from_attributes = True 

# Если ваш репозиторий ожидает именно UserInDB, вы можете сделать так:
class UserInDB(UserInDBBase): # <<<--- ДОБАВЬТЕ ЭТОТ КЛАСС, ЕСЛИ ОН ИСПОЛЬЗУЕТСЯ ПО ИМЕНИ
    pass

# Схема для пользователя, возвращаемая API (без пароля)
class UserSchema(UserBaseSchema):
    id: uuid.UUID
    is_active: bool
    role: str

    class Config:
        from_attributes = True