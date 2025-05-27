import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from backend.app.db.session import connect_to_mongo, close_mongo_connection
# from backend.app.api.v1.api import api_router_v1 # Раскомментируем, когда будет api_router_v1
from backend.app.core.logging_config import setup_logging # Предполагаем, что это уже есть

# Настройка логирования при старте
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0", # Или из settings, если там будет версия проекта
    description="API для доступа к данным и управления системой SCB DB",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup...")
    await connect_to_mongo()
    # await connect_to_clickhouse() # Если будет ClickHouse клиент

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown...")
    await close_mongo_connection()
    # await close_clickhouse_connection() # Если будет ClickHouse клиент

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
    # Можно добавить проверку доступности БД
    return {"status": "ok"}

# app.include_router(api_router_v1, prefix=settings.API_V1_STR) # Раскомментируем позже

logger.info("Application configured.")