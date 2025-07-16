# Путь: backend/repositories/user_repo.py

import logging
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo import IndexModel, ASCENDING
from datetime import datetime

# --- ИЗМЕНЕНИЕ: Импортируем security для хэширования паролей ---
from core import security
from schemas.user_schemas import UserInDB, UserCreateSchema

logger = logging.getLogger(__name__)

class UserRepo:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db["users"]

    async def initialize_repo(self):
        """Создает необходимые индексы и пользователей по умолчанию при старте."""
        logger.info("Initializing UserRepo: creating indexes and default users...")
        
        # 1. Создание индексов
        username_index = IndexModel([("username", ASCENDING)], name="username_unique_idx", unique=True)
        email_index = IndexModel([("email", ASCENDING)], name="email_unique_idx", unique=True)
        try:
            await self.collection.create_indexes([username_index, email_index])
            logger.info("User indexes checked/created successfully.")
        except Exception as e:
            logger.error(f"Error creating user indexes: {e}")

        # --- ИЗМЕНЕНИЕ: Логика создания пользователей по умолчанию ---
        # 2. Создание пользователя-администратора
        admin_user = await self.get_user_by_username("admin")
        if not admin_user:
            logger.info("Admin user not found, creating one.")
            admin_data = {
                "username": "admin",
                "email": "admin@example.com",
                "hashed_password": security.get_password_hash("admin"),
                "role": "admin" # Устанавливаем роль 'admin'
            }
            await self.create_user(admin_data)
            logger.info("Default admin user created successfully.")

        # 3. Создание обычного пользователя
        default_user = await self.get_user_by_username("user")
        if not default_user:
            logger.info("Default user not found, creating one.")
            user_data = {
                "username": "user",
                "email": "user@example.com",
                "hashed_password": security.get_password_hash("user"),
                "role": "user" # Роль по умолчанию
            }
            await self.create_user(user_data)
            logger.info("Default user created successfully.")

    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        user_doc = await self.collection.find_one({"username": username})
        if user_doc:
            return UserInDB(**user_doc) 
        return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        user_doc = await self.collection.find_one({"email": email})
        if user_doc:
            return UserInDB(**user_doc)
        return None

    async def create_user(self, user_data: dict) -> UserInDB:
        """Принимает словарь с данными, готовит его и сохраняет в базу."""
        try:
            db_user_data = user_data.copy()
            
            db_user_data["is_active"] = True
            # Роль теперь передается в user_data, по умолчанию будет 'user'
            if "role" not in db_user_data:
                db_user_data["role"] = "user" 
            db_user_data["created_at"] = datetime.utcnow()
            db_user_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.insert_one(db_user_data)
            
            created_user_doc = await self.collection.find_one({"_id": result.inserted_id})

            if not created_user_doc:
                raise Exception("Failed to retrieve user after creation")

            return UserInDB(**created_user_doc)
        
        except DuplicateKeyError as e:
            logger.warning(f"Attempted to create duplicate user: {e.details}")
            if 'username' in e.details.get('errmsg', ''):
                raise ValueError(f"Пользователь с именем '{db_user_data.get('username')}' уже существует.")
            if 'email' in e.details.get('errmsg', ''):
                raise ValueError(f"Пользователь с email '{db_user_data.get('email')}' уже существует.")
            raise