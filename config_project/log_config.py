import sys

from loguru import logger


def setup_logger():
    """Настройка конфигурация логирования проекта"""
    try:
        # Очистка всех предыдущих обработчиков
        logger.remove()

        logger.add("logs/file_{time:DD-MM-YYYY}.log",
                   rotation="00:00",
                   level="DEBUG",
                   format="{time:DD-MM-YYYY HH:mm:ss} | {level} | {file.name}:{line} | {message}"
                   )  # Логирование в файл по дате

        logger.add("logs/error_{time:DD-MM-YYYY}.log",
                   rotation="00:00",
                   level="ERROR",
                   format="{time:DD-MM-YYYY HH:mm:ss} | {level} | {file.name}:{line} | {message}"
                   )  # Логирование ошибок по дате
        # Логирование ошибок в консоль
        logger.add(
            sys.stderr,
            level="DEBUG",
            format="{time:DD-MM-YYYY HH:mm:ss} | {level} | {file.name}:{line} | {message}"
        )
    except Exception:
        logger.exception('Произошла ошибки при инициализации логирования')
