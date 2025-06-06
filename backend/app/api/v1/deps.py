# backend/app/api/v1/deps.py
from typing import Generator, Optional, AsyncGenerator 

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

# Настройки и сессии БД
from app.core.config import settings # <-- Убедитесь, что путь правильный (app.core.config)
from app.db.session import get_mongo_db, get_clickhouse_client # <-- Добавили get_clickhouse_client
from motor.motor_asyncio import AsyncIOMotorDatabase
from clickhouse_connect.driver.client import Client as ClickHouseClient # <-- Добавили импорт клиента ClickHouse

# Схемы
from app.schemas.token_schemas import TokenDataSchema
from app.schemas.user_schemas import UserSchema

# Репозитории
from app.repositories.user_repo import UserRepo 
from app.repositories.ontology_repo import OntologyRepo
from app.repositories.data_lake_repo import DataLakeRepo 
from app.repositories.warehouse_repo import WarehouseRepo # <-- ДОБАВИЛИ

# Сервисы
from app.services.ontology_service import OntologyService
from app.services.file_processing_service import FileProcessingService
from app.services.auth_service import AuthService 
from app.services.data_query_service import DataQueryService # <-- ДОБАВИЛИ
# from app.clients.airflow_client import AirflowClient 

# --- Зависимости для Базы Данных ---
async def get_db() -> AsyncIOMotorDatabase: # Было get_db(), сделал async, так как get_mongo_db() скорее всего async
    """
    Асинхронная зависимость для получения экземпляра базы данных MongoDB.
    """
    mongo_client = await get_mongo_db() # Предполагаем, что get_mongo_db возвращает AsyncIOMotorClient
    if mongo_client is None:
        # logger.critical("MongoDB client is not available") # Рекомендуется логирование
        raise HTTPException(status_code=503, detail="MongoDB connection not available")
    return mongo_client[settings.MONGO_DB_NAME]


async def get_ch_db_client() -> ClickHouseClient: # Сделал async, так как get_clickhouse_client() может быть async
    """
    Асинхронная зависимость для получения экземпляра клиента ClickHouse.
    """
    ch_client_instance = await get_clickhouse_client() # Предполагаем, что get_clickhouse_client возвращает AsyncClient или управляет соединением
    if ch_client_instance is None or not ch_client_instance.is_active:
        # logger.critical("ClickHouse client is not available or not active") # Рекомендуется логирование
        # Можно добавить логику переподключения, если это применимо
        raise HTTPException(status_code=503, detail="ClickHouse connection not available")
    return ch_client_instance


# --- OAuth2 Схема ---
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token" 
)

# --- Зависимости для Репозиториев ---
def get_user_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserRepo:
    return UserRepo(db=db)

def get_ontology_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> OntologyRepo:
    return OntologyRepo(db=db)

def get_data_lake_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> DataLakeRepo:
    return DataLakeRepo(db=db)

def get_warehouse_repo(ch_client: ClickHouseClient = Depends(get_ch_db_client)) -> WarehouseRepo: # <-- ДОБАВИЛИ
    """
    Зависимость для получения экземпляра WarehouseRepo.
    """
    return WarehouseRepo(ch_client=ch_client)


# --- Зависимости для Сервисов ---
def get_auth_service(user_repo: UserRepo = Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo=user_repo)

def get_ontology_service(
    ontology_repo: OntologyRepo = Depends(get_ontology_repo)
) -> OntologyService:
    return OntologyService(ontology_repo=ontology_repo)

# Зависимость для FileProcessingService осталась без изменений, но может понадобиться airflow_client в будущем
def get_file_processing_service(
    data_lake_repo: DataLakeRepo = Depends(get_data_lake_repo)
    # airflow_client: AirflowClient = Depends(get_airflow_client) # Если используется
) -> FileProcessingService:
    return FileProcessingService(
        data_lake_repo=data_lake_repo
        # airflow_client=airflow_client # Если используется
    )

def get_data_query_service( # <-- ДОБАВИЛИ
    warehouse_repo: WarehouseRepo = Depends(get_warehouse_repo),
    # ontology_repo: OntologyRepo = Depends(get_ontology_repo) # Если ваш DataQueryService будет использовать онтологию
) -> DataQueryService:
    """
    Зависимость для получения экземпляра DataQueryService.
    """
    return DataQueryService(
        warehouse_repo=warehouse_repo
        # ontology_repo=ontology_repo # Раскомментируйте, если нужно
    )


# --- Зависимости для Аутентификации и Авторизации ---
async def get_current_user( # Сделал async, так как user_repo методы теперь async
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepo = Depends(get_user_repo) # Используем get_user_repo
) -> UserSchema: # Возвращаем UserSchema, а не Optional[UserSchema], так как при ошибке будет HTTPException
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
        # token_data = TokenDataSchema(username=username) # Валидация через TokenDataSchema полезна
    except (JWTError, ValidationError): # Добавил ValidationError на случай проблем с TokenDataSchema
        raise credentials_exception
    
    # user_in_db = await user_repo.get_user_by_username(username=token_data.username)
    user_in_db = await user_repo.get_user_by_username(username=username) # Используем username напрямую
    if user_in_db is None:
        raise credentials_exception
    # Убедитесь, что UserInDB (из репозитория) и UserSchema (для API) правильно мапятся
    # UserSchema.model_validate(user) для Pydantic v2+ или UserSchema.from_orm(user) для v1
    return UserSchema.model_validate(user_in_db) 

async def get_current_active_user(
    current_user: UserSchema = Depends(get_current_user)
) -> UserSchema:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

# async def get_current_admin_user(...): # Оставляем как есть, если не менялся