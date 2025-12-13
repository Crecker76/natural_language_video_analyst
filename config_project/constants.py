import os
from pathlib import Path

from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parent.parent / '.env'

load_dotenv(dotenv_path=dotenv_path)


ENVIRONMENT = os.getenv('ENVIRONMENT')  # Состояние для запуска проекта
BOT_TOKEN = os.getenv("BOT_TOKEN") if ENVIRONMENT == 'production' else os.getenv("TEST_BOT_TOKEN")
NAME_BOT = os.getenv("NAME_BOT") if ENVIRONMENT == 'production' else os.getenv("TEST_NAME_BOT")

# ID админов
ADMIN_IDS = os.getenv('ADMIN_IDS').split(',')

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


REDIRECT_URI = os.getenv('Redirect_Uri')  # ссылка на сайт
CLIENT_ID = os.getenv('ClientId')  # получен при создании приложения
CLIENT_SECRET = os.getenv('ClientSecret')  # получен при создании приложения
AUTH_Token = os.getenv('Auth_token')
SUM_PAY = os.getenv('SumPay')


# ЮКАССА
YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY')
RETURN_URL = os.getenv('RETURN_URL')


# ПЕРЕМЕННЫЙ ПУТЕЙ
# Абсолютный путь к папке config_project
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))  # .../VPN_Bot/config_project
# Абсолютный путь к корню проекта (VPN_Bot) — поднимаемся на уровень выше
BASE_DIR = os.path.dirname(CONFIG_DIR)                  # .../VPN_Bot
# Путь к папке src
SRC_DIR = os.path.join(BASE_DIR, "src")                 # .../VPN_Bot/src
# Путь к папке media
MEDIA_DIR = os.path.join(SRC_DIR, "media")              # .../VPN_Bot/src/media
# Путь к папке c Бэкап БД
BACK_UP_DB = SRC_DIR = os.path.join(BASE_DIR, "copy_db_vpn")