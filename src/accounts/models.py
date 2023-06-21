from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.database import Base
from sqlalchemy import (
    String,
    Integer,
    TIMESTAMP,
    Boolean
)


class User(Base):
    __tablename__ = 'account'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    password: Mapped[str] = mapped_column(String(1024), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # posts = relationship('Post', back_populates='user')
