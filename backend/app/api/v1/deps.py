# backend/app/api/v1/deps.py
from typing import AsyncGenerator # Для асинхронных генераторов (если сессии БД так управляются)
from fastapi import Depends
# Для MongoDB
from pymongo.database import Database # Или AsyncIOMotorDatabase из motor.motor_asyncio
from backend.app.db.session import get_mongo_db # Предполагаем, что эта функция есть
# Для Ontology
from backend.app.repositories.ontology_repo import OntologyRepo
from backend.app.services.ontology_service import OntologyService
# Для User (аутентификация, если эндпоинт защищен) - пока закомментировано для MVP эндпоинта онтологии
# from backend.app.schemas.user_schemas import UserSchema
# from backend.app.core.security import decode_jwt_token
# from fastapi.security import OAuth2PasswordBearer
# from jose import jwt, JWTError
# from backend.app.core.config import settings
# from backend.app.repositories.user_repo import UserRepo # Если get_current_active_user будет здесь

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/token") # Если эндпоинт защищен

# --- Зависимости для Базы Данных ---
async def get_db() -> AsyncGenerator[Database, None]: # Или Database, если синхронно
    """
    Зависимость для получения сессии/клиента MongoDB.
    Предполагаем, что get_mongo_db() уже реализована в db.session
    и правильно управляет жизненным циклом соединения/клиента.
    """
    # Если get_mongo_db это генератор, то:
    # async for db_client in get_mongo_db():
    #     yield db_client
    # Если get_mongo_db просто возвращает клиент:
    db_client = await get_mongo_db() # или просто get_mongo_db() если синхронно
    yield db_client
    # Логика закрытия соединения, если она не управляется в get_mongo_db, должна быть здесь
    # await close_mongo_connection() # Пример

# --- Зависимости для Репозиториев ---
def get_ontology_repo(db: Database = Depends(get_db)) -> OntologyRepo: # Или AsyncIOMotorDatabase
    return OntologyRepo(db=db)

# def get_user_repo(db: Database = Depends(get_db)) -> UserRepo:
#     return UserRepo(db=db)

# --- Зависимости для Сервисов ---
def get_ontology_service(
    ontology_repo: OntologyRepo = Depends(get_ontology_repo)
) -> OntologyService:
    return OntologyService(ontology_repo=ontology_repo)

# --- Зависимости для Аутентификации (пример, если эндпоинт будет защищен) ---
# async def get_current_active_user(
#     token: str = Depends(oauth2_scheme),
#     user_repo: UserRepo = Depends(get_user_repo)
# ) -> UserSchema:
#     # ... (логика из вашего core.security или auth_service) ...
#     # Здесь упрощенно, реальная логика сложнее
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = decode_jwt_token(token) # Ваша функция декодирования из core.security
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#
#     user = await user_repo.get_user_by_username(username=username)
#     if user is None or not user.is_active: # UserInDB должен иметь is_active
#         raise credentials_exception
#     return UserSchema.model_validate(user) # или from_orm(user) для Pydantic v1