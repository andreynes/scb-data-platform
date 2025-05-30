# backend/app/core/config.py
import os
from typing import List, Union, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загружаем переменные из .env файла, если он есть
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "SCB DB Backend"
    API_V1_STR: str = "/api/v1"

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_in_env") # КРИТИЧНО: ЗАМЕНИТЬ И ВЫНЕСТИ В .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 дней

    # MongoDB Settings
    MONGO_DB_URL: str = os.getenv("MONGO_DB_URL", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "scb_db")
    
    # ClickHouse Settings (если нужны глобально)
    # CLICKHOUSE_HOST: str = os.getenv("CLICKHOUSE_HOST", "localhost")
    # CLICKHOUSE_PORT: int = int(os.getenv("CLICKHOUSE_PORT", "9000"))
    # CLICKHOUSE_USER: str = os.getenv("CLICKHOUSE_USER", "default")
    # CLICKHOUSE_PASSWORD: str = os.getenv("CLICKHOUSE_PASSWORD", "")
    # CLICKHOUSE_DB: str = os.getenv("CLICKHOUSE_DB", "scb_warehouse")

    # Airflow API Settings (если нужны глобально)
    # AIRFLOW_API_URL: Optional[str] = os.getenv("AIRFLOW_API_URL")
    # AIRFLOW_USER: Optional[str] = os.getenv("AIRFLOW_USER")
    # AIRFLOW_PASSWORD: Optional[str] = os.getenv("AIRFLOW_PASSWORD")
    
    # CORS Origins
    CORS_ORIGINS: List[str] = ["http://localhost:5173"] # Добавьте сюда URL вашего фронтенда

    class Config:
        case_sensitive = True
        env_file = ".env" # Если используете .env файл для переменных окружения
        env_file_encoding = 'utf-8'

settings = Settings()