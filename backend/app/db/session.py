import logging
from typing import AsyncGenerator, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import clickhouse_connect

from app.core.config import settings

logger = logging.getLogger(__name__)

# --- MongoDB ---
mongo_client: Optional[AsyncIOMotorClient] = None

async def connect_to_mongo():
    global mongo_client
    logger.info("Connecting to MongoDB...")
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_DB_URL)
        await mongo_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        mongo_client = None

async def close_mongo_connection():
    global mongo_client
    if mongo_client:
        logger.info("Closing MongoDB connection...")
        mongo_client.close()
        logger.info("MongoDB connection closed.")

async def get_mongo_db() -> AsyncIOMotorDatabase:
    if mongo_client is None:
        logger.critical("MongoDB client is not initialized!")
        raise Exception("Database client not initialized. Check startup logs.")
    return mongo_client[settings.MONGO_DB_NAME]


# --- ClickHouse ---
ch_client: Optional[clickhouse_connect.driver.AsyncClient] = None

async def connect_to_clickhouse():
    global ch_client
    logger.info("Connecting to ClickHouse...")
    try:
        # Убрали await отсюда
        ch_client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=int(settings.CLICKHOUSE_PORT),
            user=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
            database=settings.CLICKHOUSE_DB,
        )
        # Убираем await и отсюда
        ch_client.ping()
        logger.info("Successfully connected to ClickHouse.")
    except Exception as e:
        logger.error(f"Failed to connect to ClickHouse: {e}")
        ch_client = None

async def close_clickhouse_connection():
    global ch_client
    if ch_client and ch_client.connected:
        logger.info("Closing ClickHouse connection...")
        await ch_client.close()
        logger.info("ClickHouse connection closed.")

async def get_clickhouse_client() -> clickhouse_connect.driver.AsyncClient:
    """
    Зависимость для FastAPI для получения асинхронного клиента ClickHouse.
    """
    if ch_client is None or not ch_client.connected:
        logger.critical("ClickHouse client is not initialized!")
        raise Exception("Database client not initialized. Check startup logs.")
    return ch_client