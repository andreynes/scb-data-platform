# backend/app/core/config.py
import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SCB DB Backend"
    API_V1_STR: str = "/api/v1"

    # JWT Settings - Pydantic автоматически подхватит их из окружения
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # MongoDB Settings - Pydantic автоматически подхватит их из окружения
    MONGO_DB_URL: str 
    MONGO_DB_NAME: str
    
    # ClickHouse Settings - Pydantic автоматически подхватит их из окружения
    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: int
    CLICKHOUSE_USER: str
    CLICKHOUSE_PASSWORD: str
    CLICKHOUSE_DB: str

    # CORS_ORIGINS_STR будет прочитана из окружения, если она там есть
    CORS_ORIGINS_STR: Optional[str] = None
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        if self.CORS_ORIGINS_STR:
            return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]
        return ["http://localhost:5173"]

    class Config:
        # Указываем Pydantic, что нужно читать переменные из .env файла
        # Путь теперь не нужен, так как docker-compose сам их передаст
        case_sensitive = True
        # Мы больше не указываем env_file, Pydantic будет читать из переменных окружения,
        # которые предоставляет Docker Compose.
        
settings = Settings()