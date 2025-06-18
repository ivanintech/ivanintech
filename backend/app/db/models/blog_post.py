from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional
from datetime import date
from uuid import uuid4

from app.db.base_class import Base

class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    title = Column(String, index=True, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    published_date: Mapped[date] = mapped_column(Date, nullable=False)
    last_modified_date: Mapped[Optional[date]] = mapped_column(Date, onupdate=date.today, nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    linkedin_post_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='published', index=True)

    author = relationship("User", back_populates="blog_posts")
    # category: Mapped[Optional[str]] = mapped_column(String(100)) 