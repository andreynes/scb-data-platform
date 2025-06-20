# Путь: backend/app/repositories/user_repo.py

import logging
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo import IndexModel, ASCENDING
from datetime import datetime
from bson import ObjectId # <-- ВАЖНЫЙ ИМПОРТ

from app.schemas.user_schemas import UserInDB, UserCreateSchema

logger = logging.getLogger(__name__)

class UserRepo:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db["users"]

    async def initialize_repo(self):
        """Создает необходимые индексы при старте."""
        logger.info("Initializing UserRepo: creating indexes...")
        username_index = IndexModel([("username", ASCENDING)], name="username_unique_idx", unique=True)
        email_index = IndexModel([("email", ASCENDING)], name="email_unique_idx", unique=True)
        try:
            await self.collection.create_indexes([username_index, email_index])
            logger.info("User indexes created successfully.")
        except Exception as e:
            logger.error(f"Error creating user indexes: {e}")

    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        user_doc = await self.collection.find_one({"username": username})
        if user_doc:
            # Pydantic теперь корректно обработает _id типа ObjectId
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
            
            # --- ГЛАВНОЕ ИЗМЕНЕНИЕ ЗДЕСЬ ---
            # MongoDB сам сгенерирует уникальный ObjectId для поля _id,
            # если мы его не передадим. Это лучшая практика.
            # Мы больше не генерируем ID вручную.
            
            db_user_data["is_active"] = True
            db_user_data["role"] = "user"
            db_user_data["created_at"] = datetime.utcnow()
            db_user_data["updated_at"] = datetime.utcnow()
            
            # Вставляем данные в базу
            result = await self.collection.insert_one(db_user_data)
            
            # Теперь получаем только что созданного пользователя из БД,
            # чтобы убедиться, что все поля (включая _id) на месте.
            created_user_doc = await self.collection.find_one({"_id": result.inserted_id})

            if not created_user_doc:
                # Это маловероятно, но лучше обработать
                raise Exception("Failed to retrieve user after creation")

            return UserInDB(**created_user_doc)
        
        except DuplicateKeyError as e:
            logger.warning(f"Attempted to create duplicate user: {e.details}")
            # Возбуждаем кастомные ошибки, чтобы сервисный слой мог их поймать
            if 'username' in e.details.get('errmsg', ''):
                raise ValueError(f"Пользователь с именем '{db_user_data['username']}' уже существует.")
            if 'email' in e.details.get('errmsg', ''):
                raise ValueError(f"Пользователь с email '{db_user_data['email']}' уже существует.")
            raise