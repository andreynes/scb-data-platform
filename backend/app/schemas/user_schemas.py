# Путь: backend/app/schemas/user_schemas.py

import uuid
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

# ---- Вспомогательный тип для ObjectId ----
# Это позволяет Pydantic работать с ObjectId и правильно его валидировать.
# Мы создаем псевдоним PyObjectId, чтобы Pydantic понимал, как с ним обращаться.
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.is_instance_schema(ObjectId),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

# --- Основные схемы ---

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
    # Используем Field с псевдонимом '_id' для поля 'id'.
    # Тип PyObjectId гарантирует правильную обработку данных из MongoDB.
    id: PyObjectId = Field(alias="_id", default_factory=PyObjectId)
    
    class Config:
        from_attributes = True
        populate_by_name = True # Позволяет инициализировать по полю 'id' или '_id'
        arbitrary_types_allowed = True # Разрешает типы, которые Pydantic не знает, как ObjectId
        json_encoders = {ObjectId: str} # Говорит, как превращать ObjectId в JSON

# Схема для возврата данных пользователя через API (без пароля)
# Эта схема будет автоматически преобразовывать ObjectId в строку благодаря json_encoders.
class UserSchema(UserInDBBase):
    pass

# Полная схема пользователя в БД (включая хэш пароля)
# Эта схема используется внутри приложения и работает с реальным ObjectId.
class UserInDB(UserInDBBase):
    hashed_password: str