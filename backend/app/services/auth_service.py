# backend/app/services/auth_service.py

from typing import Optional
from app.core import security
from app.repositories.user_repo import UserRepo
# --- > ИЗМЕНЕННЫЙ ИМПОРТ < ---
from app.schemas.user_schemas import UserSchema, UserCreateSchema, UserInDB
from .exceptions import UserAlreadyExistsError, InvalidCredentialsError

class AuthService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def authenticate_user(self, username: str, password: str) -> Optional[UserSchema]:
        user = await self.user_repo.get_user_by_username(username=username)
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return UserSchema.from_orm(user)

    async def create_user(self, user_in: UserCreateSchema) -> UserSchema:
        existing_user = await self.user_repo.get_user_by_username(username=user_in.username)
        if existing_user:
            raise UserAlreadyExistsError("Username already registered")
        
        hashed_password = security.get_password_hash(user_in.password)
        
        # Убираем пароль из данных перед передачей в репозиторий
        user_create_data = user_in.model_dump(exclude={"password"})
        
        created_user = await self.user_repo.create_user(
            user_data=user_create_data, hashed_password=hashed_password
        )
        return UserSchema.from_orm(created_user)

    def create_access_token(self, data: dict) -> str:
        return security.create_jwt_token(data=data)