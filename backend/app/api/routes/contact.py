from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import logging

from app.schemas.contact import ContactForm, ContactResponse
# from app.db.models.contact import ContactMessage # No longer used directly here
from app.api import deps  # Standardized dependency import
from app.core.config import settings
from app import crud # Import the crud module

router = APIRouter()

# Helper function to send email in the background
async def send_email_notification(subject: str, recipient: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=body,
        subtype="html"
    )
    
    # Get configuration
    conf = settings.fm_connection_config
    
    # Initialize FastMail with the settings configuration
    fm = FastMail(conf)
    
    try:
        await fm.send_message(message)
        logging.info(f"Email notification sent successfully to {recipient}")
    except Exception as e:
        logging.error(f"Failed to send email notification to {recipient}: {e}")

@router.post("/submit", response_model=ContactResponse)
async def submit_contact_form(
    contact_data: ContactForm,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Receives contact form data, saves it using CRUD, and sends an email notification.
    """
    try:
        # Call the CRUD function to create the message
        db_message = await crud.contact_message.create(db=db, obj_in=contact_data)
        
        # Send email in the background
        email_subject = f"New Contact Message from {contact_data.name} (ID: {db_message.id})"
        email_recipient = "info.ivanintech@gmail.com" # Your email
        email_body = f"""
        <p>You have received a new message from your website:</p>
        <ul>
            <li><b>Message ID:</b> {db_message.id}</li>
            <li><b>Name:</b> {db_message.name}</li>
            <li><b>Email:</b> {db_message.email}</li>
            <li><b>Date:</b> {db_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}</li>
        </ul>
        <p><b>Message:</b></p>
        <p>{db_message.message}</p>
        """
        
        background_tasks.add_task(
            send_email_notification,
            email_subject,
            email_recipient,
            email_body
        )

        return ContactResponse(message="Message received successfully.")

    except Exception as e:
        # db.rollback() # Rollback should be handled within CRUD if necessary or here if creation fails
        print(f"Error in contact submission route: {e}")
        # We could log the full error 'e' here
        raise HTTPException(
            status_code=500,
            detail="There was an error processing your message. Please try again later."
        )

# Potentially add extra validation or rate limiting here 