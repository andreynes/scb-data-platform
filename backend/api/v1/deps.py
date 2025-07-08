# backend/app/api/v1/deps.py

from typing import Optional, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.config import settings
from db.session import get_mongo_db, get_clickhouse_client
from schemas.token_schemas import TokenDataSchema
from schemas.user_schemas import UserSchema
from repositories.user_repo import UserRepo
from repositories.ontology_repo import OntologyRepo
from repositories.data_lake_repo import DataLakeRepo
from repositories.warehouse_repo import WarehouseRepo
from services.auth_service import AuthService
from services.ontology_service import OntologyService
from services.file_processing_service import FileProcessingService
from services.data_query_service import DataQueryService
from services.verification_service import VerificationService
from services.admin_service import AdminService
# --- ИЗМЕНЕНИЕ: Импортируем СИНХРОННЫЙ клиент ---
from clickhouse_connect.driver import Client as ClickHouseClient


# --- Схема OAuth2 ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# --- Зависимости для Репозиториев ---
def get_user_repo(db: AsyncIOMotorDatabase = Depends(get_mongo_db)) -> UserRepo:
    return UserRepo(db=db)

def get_ontology_repo(db: AsyncIOMotorDatabase = Depends(get_mongo_db)) -> OntologyRepo:
    return OntologyRepo(db=db)

def get_data_lake_repo(db: AsyncIOMotorDatabase = Depends(get_mongo_db)) -> DataLakeRepo:
    return DataLakeRepo(db=db)

# --- ИЗМЕНЕНИЕ: Зависимость теперь принимает СИНХРОННЫЙ клиент ---
def get_warehouse_repo(
    ch_client: ClickHouseClient = Depends(get_clickhouse_client)
) -> WarehouseRepo:
    return WarehouseRepo(ch_client=ch_client)

# --- Зависимости для Сервисов ---
def get_auth_service(user_repo: UserRepo = Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo=user_repo)

def get_ontology_service(
    ontology_repo: OntologyRepo = Depends(get_ontology_repo)
) -> OntologyService:
    return OntologyService(ontology_repo=ontology_repo)

def get_data_query_service(
    warehouse_repo: WarehouseRepo = Depends(get_warehouse_repo),
    ontology_service: OntologyService = Depends(get_ontology_service),
    data_lake_repo: DataLakeRepo = Depends(get_data_lake_repo) # Добавляем зависимость
) -> DataQueryService:
    return DataQueryService(
        warehouse_repo=warehouse_repo, ontology_service=ontology_service, data_lake_repo=data_lake_repo
    )
    
def get_file_processing_service(
    data_lake_repo: DataLakeRepo = Depends(get_data_lake_repo)
) -> FileProcessingService:
    return FileProcessingService(data_lake_repo=data_lake_repo)

def get_verification_service(
    data_lake_repo: DataLakeRepo = Depends(get_data_lake_repo),
    warehouse_repo: WarehouseRepo = Depends(get_warehouse_repo),
) -> VerificationService:
    return VerificationService(
        data_lake_repo=data_lake_repo, warehouse_repo=warehouse_repo
    )

def get_admin_service(
    data_lake_repo: DataLakeRepo = Depends(get_data_lake_repo),
    verification_service: VerificationService = Depends(get_verification_service)
) -> AdminService:
    return AdminService(
        data_lake_repo=data_lake_repo,
        verification_service=verification_service
    )

# --- Зависимости для Аутентификации и Авторизации (остаются async) ---
async def get_current_user(
    token: str = Depends(oauth2_scheme), user_repo: UserRepo = Depends(get_user_repo)
) -> UserSchema:
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
        if not username:
            raise credentials_exception
        token_data = TokenDataSchema(username=username)
    except (JWTError, ValidationError):
        raise credentials_exception

    user = await user_repo.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
        
    return UserSchema.model_validate(user)

async def get_current_active_user(
    current_user: UserSchema = Depends(get_current_user),
) -> UserSchema:
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user

async def get_current_admin_user(
    current_user: UserSchema = Depends(get_current_active_user),
) -> UserSchema:
    if current_user.role not in ["admin", "maintainer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="The user does not have enough privileges"
        )
    return current_user