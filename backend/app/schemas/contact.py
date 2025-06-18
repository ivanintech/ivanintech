from pydantic import BaseModel, EmailStr

# Schema for the incoming contact form data
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str

# Schema for updating a contact message (could be empty if not needed)
class ContactUpdate(BaseModel):
    pass

# Schema for the response after submitting the form
class ContactResponse(BaseModel):
    message: str 