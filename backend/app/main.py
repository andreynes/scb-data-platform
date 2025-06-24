# backend/app/main.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import (
    connect_to_mongo,
    close_mongo_connection,
    connect_to_clickhouse,
    close_clickhouse_connection,
    get_mongo_db
)
from app.repositories.user_repo import UserRepo
from app.api.v1.api import api_router # Используем правильное имя
from app.core.logging_config import setup_logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

# Создание основного объекта приложения FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API для доступа к данным и управления системой SCB DB",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Обработчик события "startup"
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup...")
    await connect_to_mongo()
    await connect_to_clickhouse()
    
    # Инициализация репозиториев и создание индексов
    try:
        mongo_db_session = await get_mongo_db() 
        user_repo = UserRepo(mongo_db_session)
        await user_repo.initialize_repo() 
    except Exception as e:
        logger.error(f"Failed to initialize repositories or create indexes: {e}")

# Обработчик события "shutdown"
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown...")
    await close_mongo_connection()
    await close_clickhouse_connection()

# Настройка CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Эндпоинт для проверки "здоровья" сервиса
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

# Подключение всех роутеров из api.py с префиксом /api/v1
app.include_router(api_router, prefix=settings.API_V1_STR)

logger.info("Application configured.")