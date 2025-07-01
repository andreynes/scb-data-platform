# backend/app/services/auth_service.py

from typing import Optional
from core import security
from repositories.user_repo import UserRepo
from schemas.user_schemas import UserSchema, UserCreateSchema, UserInDB
from .exceptions import UserAlreadyExistsError 

class AuthService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """
        Аутентифицирует пользователя.
        Возвращает объект пользователя при успехе или None при неудаче.
        """
        # --- ДОБАВЛЕНЫ ОТЛАДОЧНЫЕ ВЫВОДЫ ---
        print("--- AUTHENTICATION ATTEMPT ---")
        print(f"--> Received username: '{username}'")
        print(f"--> Received password: '{password}'")
        
        user = await self.user_repo.get_user_by_username(username=username)
        
        if not user:
            print(f"[!] User '{username}' NOT FOUND in the database.")
            print("---------------------------------")
            return None
            
        print(f"[+] User '{username}' FOUND.")
        print(f"    Hashed password from DB is: {user.hashed_password}")
        
        is_password_correct = security.verify_password(password, user.hashed_password)
        
        if not is_password_correct:
            print(f"[!] Password verification FAILED for user '{username}'.")
            print("---------------------------------")
            return None
        
        print(f"[+] Password verification SUCCESSFUL for user '{username}'.")
        print("---------------------------------")
        return user

    async def create_user(self, user_in: UserCreateSchema) -> UserInDB:
        if await self.user_repo.get_user_by_username(username=user_in.username):
            raise UserAlreadyExistsError(f"User with username '{user_in.username}' already exists.")
        
        if hasattr(user_in, 'email') and user_in.email:
            if await self.user_repo.get_user_by_email(email=user_in.email):
                raise UserAlreadyExistsError(f"User with email '{user_in.email}' already exists.")

        hashed_password = security.get_password_hash(user_in.password)
        
        user_data_to_create = user_in.model_dump()
        # Убедимся, что мы не пытаемся записать пароль дважды, если он есть в схеме
        user_data_to_create.pop("password", None) 
        user_data_to_create["hashed_password"] = hashed_password
        
        created_user = await self.user_repo.create_user(user_data=user_data_to_create)
        return created_user

    def create_access_token_for_user(self, user: UserInDB) -> str:
        access_token = security.create_jwt_token(subject=user.username)
        return access_token