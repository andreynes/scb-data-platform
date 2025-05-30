# backend/app/api/v1/deps.py
from typing import Generator, Optional, AsyncGenerator 

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

# Настройки и сессии БД
from app.core.config import settings
from app.db.session import get_mongo_db 
from motor.motor_asyncio import AsyncIOMotorDatabase 

# Схемы
from app.schemas.token_schemas import TokenDataSchema
from app.schemas.user_schemas import UserSchema

# Репозитории
from app.repositories.user_repo import UserRepo 
from app.repositories.ontology_repo import OntologyRepo
from app.repositories.data_lake_repo import DataLakeRepo 

# Сервисы
from app.services.ontology_service import OntologyService
from app.services.file_processing_service import FileProcessingService
from app.services.auth_service import AuthService 
# from app.clients.airflow_client import AirflowClient 

# --- Зависимости для Базы Данных ---
# Эта зависимость у вас уже была, просто убедимся, что она возвращает правильный тип
async def get_db() -> AsyncIOMotorDatabase:
    """
    Асинхронная зависимость для получения экземпляра базы данных MongoDB.
    """
    # Предполагается, что get_mongo_db() - это асинхронная функция,
    # которая правильно управляет жизненным циклом соединения/клиента.
    # Если get_mongo_db() возвращает клиент, а не базу, то здесь нужно получить базу:
    # client = await get_mongo_client()
    # return client[settings.MONGO_DB_NAME]
    # В вашем случае, похоже, get_mongo_db уже возвращает базу.
    return await get_mongo_db()

# --- OAuth2 Схема ---
# Нужна для get_current_user. Указывает FastAPI, откуда брать токен.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token" # Эндпоинт для получения токена
)

# --- Зависимости для Репозиториев ---
def get_user_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserRepo:
    """
    Зависимость для получения экземпляра UserRepo.
    """
    return UserRepo(db=db)

def get_ontology_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> OntologyRepo:
    """
    Зависимость для получения экземпляра OntologyRepo.
    """
    return OntologyRepo(db=db)

# --- НОВАЯ ЗАВИСИМОСТЬ ДЛЯ РЕПОЗИТОРИЯ ---
def get_data_lake_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> DataLakeRepo:
    """
    Зависимость для получения экземпляра DataLakeRepo.
    """
    return DataLakeRepo(db=db)

def get_auth_service(user_repo: UserRepo = Depends(get_user_repo)) -> AuthService:
    """
    Зависимость для получения экземпляра AuthService.
    """
    return AuthService(user_repo=user_repo)

# --- КОНЕЦ НОВОЙ ЗАВИСИМОСТИ ДЛЯ РЕПОЗИТОРИЯ ---

# --- Зависимости для Сервисов ---
def get_ontology_service(
    ontology_repo: OntologyRepo = Depends(get_ontology_repo)
) -> OntologyService:
    """
    Зависимость для получения экземпляра OntologyService.
    """
    return OntologyService(ontology_repo=ontology_repo)

# --- НОВАЯ ЗАВИСИМОСТЬ ДЛЯ СЕРВИСА ---
# def get_airflow_client() -> AirflowClient: # Если FileProcessingService его использует
#     # Здесь должна быть логика получения или создания клиента Airflow
#     # Например, из настроек
#     return AirflowClient(api_url=settings.AIRFLOW_API_URL, auth=(settings.AIRFLOW_USER, settings.AIRFLOW_PASSWORD))

def get_file_processing_service(
    data_lake_repo: DataLakeRepo = Depends(get_data_lake_repo)
    # airflow_client: AirflowClient = Depends(get_airflow_client) # Если используется
) -> FileProcessingService:
    """
    Зависимость для получения экземпляра FileProcessingService.
    """
    return FileProcessingService(
        data_lake_repo=data_lake_repo
        # airflow_client=airflow_client # Если используется
    )
# --- КОНЕЦ НОВОЙ ЗАВИСИМОСТИ ДЛЯ СЕРВИСА ---


# --- Зависимости для Аутентификации и Авторизации ---
# Эти функции понадобятся для защиты эндпоинта /files/upload

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepo = Depends(get_user_repo)
) -> Optional[UserSchema]:
    """
    Зависимость для получения текущего пользователя на основе JWT токена.
    Возвращает UserSchema или выбрасывает HTTPException, если токен невалиден или пользователь не найден.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenDataSchema(username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    user = await user_repo.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return UserSchema.model_validate(user) # Используем model_validate для Pydantic v2+

async def get_current_active_user(
    current_user: UserSchema = Depends(get_current_user)
) -> UserSchema:
    """
    Зависимость для получения текущего активного пользователя.
    Выбрасывает HTTPException, если пользователь неактивен.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

# Если понадобится get_current_admin_user, он может выглядеть так:
# async def get_current_admin_user(
#     current_user: UserSchema = Depends(get_current_active_user)
# ) -> UserSchema:
#     """
#     Зависимость для получения текущего активного пользователя с правами администратора/мейнтейнера.
#     Выбрасывает HTTPException, если у пользователя нет нужных прав.
#     """
#     if current_user.role not in ["admin", "maintainer"]: # Пример проверки роли
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="The user doesn't have enough privileges"
#         )
#     return current_user