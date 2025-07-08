import logging
import sys

# Определяем формат сообщений
LOG_FORMAT = "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Создаем базовый обработчик, который выводит логи в консоль
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

def get_logger(name: str) -> logging.Logger:
    """
    Создает и настраивает логгер с заданным именем.
    """
    logger = logging.getLogger(name)
    
    # Устанавливаем уровень логирования (например, INFO)
    # Это можно вынести в .env файл, если нужно
    logger.setLevel(logging.INFO)
    
    # Добавляем обработчик, чтобы логи выводились в консоль
    # Проверяем, что обработчик еще не добавлен, чтобы избежать дублирования
    if not logger.handlers:
        logger.addHandler(stream_handler)
        
    # Отключаем распространение логов наверх по иерархии,
    # чтобы избежать дублирования, если корневой логгер тоже настроен.
    logger.propagate = False
    
    return logger

# Пример использования, который можно запустить для проверки:
if __name__ == '__main__':
    test_logger = get_logger("test_logger")
    test_logger.info("Это информационное сообщение.")
    test_logger.warning("Это предупреждение.")
    test_logger.error("Это сообщение об ошибке.")