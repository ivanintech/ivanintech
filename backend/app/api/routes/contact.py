from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from app.schemas.contact import ContactForm, ContactResponse
# from app.db.models.contact import ContactMessage # No longer used directly here
from app.db.session import get_db
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
    
    # --- Debug Logs --- 
    print("--- Email Config Debug ---")
    print(f"MAIL_USERNAME: {conf.MAIL_USERNAME}")
    print(f"MAIL_PASSWORD set: {'Yes' if conf.MAIL_PASSWORD else 'No'} (Length: {len(conf.MAIL_PASSWORD) if conf.MAIL_PASSWORD else 0})") # Do not print the actual password
    print(f"MAIL_FROM: {conf.MAIL_FROM}")
    print(f"MAIL_SERVER: {conf.MAIL_SERVER}")
    print(f"MAIL_PORT: {conf.MAIL_PORT}")
    print(f"MAIL_STARTTLS: {conf.MAIL_STARTTLS}")
    print(f"MAIL_SSL_TLS: {conf.MAIL_SSL_TLS}")
    print(f"USE_CREDENTIALS: {conf.USE_CREDENTIALS}")
    print("-------------------------")
    # --- End Debug Logs ---

    # Initialize FastMail with the settings configuration
    fm = FastMail(conf)
    
    try:
        await fm.send_message(message)
        print(f"Email notification sent successfully to {recipient}")
    except Exception as e:
        print(f"Failed to send email notification to {recipient}: {e}")
        # Consider retrying or logging in more detail

@router.post("/submit", response_model=ContactResponse)
async def submit_contact_form(
    contact_data: ContactForm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Receives contact form data, saves it using CRUD, and sends an email notification.
    """
    try:
        # Call the CRUD function to create the message
        db_message = crud.contact.create_contact_message(db=db, contact_data=contact_data)
        
        # Send email in the background
        email_subject = f"New Contact Message from {contact_data.name} (ID: {db_message.id})"
        email_recipient = "info.ivancm@gmail.com" # Your email
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