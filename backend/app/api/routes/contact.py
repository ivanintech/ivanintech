from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import logging
from typing import Any

from app.schemas.contact import ContactForm, ContactResponse
from app.api import deps
from app.core.config import settings
from app import crud
from fastapi import status

router = APIRouter()

async def send_email_notification(subject: str, recipient: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=body,
        subtype="html"
    )
    
    conf = settings.fm_connection_config
    
    fm = FastMail(conf)
    
    try:
        await fm.send_message(message)
        logging.info(f"Email notification sent successfully to {recipient}")
    except Exception as e:
        logging.error(f"Failed to send email notification to {recipient}: {e}")

@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contact submission",
    response_description="A confirmation message.",
)
async def create_contact_submission(
    *,
    db: deps.SessionDep,
    submission_in: ContactForm,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Receives contact form data, saves it using CRUD, and sends an email notification.
    """
    try:
        db_message = await crud.contact_message.create(db=db, obj_in=submission_in)
        
        email_subject = f"New Contact Message from {submission_in.name} (ID: {db_message.id})"
        email_recipient = "info.ivanintech@gmail.com"
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
        logging.error(f"Error in contact submission route: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="There was an error processing your message. Please try again later."
        )

# Potentially add extra validation or rate limiting here 