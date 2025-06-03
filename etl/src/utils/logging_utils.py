# etl/src/utils/logging_utils.py
import logging
import sys

def setup_etl_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Настраивает и возвращает стандартный Python логгер для ETL задач."""
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())

    # Предотвращаем дублирование логов, если обработчик уже есть
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

if __name__ == '__main__':
    # Пример использования
    logger = setup_etl_logger(__name__, "DEBUG")
    logger.debug("Это debug сообщение.")
    logger.info("Это info сообщение.")
    logger.warning("Это warning сообщение.")