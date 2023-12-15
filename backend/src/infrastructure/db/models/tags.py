from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.database import Base

if TYPE_CHECKING:
    from infrastructure.db.models.posts import Post
    from infrastructure.db.models.users import User


class Tag(Base):
    __tablename__ = 'tag'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('account.id'))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    user: Mapped['User'] = relationship(back_populates='tags')
    posts: Mapped[List['Post']] = relationship(
        secondary='post_tag',
        back_populates='tags',
    )

    def __repr__(self):
        return f'Object: [id: {self.id}, name:{self.name}]'


class PostTag(Base):
    __tablename__ = 'post_tag'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('post.id'))
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tag.id'))

    def __repr__(self):
        return f'Object: [post_id: {self.post_id}, tag_id:{self.tag_id}]'
