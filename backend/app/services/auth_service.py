# backend/app/services/auth_service.py
from typing import Optional
from app.core import security
from app.repositories.user_repo import UserRepo
from app.schemas.user_schemas import UserSchema, UserCreateSchema, UserInDB
from .exceptions import UserAlreadyExistsError, InvalidCredentialsError

class AuthService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        user = await self.user_repo.get_user_by_username(username=username)
        if not user or not security.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Incorrect username or password")
        return user

    async def create_user(self, user_in: UserCreateSchema) -> UserInDB:
        # Проверки на уникальность остаются теми же
        if await self.user_repo.get_user_by_username(username=user_in.username):
            raise UserAlreadyExistsError(f"User with username '{user_in.username}' already exists.")
        if await self.user_repo.get_user_by_email(email=user_in.email):
            raise UserAlreadyExistsError(f"User with email '{user_in.email}' already exists.")

        hashed_password = security.get_password_hash(user_in.password)
        
        # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
        # Создаем простой словарь, а не Pydantic-модель
        user_data_to_create = user_in.model_dump()
        user_data_to_create["hashed_password"] = hashed_password
        
        try:
            created_user = await self.user_repo.create_user(user_data=user_data_to_create)
            return created_user
        except ValueError as e:
            raise UserAlreadyExistsError(str(e))

    def create_access_token_for_user(self, user: UserInDB) -> str:
        #
        # ИСПРАВЛЕННЫЙ ВЫЗОВ
        # Мы передаем username пользователя как 'subject' для токена
        #
        access_token = security.create_jwt_token(subject=user.username)
        return access_token