from typing import List
import subprocess
from datetime import datetime, timedelta
import os

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from loguru import logger

from src.database.engine import Session




def handle_sqlalchemy_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            with Session() as session:
                session.rollback()  # Откат транзакции
                logger.error(f"Ошибка в функции {func.__name__}: {e}")
                raise
    return wrapper
