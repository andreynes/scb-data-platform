# backend/app/services/auth_service.py
from typing import Optional
from fastapi import HTTPException, status
from datetime import timedelta

from app.repositories.user_repo import UserRepo
from app.schemas.user_schemas import UserCreateSchema, UserSchema, UserInDBBase
from app.core.security import get_password_hash, verify_password, create_jwt_token
from app.core.config import settings
from app.services.exceptions import UserAlreadyExistsError, InvalidCredentialsError # Эти исключения нужно будет создать

class AuthService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDBBase]:
        """
        Аутентифицирует пользователя.
        Возвращает пользователя, если аутентификация успешна, иначе None или выбрасывает исключение.
        """
        user = await self.user_repo.get_user_by_username(username=username)
        if not user:
            # logger.warning(f"Аутентификация не удалась: пользователь {username} не найден.")
            raise InvalidCredentialsError("Неверное имя пользователя или пароль")
        
        if not verify_password(password, user.hashed_password):
            # logger.warning(f"Аутентификация не удалась: неверный пароль для пользователя {username}.")
            raise InvalidCredentialsError("Неверное имя пользователя или пароль")
        
        return user

    async def create_user(self, user_in: UserCreateSchema) -> UserInDBBase:
        """
        Создает нового пользователя.
        """
        existing_user_by_username = await self.user_repo.get_user_by_username(username=user_in.username)
        if existing_user_by_username:
            raise UserAlreadyExistsError(f"Пользователь с именем '{user_in.username}' уже существует.")
        
        existing_user_by_email = await self.user_repo.get_user_by_email(email=user_in.email)
        if existing_user_by_email:
            raise UserAlreadyExistsError(f"Пользователь с email '{user_in.email}' уже существует.")

        hashed_password = get_password_hash(user_in.password)
        # В MVP роль может быть фиксированной
        user_db_in = UserInDBBase(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            is_active=True, # По умолчанию активен
            role="user" # По умолчанию роль 'user'
        )
        created_user = await self.user_repo.create_user(user_in=user_db_in)
        return created_user

    def create_access_token_for_user(self, user: UserInDBBase, expires_delta: Optional[timedelta] = None) -> str:
        """
        Создает JWT токен для пользователя.
        """
        # Идентификатор пользователя (например, username или user.id) будет в 'sub' токене
        return create_jwt_token(subject=user.username, expires_delta=expires_delta)

# Вам также нужно будет создать файл для кастомных исключений, например:
# backend/app/services/exceptions.py
# class UserAlreadyExistsError(Exception):
#     pass
# class InvalidCredentialsError(Exception):
#     pass