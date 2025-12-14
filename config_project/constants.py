import os
from pathlib import Path

from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parent.parent / '.env'

load_dotenv(dotenv_path=dotenv_path)


ENVIRONMENT = os.getenv('ENVIRONMENT')  # Состояние для запуска проекта
BOT_TOKEN = os.getenv("BOT_TOKEN") if ENVIRONMENT == 'production' else os.getenv("TEST_BOT_TOKEN")


# Данные для подключения к БД
# dev
LOCAL_DB_USER_NAME = os.getenv('LOCAL_DB_USER_NAME')
LOCAL_DB_PASSWORD = os.getenv('LOCAL_DB_PASSWORD')

# prod or container
USER_NAME_DB = os.getenv('USER_NAME_DB')
PASSWORD_DB = os.getenv('PASSWORD_DB')
PORT_DB = os.getenv('PORT_DB', '5432')
NAME_DB = os.getenv('NAME_DB')

CONTAINER_NAME_DB = os.getenv('CONTAINER_NAME_DB')
