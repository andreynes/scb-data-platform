from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SCB DB Backend"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str # Ключ для подписи JWT, критически важно!
    ALGORITHM: str = "HS256" # Алгоритм подписи JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 дней

    # MongoDB settings
    MONGO_DB_URL: str
    MONGO_DB_NAME: str

    # CORS settings
    CORS_ORIGINS: List[str] = ["*"] # Настроить для production!

    # LLM settings (оставим для будущего, но определим)
    LLM_PROVIDER: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    LLM_API_ENDPOINT: Optional[str] = None
    LLM_PARSING_MODEL_NAME: Optional[str] = None
    LLM_CODEGEN_MODEL_NAME: Optional[str] = None

    # Logging settings
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env" # Указывает FastAPI Pydantic загружать из .env файла
        env_file_encoding = 'utf-8'
        extra = 'ignore' # Игнорировать лишние переменные окружения

settings = Settings()