import os
from loguru import logger
from sqlalchemy import inspect

from src.database.engine import engine
from src.database.models import Users, Videos, VideoSnapshots, Creators, Base
from config_project.constants import dotenv_path

from config_project.log_config import setup_logger



class ConfigProject:
    @staticmethod
    def check_db_and_tables():
        """Проверка подключения к БД и существования таблицы в БД"""

        # Задаем список таблиц для проверки
        tables = [Users, Videos, VideoSnapshots, Creators]  # Используем классы моделей
        try:
            with engine.connect() as connection:
                inspector = inspect(connection)
                existing_tables = inspector.get_table_names()

                for table in tables:
                    if table.__tablename__ not in existing_tables:
                        logger.info(f"Таблица '{table.__tablename__}' не найдена. Создаем таблицу.")
                        Base.metadata.create_all(engine)  # Создание всех таблиц, которые не существуют
                        logger.info(f"Таблица '{table.__tablename__}' была создана.")

                logger.info("Проверка таблиц прошла успешно.")
        except Exception as e:
            logger.error(f'Ошибка при проверке таблиц: {e}')
            raise

    @staticmethod
    def check_env_var():
        """Проверка, что все переменные из .env загружены в окружение, с игнорированием комментариев"""

        if not os.path.exists(dotenv_path):
            logger.warning(f".env файл не найден по пути: {dotenv_path}")
            return

        required_keys = []

        with open(dotenv_path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                # Пропускаем пустые строки и комментарии
                if not stripped or stripped.startswith("#"):
                    continue
                # Получаем имя переменной до первого "="
                if "=" in stripped:
                    key = stripped.split("=", 1)[0].strip()
                    required_keys.append(key)
        missing = [key for key in required_keys if os.environ.get(key) is None]

        if missing:
            for key in missing:
                logger.error(f"Переменная {key} из .env не загружена в окружение.")
            raise EnvironmentError(f"Переменные не загружены: {', '.join(missing)}")
        logger.info('Проверка переменных виртуального окружения прошла успешно')

    def prepare_check_project(self):
        """Функция предварительной проверки для инициализации системы."""
        try:
            setup_logger()  # Настройка логирования
            logger.info('Настройка логов пройдена успешно')

            steps = [
                ("Переменные окружения", self.check_env_var),
                ("Подключение к БД и таблицы", self.check_db_and_tables),
            ]
            for name, func in steps:
                try:
                    logger.info(f'Запуск: {name}')
                    func()  # ждем выполнения
                    logger.info(f'Успешно: {name}')
                except Exception as e:
                    logger.exception(f'Ошибка на шаге "{name}": {e}')
                    return False
            return True
        except Exception:
            logger.exception(f'Ошибка предварительной проверки')
            return False


if '__main__' == __name__:
    obj = ConfigProject()
    obj.check_db_and_tables()

