# backend/app/core/config.py
import os
from typing import List, Optional

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SCB DB Backend"
    API_V1_STR: str = "/api/v1"

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # MongoDB Settings
    MONGO_DB_URL: str
    MONGO_DB_NAME: str
    
    # ClickHouse Settings
    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: int
    CLICKHOUSE_USER: str
    CLICKHOUSE_PASSWORD: str
    CLICKHOUSE_DB: str

    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # --- Airflow API Settings (ДОБАВЛЕНО) ---
    AIRFLOW_API_URL: Optional[str] = None
    AIRFLOW_API_USER: Optional[str] = "airflow"
    AIRFLOW_API_PASSWORD: Optional[str] = "airflow"

    class Config:
        case_sensitive = True
        # УДАЛЕНО: env_file = "/app/.env"
        env_file_encoding = 'utf-8'

settings = Settings()