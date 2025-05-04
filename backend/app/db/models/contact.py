from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base # <-- Corregido

class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String) # Considerar index=True si se busca por email
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 