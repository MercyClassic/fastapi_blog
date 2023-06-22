from datetime import datetime
from src.db.database import Base
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Integer,
    TIMESTAMP,
    Boolean,
)


class Post(Base):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('account.id'))
    user = relationship('User', back_populates='posts')
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    published: Mapped[bool] = mapped_column(Boolean, default=True)

    tags = relationship('Tag', secondary='post_tag', back_populates='posts')


class Tag(Base):
    __tablename__ = 'tag'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)

    posts = relationship('Post', secondary='post_tag', back_populates='tags')


class PostTag(Base):
    __tablename__ = 'post_tag'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('post.id'))
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tag.id'))
