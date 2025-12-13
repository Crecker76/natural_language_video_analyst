import uuid

from sqlalchemy.orm import registry, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Index, func, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import uuid4

# Новый способ объявления Base в SQLAlchemy 2.0
reg = registry()
Base = reg.generate_base()


class Creators(Base):
    __tablename__ = 'creators'

    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    date_registration: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    name: Mapped[str] = mapped_column(String, default='unknown', nullable=False)

    # Связь один-ко-многим
    videos: Mapped[list["Videos"]] = relationship(
        "Videos",
        back_populates="creator",
        cascade="all, delete-orphan"
    )


class Videos(Base):
    __tablename__ = 'videos'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('creators.creator_id', ondelete='CASCADE'),
        nullable=False
    )
    video_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    views_count: Mapped[int] = mapped_column(default=0, server_default='0', nullable=False)
    likes_count: Mapped[int] = mapped_column(default=0, server_default='0', nullable=False)
    comments_count: Mapped[int] = mapped_column(default=0, server_default='0', nullable=False)
    reports_count: Mapped[int] = mapped_column(default=0, server_default='0', nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Обратные связи
    creator: Mapped["Creators"] = relationship("Creators", back_populates="videos")
    snapshots: Mapped[list["VideoSnapshots"]] = relationship(
        "VideoSnapshots",
        back_populates="video",
        cascade="all, delete-orphan",
        order_by="desc(VideoSnapshots.created_at)"
    )


class VideoSnapshots(Base):
    __tablename__ = 'video_snapshots'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('videos.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    views_count: Mapped[int] = mapped_column(nullable=False)
    likes_count: Mapped[int] = mapped_column(nullable=False)
    comments_count: Mapped[int] = mapped_column(nullable=False)
    reports_count: Mapped[int] = mapped_column(nullable=False)

    delta_views_count: Mapped[int] = mapped_column(default=0, nullable=False)
    delta_likes_count: Mapped[int] = mapped_column(default=0, nullable=False)
    delta_comments_count: Mapped[int] = mapped_column(default=0, nullable=False)
    delta_reports_count: Mapped[int] = mapped_column(default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    video: Mapped["Videos"] = relationship("Videos", back_populates="snapshots")
