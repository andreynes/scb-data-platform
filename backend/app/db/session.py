# backend/app/db/session.py
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from clickhouse_connect.driver.httpclient import HttpClient as ClickHouseClient
from core.config import settings

mongo_client: Optional[AsyncIOMotorClient] = None
clickhouse_client: Optional[ClickHouseClient] = None
logger = logging.getLogger(__name__)

async def connect_to_mongo():
    global mongo_client
    logger.info("Connecting to MongoDB...")
    try:
        mongo_client = AsyncIOMotorClient(str(settings.MONGO_DB_URL))
        await mongo_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        mongo_client = None

async def close_mongo_connection():
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed.")

def connect_to_clickhouse():
    global clickhouse_client
    logger.info("Connecting to ClickHouse...")
    try:
        # --- ИСПРАВЛЕНИЕ: Вызываем конструктор класса напрямую, без .get_client ---
        clickhouse_client = ClickHouseClient(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            username=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
            database=settings.CLICKHOUSE_DB,
            interface='http'
        )
        # ping() является синхронным, оставляем без await
        clickhouse_client.ping()
        logger.info("Successfully connected to ClickHouse.")
    except Exception as e:
        logger.error(f"Failed to connect to ClickHouse: {e}", exc_info=True)
        clickhouse_client = None

def close_clickhouse_connection():
    global clickhouse_client
    if clickhouse_client and clickhouse_client.is_connected:
        clickhouse_client.close()
        logger.info("ClickHouse connection closed.")

async def get_mongo_db() -> AsyncIOMotorDatabase:
    if mongo_client is None: raise RuntimeError("MongoDB client is not initialized")
    return mongo_client[settings.MONGO_DB_NAME]

def get_clickhouse_client() -> ClickHouseClient:
    if clickhouse_client is None or not clickhouse_client.is_connected:
        raise RuntimeError("ClickHouse client is not initialized or disconnected")
    return clickhouse_client