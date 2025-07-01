# backend/app/core/logging_config.py
import logging
import sys
from core.config import settings 

# Уровни логирования для стандартных библиотек, которые могут быть слишком "шумными"
# Uvicorn логирует доступ, его можно оставить на INFO или поднять до WARNING, если логов слишком много
LOGGING_CONFIG_DEFAULTS = {
    "version": 1,
    "disable_existing_loggers": False, # Важно оставить существующие логгеры (например, uvicorn)
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter", # Используем форматтер uvicorn для консистентности
            "fmt": "%(levelprefix)s %(asctime)s [%(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": None, # Автоматическое определение или True/False
        },
        "access": { # Форматтер для логов доступа uvicorn
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(asctime)s [%(name)s] %(client_addr)s - "%(request_line)s" %(status_code)s',
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": None,
        },
    },
    "handlers": {
        "default": { # Логи приложения (все, кроме uvicorn.access)
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": sys.stdout, # или sys.stderr
        },
        "access": { # Логи доступа uvicorn
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "uvicorn.error": { # Логи ошибок uvicorn
             "handlers": ["default"], # Используем наш default handler
             "level": "INFO", # Можно настроить
             "propagate": False
        },
        "uvicorn.access": { # Логи доступа uvicorn
             "handlers": ["access"], # Используем наш access handler
             "level": "INFO", # Можно настроить, WARNING чтобы убрать логи доступа
             "propagate": False
        },
        # Можно добавить специфичные настройки для других библиотек, если они слишком "болтливы"
        # "sqlalchemy.engine": {"handlers": ["default"], "level": "WARNING", "propagate": False},
    },
    "root": { # Настройки для корневого логгера (и всех логгеров приложения, если не переопределены)
        "handlers": ["default"],
        "level": "INFO", # Уровень по умолчанию для вашего приложения
    },
}

def setup_logging():
    """
    Настраивает систему логирования для приложения.
    """
    # Устанавливаем уровень корневого логгера из настроек, если он там есть
    log_level_name = settings.LOG_LEVEL.upper() if hasattr(settings, 'LOG_LEVEL') else "INFO"
    
    # Обновляем уровень для корневого логгера в нашей конфигурации
    # Это повлияет на все логгеры, которые не имеют явно заданного уровня
    if "root" in LOGGING_CONFIG_DEFAULTS and "level" in LOGGING_CONFIG_DEFAULTS["root"]:
        LOGGING_CONFIG_DEFAULTS["root"]["level"] = log_level_name
    else:
        # На случай если структура LOGGING_CONFIG_DEFAULTS изменится
        logging.warning("Could not set root logger level from settings in LOGGING_CONFIG_DEFAULTS.")


    # Применяем конфигурацию
    logging.config.dictConfig(LOGGING_CONFIG_DEFAULTS)
    
    logger = logging.getLogger(__name__) # Получаем логгер для этого модуля
    logger.info(f"Logging configured with root level: {log_level_name}")

if __name__ == "__main__":
    # Пример использования
    setup_logging()
    logger = logging.getLogger("my_app_test") # Пример получения логгера в другом модуле
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("Caught an exception:")