# backend/app/core/config.py
import os
from typing import List, Union, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

# Определяем путь к корневой директории проекта
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = PROJECT_ROOT / "infra" / "compose" / ".env"

# Загружаем переменные из .env файла по указанному пути
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    print(f"Warning: .env file not found at {ENV_PATH}")


class Settings(BaseSettings):
    PROJECT_NAME: str = "SCB DB Backend"
    API_V1_STR: str = "/api/v1"

    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_in_env_or_generated")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # MongoDB Settings
    # Внутри Docker-сети используем имя сервиса 'mongo', а не 'localhost'
    MONGO_DB_URL: str = os.getenv("MONGO_DB_URL", "mongodb://mongo:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "scb_db")
    
    # ClickHouse Settings
    # Внутри Docker-сети используем имя сервиса 'clickhouse', а не 'localhost'
    CLICKHOUSE_HOST: str = os.getenv("CLICKHOUSE_HOST", "clickhouse")
    CLICKHOUSE_PORT: int = int(os.getenv("CLICKHOUSE_PORT", "8123"))
    CLICKHOUSE_USER: str = os.getenv("CLICKHOUSE_USER", "default")
    CLICKHOUSE_PASSWORD: str = os.getenv("CLICKHOUSE_PASSWORD", "")
    # Переименовал для единообразия, чтобы соответствовать session.py
    CLICKHOUSE_DB: str = os.getenv("CLICKHOUSE_DB_FOR_SCB_WAREHOUSE", "scb_warehouse")

    CORS_ORIGINS_STR: Optional[str] = os.getenv("CORS_ORIGINS")
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        if self.CORS_ORIGINS_STR:
            return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]
        # Добавим адрес фронтенда из docker-compose, если он там есть
        return ["http://localhost:5173", "http://frontend:5173"]

    class Config:
        case_sensitive = True
        env_file = str(ENV_PATH)
        env_file_encoding = 'utf-8'
        extra = 'ignore'

settings = Settings()