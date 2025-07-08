from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional
from uuid import uuid4

from app.db.base_class import Base

class BlogSuggestion(Base):
    __tablename__ = "blog_suggestions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(Text)
    
    # Datos generados por IA para que el admin los revise
    excerpt: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[str]] = mapped_column(String(255))
    image_url: Mapped[Optional[str]] = mapped_column(String(512))
    
    # Estado de la sugerencia
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='pending', index=True) # pending, approved, rejected
    
    # Origen de la sugerencia (ej. 'gemini-automated', 'user-submission')
    source: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    processed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    # Relación con el post que se crea cuando se aprueba
    published_post_id: Mapped[Optional[str]] = mapped_column(ForeignKey("blog_posts.id"), nullable=True)
    published_post = relationship("BlogPost")

    suggested_by_email: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    def __repr__(self):
        return f"<BlogSuggestion(title='{self.title}', status='{self.status}')>" 