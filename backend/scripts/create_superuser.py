import asyncio
import os
import sys

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from repositories.user_repo import UserRepo
from core.security import get_password_hash

async def create_superuser():
    print("Connecting to MongoDB to create/update a superuser...")
    
    client = AsyncIOMotorClient(settings.MONGO_DB_URL)
    db = client[settings.MONGO_DB_NAME]
    
    user_repo = UserRepo(db)
    
    # Устанавливаем пароль, который вы хотите использовать
    new_password = "password"  # <-- ИЗМЕНИТЕ ЭТОТ ПАРОЛЬ, ЕСЛИ НУЖНО
    
    # Хешируем новый пароль
    hashed_password = get_password_hash(new_password)

    # Проверяем, существует ли уже пользователь
    existing_user = await user_repo.get_user_by_username("admin")
    if existing_user:
        print("User 'admin' already exists. Updating password.")
        # Обновляем пароль в базе данных
        await db.users.update_one(
            {"username": "admin"},
            {"$set": {"hashed_password": hashed_password}}
        )
        print(f"Password for superuser 'admin' has been updated successfully!")
    else:
        print("User 'admin' not found. Creating a new one.")
        # Создаем словарь с правильными полями для базы данных
        user_to_create = {
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": hashed_password,
            "is_superuser": True,
            "is_active": True
        }
        # Вставляем нового пользователя
        await db.users.insert_one(user_to_create)
        print("Superuser 'admin' created successfully!")

    client.close()

if __name__ == "__main__":
    asyncio.run(create_superuser())