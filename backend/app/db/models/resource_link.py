from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, List
import uuid
from datetime import datetime

from app.db.base_class import Base

class ResourceLink(Base):
    __tablename__ = "resource_links"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True, default=lambda: uuid.uuid4().hex)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    ai_generated_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    personal_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    tags: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    star_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    likes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dislikes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now)

    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True)
    author: Mapped["User"] = relationship("User", back_populates="resource_links")

    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    votes: Mapped[List["ResourceVote"]] = relationship("ResourceVote", back_populates="resource_link", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ResourceLink(title='{self.title}', url='{self.url}')>"