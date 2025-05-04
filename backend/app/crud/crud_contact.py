from sqlalchemy.orm import Session

from app.db.models.contact import ContactMessage
from app.schemas.contact import ContactForm


def create_contact_message(db: Session, *, contact_data: ContactForm) -> ContactMessage:
    """Creates a new contact message in the database."""
    db_message = ContactMessage(
        name=contact_data.name,
        email=contact_data.email,
        message=contact_data.message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message) # Refresh para obtener ID y created_at generados por la BD
    return db_message 