import logging
from typing import AsyncGenerator, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)

mongo_client: Optional[AsyncIOMotorClient] = None

async def connect_to_mongo():
    global mongo_client
    logger.info("Connecting to MongoDB...")
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_DB_URL)
        # Проверка соединения (опционально, но рекомендуется)
        await mongo_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        mongo_client = None # Убедиться, что клиент None при ошибке

async def close_mongo_connection():
    global mongo_client
    if mongo_client:
        logger.info("Closing MongoDB connection...")
        mongo_client.close()
        logger.info("MongoDB connection closed.")

async def get_mongo_db() -> AsyncIOMotorDatabase:
    if mongo_client is None:
        # Эта ситуация означает ошибку при старте приложения
        logger.critical("MongoDB client is not initialized!")
        raise Exception("Database client not initialized. Check startup logs.")
    return mongo_client[settings.MONGO_DB_NAME]

# Потенциально здесь же можно добавить get_clickhouse_client, если он будет нужен глобально
# async def get_clickhouse_client() -> AsyncClient: ...