import datetime
from uuid import uuid4


from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, BOOLEAN, JSON, BIGINT, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base, backref


Base = declarative_base()


class User(Base):
    """
    Таблица пользователя

    Free_plan - Бесплатный период - True -доступен False -NO
    """

    __tablename__ = 'user'
    user_id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    date_registration: datetime.datetime = Column(DateTime, default=func.now())
    telegram_id: int = Column(BIGINT)
    name: str = Column(String, default='unknown')
