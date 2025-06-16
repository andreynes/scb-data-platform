# backend/app/repositories/user_repo.py
import logging
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo import IndexModel, ASCENDING
import uuid
from datetime import datetime

from app.schemas.user_schemas import UserInDB, UserCreateSchema

logger = logging.getLogger(__name__)

class UserRepo:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db["users"]

    async def initialize_repo(self):
        """Создает необходимые индексы при старте."""
        logger.info("Initializing UserRepo: creating indexes...")
        # Уникальный индекс по username и email, чтобы база сама следила за уникальностью
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
            # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
            # Дополняем словарь полями по умолчанию
            db_user_data = user_data.copy()
            db_user_data["_id"] = str(uuid.uuid4()) # Генерируем уникальный ID
            db_user_data["is_active"] = True
            db_user_data["role"] = "user"
            db_user_data["created_at"] = datetime.utcnow()
            db_user_data["updated_at"] = datetime.utcnow()

            # Создаем объект UserInDB для валидации ПЕРЕД вставкой в базу
            user_to_insert = UserInDB(**db_user_data)
            
            # Вставляем в базу словарь, а не Pydantic-модель
            await self.collection.insert_one(user_to_insert.model_dump(by_alias=True))
            
            # Возвращаем созданный объект Pydantic
            return user_to_insert
        except DuplicateKeyError as e:
            logger.warning(f"Attempted to create duplicate user: {e.details}")
            if 'username' in e.details['errmsg']:
                raise ValueError("A user with this username already exists.")
            if 'email' in e.details['errmsg']:
                raise ValueError("A user with this email already exists.")
            raise