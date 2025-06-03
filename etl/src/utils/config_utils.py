# etl/src/utils/config_utils.py
from pydantic_settings import BaseSettings
from typing import Optional

class ETLSettings(BaseSettings):
    MONGO_DB_URL: str = "mongodb://localhost:27017/"
    MONGO_DB_NAME: str = "scb_db_data_lake"
    RAW_DATA_LAKE_COLLECTION: str = "raw_data_lake"
    ONTOLOGY_SCHEMAS_COLLECTION: str = "ontology_schemas"
    ONTOLOGY_VOCABULARIES_COLLECTION: str = "ontology_vocabularies"
    ONTOLOGY_STATUS_COLLECTION: str = "ontology_status" # Коллекция для статуса активной онтологии

    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 8123 # или 9000 для нативного
    CLICKHOUSE_USER: Optional[str] = "default"
    CLICKHOUSE_PASSWORD: Optional[str] = ""
    CLICKHOUSE_DB: str = "scb_warehouse"
    CLICKHOUSE_ATOMIC_TABLE: str = "atomic_data_warehouse"

    # Можно добавить другие настройки по мере необходимости

    class Config:
        env_file = ".env" # Если используете .env файл для конфигурации
        env_file_encoding = 'utf-8'
        extra = 'ignore'

etl_settings = ETLSettings()

if __name__ == '__main__':
    # Пример использования
    print(f"MongoDB URL: {etl_settings.MONGO_DB_URL}")
    print(f"ClickHouse Host: {etl_settings.CLICKHOUSE_HOST}")