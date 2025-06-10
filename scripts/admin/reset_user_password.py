import argparse
import sys
from pymongo import MongoClient
from passlib.context import CryptContext

# --- Важная настройка для запуска скрипта из корня проекта ---
# Добавляем путь к папке backend/app, чтобы можно было импортировать
# модули приложения, такие как config и user_repo.
# Это позволяет запускать скрипт из любой директории, если корень проекта в sys.path
sys.path.insert(0, './backend')
# -------------------------------------------------------------

from app.repositories.user_repo import UserRepo
from app.schemas.user_schemas import UserCreateSchema
from app.core.config import settings

# Используем тот же контекст пароля, что и в основном приложении
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Генерирует хэш для пароля."""
    return pwd_context.hash(password)

def reset_or_create_user(
    db: MongoClient, 
    username: str, 
    password: str
):
    """Находит пользователя и обновляет его пароль, или создает нового, если не найден."""
    user_repository = UserRepo(db)
    
    print(f"Ищем пользователя '{username}'...")
    user = user_repository.get_user_by_username_sync(username) # Используем синхронную версию для скрипта

    hashed_password = get_password_hash(password)

    if user:
        print(f"Пользователь '{username}' найден. Обновляем пароль...")
        update_data = {"hashed_password": hashed_password}
        updated = user_repository.update_user_sync(user.id, update_data)
        if updated:
            print(f"Пароль для пользователя '{username}' успешно обновлен.")
        else:
            print(f"ОШИБКА: Не удалось обновить пароль для пользователя '{username}'.")
    else:
        print(f"Пользователь '{username}' не найден. Создаем нового пользователя...")
        user_in = UserCreateSchema(username=username, email=f"{username}@example.com", password=password)
        created_user = user_repository.create_user_sync(user_in=user_in, hashed_password=hashed_password)
        if created_user:
            print(f"Пользователь '{created_user.username}' с email '{created_user.email}' успешно создан.")
        else:
            print(f"ОШИБКА: Не удалось создать пользователя '{username}'.")


def main():
    """Главная функция для парсинга аргументов и запуска логики."""
    parser = argparse.ArgumentParser(description="Сброс или создание пароля пользователя в MongoDB.")
    parser.add_argument("--username", required=True, help="Имя пользователя (логин).")
    parser.add_argument("--password", required=True, help="Новый пароль для пользователя.")
    args = parser.parse_args()

    print("Подключаемся к MongoDB...")
    try:
        # Подключаемся к MongoDB, используя URI из настроек
        client = MongoClient(settings.MONGO_DB_URL)
        # Получаем объект базы данных
        db = client[settings.MONGO_DB_NAME]
        
        # Проверяем соединение
        db.command('ping')
        print("Соединение с MongoDB установлено.")

        reset_or_create_user(db, args.username, args.password)

    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        sys.exit(1)
    finally:
        if 'client' in locals() and client:
            client.close()
            print("Соединение с MongoDB закрыто.")

if __name__ == "__main__":
    main()