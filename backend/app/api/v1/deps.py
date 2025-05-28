# backend/app/api/v1/deps.py
from fastapi import Depends

# Для MongoDB
from app.db.session import get_mongo_db # Убедитесь, что этот импорт корректен
from motor.motor_asyncio import AsyncIOMotorDatabase # Или ваш тип клиента/базы

# Для Ontology
from app.repositories.ontology_repo import OntologyRepo
from app.services.ontology_service import OntologyService

# --- Зависимости для Базы Данных ---
async def get_db() -> AsyncIOMotorDatabase: # Упрощено, предполагаем get_mongo_db возвращает базу
    return await get_mongo_db()

# --- Зависимости для Репозиториев ---
def get_ontology_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> OntologyRepo:
    return OntologyRepo(db=db)

# --- Зависимости для Сервисов ---
def get_ontology_service(
    ontology_repo: OntologyRepo = Depends(get_ontology_repo)
) -> OntologyService:
    return OntologyService(ontology_repo=ontology_repo)

# --- Аутентификация пока НЕ НУЖНА для эндпоинта онтологии на этом этапе ---
# Закомментируем или удалим все, что связано с get_current_active_user,
# UserSchema, OAuth2PasswordBearer, settings, decode_jwt_token, UserRepo и т.д.,
# если они не используются другими активными эндпоинтами, которые вы хотите сейчас запустить.
# Если get_ontology_service или его зависимости требуют UserSchema, это нужно будет учесть.
# Но для простого отображения онтологии обычно аутентификация не критична на начальном этапе.