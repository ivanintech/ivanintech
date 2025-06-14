from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func, UniqueConstraint, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base_class import Base
import enum
from datetime import datetime

class VoteType(enum.Enum):
    like = "like"
    dislike = "dislike"

class ResourceVote(Base):
    __tablename__ = 'resource_votes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    resource_link_id: Mapped[str] = mapped_column(ForeignKey('resource_links.id'), nullable=False)
    
    vote_type: Mapped[VoteType] = mapped_column(SQLAlchemyEnum(VoteType), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user = relationship("User", back_populates="votes")
    resource_link = relationship("ResourceLink", back_populates="votes")

    __table_args__ = (
        UniqueConstraint('user_id', 'resource_link_id', name='_user_resource_uc'),
    )

    def __repr__(self):
        return f"<ResourceVote(user_id={self.user_id}, resource_id={self.resource_link_id}, type='{self.vote_type.name}')>"
