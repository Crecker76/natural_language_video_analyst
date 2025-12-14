import re

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text


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


@handle_sqlalchemy_error
def direct_sql_requests(sql_query:str):
    """Прямые SQL запросы к БД"""

    try:
        sql_query = re.sub(r'^```sql|```$', '', sql_query, flags=re.IGNORECASE).strip()
        with Session() as session:
            result = session.execute(text(sql_query))
            scalar_result = result.scalar()
            return scalar_result
    except Exception:
        logger.exception('Ошибка при sql запросе')
