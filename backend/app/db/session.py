# backend/app/db/session.py
import logging
from typing import Optional, Generator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
# --- ИЗМЕНЕНИЕ: Используем СИНХРОННЫЙ клиент ClickHouse ---
from clickhouse_connect.driver import Client as ClickHouseClient
import clickhouse_connect

from core.config import settings

logger = logging.getLogger(__name__)

# --- MongoDB (остается без изменений) ---
mongo_client: Optional[AsyncIOMotorClient] = None

async def connect_to_mongo():
    global mongo_client
    logger.info("Connecting to MongoDB...")
    try:
        mongo_client = AsyncIOMotorClient(str(settings.MONGO_DB_URL), serverSelectionTimeoutMS=5000)
        await mongo_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
        mongo_client = None

async def close_mongo_connection():
    global mongo_client
    if mongo_client:
        logger.info("Closing MongoDB connection...")
        mongo_client.close()
        logger.info("MongoDB connection closed.")

async def get_mongo_db() -> AsyncIOMotorDatabase:
    if mongo_client is None:
        raise Exception("MongoDB client is not initialized.")
    return mongo_client[settings.MONGO_DB_NAME]

# --- ClickHouse (ПЕРЕПИСАНО НА СИНХРОННЫЙ КЛИЕНТ) ---
clickhouse_client: Optional[ClickHouseClient] = None

def connect_to_clickhouse():
    """Синхронная функция для подключения к ClickHouse."""
    global clickhouse_client
    logger.info("Connecting to ClickHouse...")
    try:
        clickhouse_client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            user=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
            database=settings.CLICKHOUSE_DB,
        )
        clickhouse_client.ping()
        logger.info("Successfully connected to ClickHouse.")
    except Exception as e:
        logger.error(f"Failed to connect to ClickHouse: {e}", exc_info=True)
        clickhouse_client = None

def close_clickhouse_connection():
    """Синхронная функция для закрытия соединения с ClickHouse."""
    global clickhouse_client
    if clickhouse_client:
        logger.info("Closing ClickHouse connection...")
        clickhouse_client.close()
        logger.info("ClickHouse connection closed.")

def get_clickhouse_client() -> Generator[ClickHouseClient, None, None]:
    """Синхронная зависимость для получения клиента ClickHouse."""
    if clickhouse_client is None:
        raise Exception("ClickHouse client is not initialized.")
    try:
        yield clickhouse_client
    finally:
        # Глобальный клиент не закрываем после каждого запроса
        pass