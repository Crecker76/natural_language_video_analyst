from abc import ABC, abstractmethod

from config_project.constants import (
    USER_NAME_DB, PASSWORD_DB, PORT_DB, NAME_DB,
    LOCAL_DB_USER_NAME, LOCAL_DB_PASSWORD
)


class DatabaseConfigInterface(ABC):
    def __init__(self):
        self.user_name = USER_NAME_DB
        self.password = PASSWORD_DB
        self.port = PORT_DB
        self.name = NAME_DB

    @abstractmethod
    def get_database_uri(self):
        pass


class LocalDatabaseConfig(DatabaseConfigInterface):
    """Класс для подключения к локальной БД"""
    def __init__(self):
        super().__init__()
        self.user_name = LOCAL_DB_USER_NAME
        self.password = LOCAL_DB_PASSWORD

    def get_database_uri(self):
        return f'postgresql://{self.user_name}:{self.password}@localhost:{self.port}/{self.name}'


class ContainerDatabaseConfig(DatabaseConfigInterface):
    """Класс для подключения к БД в контейнере"""

    def __init__(self):
        super().__init__()
        self.user_name = USER_NAME_DB
        self.password = PASSWORD_DB

    def get_database_uri(self):
        return f'postgresql://{self.user_name}:{self.password}@db:{self.port}/{self.name}'
