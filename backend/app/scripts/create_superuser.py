# backend/app/scripts/create_superuser.py

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from repositories.user_repo import UserRepo
from schemas.user_schemas import UserCreateSchema
from core.security import get_password_hash

async def create_superuser():
    """
    Создает суперпользователя в базе данных, если он еще не существует.
    """
    print("Connecting to MongoDB to create a superuser...")
    
    client = None  # Инициализируем клиент, чтобы он был доступен в finally
    try:
        # Создаем подключение к БД
        client = AsyncIOMotorClient(settings.MONGO_DB_URL)
        db = client[settings.MONGO_DB_NAME]
        
        # Используем репозиторий для работы с пользователями
        user_repo = UserRepo(db)
        
        # Проверяем, существует ли уже пользователь с таким именем
        admin_username = "admin"
        existing_user = await user_repo.get_user_by_username(admin_username)
        
        if existing_user:
            print(f"User '{admin_username}' already exists. Exiting.")
            return

        # Определяем данные для нового суперпользователя
        # ВНИМАНИЕ: Установите пароль, который вы будете использовать для входа!
        new_password = "password" 
        superuser_in = UserCreateSchema(
            username=admin_username,
            password=new_password,
            email="admin@example.com",
            is_superuser=True,
            # Можно добавить email и другие поля при необходимости
            # email="admin@example.com",
        )
        
        # Хешируем пароль перед сохранением
        hashed_password = get_password_hash(superuser_in.password)
        
        # Подготавливаем данные для записи в БД
        user_to_create = superuser_in.model_dump()
        user_to_create['hashed_password'] = hashed_password
        del user_to_create['password']  # Удаляем пароль в открытом виде
        
        # Используем коллекцию 'users' для вставки документа
        await db.users.insert_one(user_to_create)
        
        print(f"Superuser '{admin_username}' created successfully!")

    except Exception as e:
        print(f"\nAN ERROR OCCURRED: {e}\n")
    
    finally:
        # Гарантированно закрываем соединение
        if client:
            client.close()
            print("MongoDB connection closed.")


# Этот блок позволяет запускать скрипт напрямую из командной строки
if __name__ == "__main__":
    print("Running script to create superuser...")
    asyncio.run(create_superuser())
    print("Script finished.")