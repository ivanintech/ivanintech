from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.contact import ContactMessage
from app.schemas.contact import ContactForm, ContactUpdate
from app.crud.base import CRUDBase


class CRUDContactMessage(CRUDBase[ContactMessage, ContactForm, ContactUpdate]):
    # El CRUDBase genérico es suficiente para este modelo simple.
    # Se pueden añadir métodos específicos si es necesario en el futuro.
    pass


contact_message = CRUDContactMessage(ContactMessage) 