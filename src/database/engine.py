from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config_project.config_db import LocalDatabaseConfig, ContainerDatabaseConfig
from config_project.constants import ENVIRONMENT

db_config = ContainerDatabaseConfig() if ENVIRONMENT in ['production', 'container'] else LocalDatabaseConfig()

# Создание соединения с базой данных
engine = create_engine(db_config.get_database_uri())

# Создание сессии для работы с базой данных
Session = sessionmaker(bind=engine)
