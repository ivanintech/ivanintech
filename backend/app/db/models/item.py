from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True, index=True) # Mantenemos Integer
    title = Column(String(255), index=True, nullable=False)
    description = Column(String(255), nullable=True)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)

    # Relación (si se usa User):
    # owner = relationship("User", back_populates="items") 