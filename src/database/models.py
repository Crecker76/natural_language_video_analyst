from datetime import datetime
from uuid import uuid4


from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, BOOLEAN, JSON, BIGINT, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base, backref


Base = declarative_base()


class Users(Base):
    """
    Таблица пользователя для бота
    """

    __tablename__ = 'users'
    user_id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    date_registration: datetime = Column(DateTime, default=func.now())
    telegram_id: int = Column(BIGINT)
    name: str = Column(String, default='unknown')


class Creators(Base):
    """Данные создателей контента"""

    __tablename__ = 'creators'
    creator_id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    date_registration: datetime = Column(DateTime, default=func.now())
    name: str = Column(String, default='unknown')

    # Обратная связь: список всех видео этого креатора
    videos = relationship("Videos", back_populates="creator", cascade="all, delete-orphan")


class Videos(Base):
    """
    Итоговая статистика по ролику

    id — идентификатор видео (UUID4);
    creator_id — идентификатор креатора;
    video_created_at — дата и время публикации видео;
    views_count — финальное количество просмотров;
    likes_count — финальное количество лайков;
    comments_count — финальное количество комментариев;
    reports_count — финальное количество жалоб;
    служебные поля:
        created_at - время создания статистики
        updated_at. - последнее время обновления статистики
    """
    __tablename__ = 'videos'

    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Внешний ключ на creator_id
    creator_id: UUID = Column(
        UUID(as_uuid=True),
        ForeignKey('creators.creator_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    video_created_at: datetime = Column(
        DateTime(timezone=True),
        default=func.now()
    )
    views_count: int = Column(Integer, nullable=False, default=0)
    likes_count: int = Column(Integer, nullable=False, default=0)
    comments_count: int = Column(Integer, nullable=False, default=0)
    reports_count: int = Column(Integer, nullable=False, default=0)

    created_at: datetime = Column(
        DateTime(timezone=True),
        default=func.now()
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        default=func.now()
    )

    # Обратная связь на создателя
    creator = relationship("Creators", back_populates="videos")


class VideoSnapshots(Base):
    """
    Почасовые замеры по ролику

    id — идентификатор снапшота;
    video_id — ссылка на соответствующее видео;
    текущие значения: views_count, likes_count, comments_count, reports_count на момент замера;
    приращения: delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count — насколько изменилось значение с прошлого замера;
    created_at — время замера (раз в час);
    updated_at — служебное поле.

    """

    __tablename__ = 'video_snapshots'

    id: UUID = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # связь с видео
    video_id: UUID = Column(
        UUID(as_uuid=True),
        ForeignKey('videos.id', ondelete='CASCADE'),
        nullable=False,
        index=True  # важно для быстрых запросов по видео
    )

    # Текущие абсолютные значения на момент замера
    views_count: int = Column(Integer, nullable=False)
    likes_count: int = Column(Integer, nullable=False)
    comments_count: int = Column(Integer, nullable=False)
    reports_count: int = Column(Integer, nullable=False)

    # Приращения с предыдущего снапшота (дельты)
    delta_views_count: int = Column(Integer, nullable=False, default=0)
    delta_likes_count: int = Column(Integer, nullable=False, default=0)
    delta_comments_count: int = Column(Integer, nullable=False, default=0)
    delta_reports_count: int = Column(Integer, nullable=False, default=0)

    # Время создания снапшота (момент замера, раз в час)
    created_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        index=True  # полезно для запросов по времени
    )

    # Служебное поле — время последнего обновления записи (на случай корректировок)
    updated_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now()
    )

    # Обратная связь к видео
    video = relationship("Videos", back_populates="snapshots")
