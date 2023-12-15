from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import TIMESTAMP, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.database import Base

if TYPE_CHECKING:
    from app.infrastructure.db.models.tags import Tag
    from app.infrastructure.db.models.users import User


class Post(Base):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('account.id'))
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    published: Mapped[bool] = mapped_column(Boolean, default=True)
    user: Mapped['User'] = relationship(back_populates='posts')
    tags: Mapped[List['Tag']] = relationship(
        'Tag',
        secondary='post_tag',
        back_populates='posts',
    )

    def __repr__(self):
        return f'Object: [id: {self.id}, name:{self.title}]'
