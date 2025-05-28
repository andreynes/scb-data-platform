# backend/app/schemas/user_schemas.py
from typing import Optional
from pydantic import BaseModel, EmailStr

# Общие поля для пользователя, которые можно использовать в других схемах
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: Optional[str] = "user" # Пример роли по умолчанию

# Схема для создания нового пользователя (например, при регистрации)
# Пароль здесь в открытом виде, так как он будет хэшироваться перед сохранением в БД
class UserCreate(UserBase):
    username: str
    email: EmailStr
    password: str

# Схема для обновления пользователя (поля опциональны)
class UserUpdate(UserBase):
    password: Optional[str] = None # Если разрешено обновление пароля через этот эндпоинт

# Базовая схема для пользователя, как он хранится в БД (включая ID)
class UserInDBBase(UserBase):
    id: Optional[int] = None # Или str/UUID, в зависимости от вашей БД

    class Config:
        # orm_mode = True # Для Pydantic v1
        from_attributes = True # Для Pydantic v2, если модель создается из ORM объекта

# Схема для пользователя, как он хранится в БД, включая хэш пароля
# Эта схема обычно не возвращается через API напрямую
class UserInDB(UserInDBBase):
    hashed_password: str

# Схема для пользователя, возвращаемая через API (без пароля)
class UserSchema(UserInDBBase):
    pass