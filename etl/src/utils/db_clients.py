# etl/src/utils/db_clients.py
import os
import pymongo
import clickhouse_connect
from typing import Optional

# --- Клиенты для баз данных ---
# Эти переменные будут хранить синглтоны клиентов для переиспользования
_mongo_client: Optional[pymongo.MongoClient] = None
_clickhouse_client: Optional[clickhouse_connect.driver.Client] = None

def get_mongo_db_client() -> pymongo.database.Database:
    """
    Создает (если еще не создан) и возвращает клиент к базе данных MongoDB.
    Использует переменные окружения для подключения.
    """
    global _mongo_client
    if _mongo_client is None:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI environment variable is not set.")
        _mongo_client = pymongo.MongoClient(mongo_uri)
    
    db_name = os.getenv("MONGO_DB_NAME", "scb_db")
    return _mongo_client[db_name]

def get_clickhouse_client() -> clickhouse_connect.driver.Client:
    """
    Создает (если еще не создан) и возвращает клиент ClickHouse.
    Использует переменные окружения для подключения.
    """
    global _clickhouse_client
    if _clickhouse_client is None:
        _clickhouse_client = clickhouse_connect.get_client(
            host=os.getenv("CLICKHOUSE_HOST", "localhost"),
            port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
            user=os.getenv("CLICKHOUSE_USER", "default"),
            password=os.getenv("CLICKHOUSE_PASSWORD", ""),
            database=os.getenv("CLICKHOUSE_DB", "scb_warehouse")
        )
    return _clickhouse_client