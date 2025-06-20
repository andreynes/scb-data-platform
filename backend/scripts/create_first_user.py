import os
import sys
from getpass import getpass
from pymongo import MongoClient
from passlib.context import CryptContext

# --- Конфигурация ---
# Обычно эти данные берутся из переменных окружения, но для простоты скрипта зададим их здесь.
# Убедитесь, что они соответствуют вашим настройкам в .env файле для docker-compose.
MONGO_URL = os.getenv("MONGO_DB_URL", "mongodb://root:example@localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "scb_db")
USERS_COLLECTION = "users"

# Контекст для хэширования паролей, должен быть таким же, как в backend/app/core/security.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Хэширует пароль."""
    return pwd_context.hash(password)

def create_user(db, username, email, password, role):
    """Создает пользователя в базе данных."""
    user_collection = db[USERS_COLLECTION]
    
    # Проверяем, не существует ли уже пользователь с таким email или username
    if user_collection.find_one({"email": email}):
        print(f"Ошибка: Пользователь с email '{email}' уже существует.")
        return
    if user_collection.find_one({"username": username}):
        print(f"Ошибка: Пользователь с именем '{username}' уже существует.")
        return

    # Создаем документ пользователя
    user_doc = {
        "username": username,
        "email": email,
        "hashed_password": get_password_hash(password),
        "is_active": True,
        "role": role, # 'maintainer' или 'admin' для прав доступа
    }
    
    # Вставляем документ в коллекцию
    result = user_collection.insert_one(user_doc)
    print(f"Пользователь '{username}' успешно создан с ID: {result.inserted_id}")

if __name__ == "__main__":
    print("--- Скрипт создания первого пользователя ---")
    
    # Запрашиваем данные у администратора
    admin_username = input("Введите имя пользователя (username) для нового администратора: ")
    admin_email = input(f"Введите email для пользователя '{admin_username}': ")
    admin_password = getpass("Введите пароль для нового администратора: ")
    admin_password_confirm = getpass("Подтвердите пароль: ")

    if admin_password != admin_password_confirm:
        print("Ошибка: Пароли не совпадают.")
        sys.exit(1)

    if not all([admin_username, admin_email, admin_password]):
        print("Ошибка: Все поля должны быть заполнены.")
        sys.exit(1)
        
    try:
        # Подключаемся к MongoDB
        print(f"\nПодключение к MongoDB по адресу: {MONGO_URL}...")
        client = MongoClient(MONGO_URL)
        db = client[MONGO_DB_NAME]
        
        # Проверяем соединение
        db.command('ping')
        print("Соединение с MongoDB установлено.")
        
        # Создаем пользователя
        # Роль 'maintainer' соответствует ТЗ для административных задач
        create_user(db, admin_username, admin_email, admin_password, role="maintainer")
        
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        print("Убедитесь, что Docker контейнеры (особенно MongoDB) запущены и переменные окружения верны.")
    finally:
        if 'client' in locals():
            client.close()
            print("Соединение с MongoDB закрыто.")