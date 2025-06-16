# backend/app/repositories/user_repo.py
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import InsertOneResult # Для примера

# Предполагаем, что у вас есть схема UserInDB для данных из БД
from app.schemas.user_schemas import UserInDB, UserCreateSchema

class UserRepo:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        # Название коллекции пользователей, лучше вынести в настройки или константы
        self.collection_name = "users" 
        self.collection = self.db[self.collection_name]

    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        # Заглушка, реальная логика будет позже
        # user_doc = await self.collection.find_one({"username": username})
        # if user_doc:
        #     return UserInDB(**user_doc)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        # Заглушка
        return None
    
    async def create_user(self, user_in: UserCreateSchema, hashed_password: str) -> UserInDB:
        # Заглушка
        # db_user = UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
        # inserted_result: InsertOneResult = await self.collection.insert_one(db_user.model_dump(by_alias=True))
        # created_user = await self.get_user_by_id(str(inserted_result.inserted_id))
        # if not created_user:
        #     raise Exception("User not created") # Пример обработки ошибки
        # return created_user
        # Пока что вернем заглушку, чтобы удовлетворить типизацию, если UserInDB имеет поля
        # Это нужно будет доработать, когда будет реальная логика
        fake_user_data = user_in.model_dump()
        fake_user_data['id'] = "fake_id" # UserInDB обычно ожидает id
        fake_user_data['is_active'] = True # UserInDB обычно ожидает is_active
        fake_user_data['role'] = "user" # UserInDB обычно ожидает role
        fake_user_data['hashed_password'] = hashed_password
        return UserInDB(**fake_user_data)

    def get_user_by_username_sync(self, username: str) -> Optional[UserInDB]:
        import asyncio
        return asyncio.run(self.get_user_by_username(username))

    def update_user_sync(self, user_id: str, data: dict) -> bool:
        import asyncio
        return asyncio.run(self.update_user(user_id, data))

    def create_user_sync(self, user_in: UserCreateSchema, hashed_password: str) -> Optional[UserInDB]:
        import asyncio
        return asyncio.run(self.create_user(user_in, hashed_password))


    # Другие методы CRUD по необходимости (update_user, delete_user)