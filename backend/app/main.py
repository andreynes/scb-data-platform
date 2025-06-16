import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
# Импортируем все нужные функции для обеих баз данных
from app.db.session import (
    connect_to_mongo,
    close_mongo_connection,
    connect_to_clickhouse,
    close_clickhouse_connection,
    get_mongo_db  # <--- ДОБАВЛЕН ИМПОРТ
)
# Импортируем репозиторий для инициализации
from app.repositories.user_repo import UserRepo # <--- ДОБАВЛЕН ИМПОРТ
from app.api.v1.api import api_router_v1 as api_router_v1
from app.core.logging_config import setup_logging

# Настройка логирования при старте
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API для доступа к данным и управления системой SCB DB",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Обработчик старта приложения
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup...")
    # 1. Подключаемся к обеим базам
    await connect_to_mongo()
    await connect_to_clickhouse()
    
    # 2. Инициализируем репозитории и создаем индексы (если нужно)
    try:
        # Получаем соединение с БД, которое мы только что открыли
        mongo_db_session = await get_mongo_db() 
        user_repo = UserRepo(mongo_db_session)
        # Вызываем метод для создания индексов
        await user_repo.initialize_repo() 
    except Exception as e:
        logger.error(f"Failed to initialize repositories or create indexes: {e}")
        # В реальном приложении здесь можно было бы остановить запуск
        # raise e


# Обработчик остановки приложения
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown...")
    # Закрываем оба соединения
    await close_mongo_connection()
    await close_clickhouse_connection()

# Настройка CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

app.include_router(api_router_v1, prefix=settings.API_V1_STR)

logger.info("Application configured.")