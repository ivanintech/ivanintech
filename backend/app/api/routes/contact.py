from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from app.schemas.contact import ContactForm, ContactResponse
# from app.db.models.contact import ContactMessage # Ya no se usa directamente aquí
from app.db.session import get_db
from app.core.config import settings
from app import crud # Importar el módulo crud

router = APIRouter()

# Función auxiliar para enviar email en segundo plano
async def send_email_notification(subject: str, recipient: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[recipient],
        body=body,
        subtype="html"
    )
    
    # Obtener configuración
    conf = settings.fm_connection_config
    
    # --- Debug Logs --- 
    print("--- Email Config Debug ---")
    print(f"MAIL_USERNAME: {conf.MAIL_USERNAME}")
    print(f"MAIL_PASSWORD set: {'Yes' if conf.MAIL_PASSWORD else 'No'} (Length: {len(conf.MAIL_PASSWORD) if conf.MAIL_PASSWORD else 0})") # No imprimir la contraseña real
    print(f"MAIL_FROM: {conf.MAIL_FROM}")
    print(f"MAIL_SERVER: {conf.MAIL_SERVER}")
    print(f"MAIL_PORT: {conf.MAIL_PORT}")
    print(f"MAIL_STARTTLS: {conf.MAIL_STARTTLS}")
    print(f"MAIL_SSL_TLS: {conf.MAIL_SSL_TLS}")
    print(f"USE_CREDENTIALS: {conf.USE_CREDENTIALS}")
    print("-------------------------")
    # --- Fin Debug Logs ---

    # Inicializar FastMail con la configuración de settings
    fm = FastMail(conf)
    
    try:
        await fm.send_message(message)
        print(f"Email notification sent successfully to {recipient}")
    except Exception as e:
        print(f"Failed to send email notification to {recipient}: {e}")
        # Considerar reintentar o loggear más detalladamente

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
        # Llamar a la función CRUD para crear el mensaje
        db_message = crud.contact.create_contact_message(db=db, contact_data=contact_data)
        
        # Enviar email en segundo plano
        email_subject = f"Nuevo Mensaje de Contacto de {contact_data.name} (ID: {db_message.id})"
        email_recipient = "info.ivancm@gmail.com" # Tu correo
        email_body = f"""
        <p>Has recibido un nuevo mensaje desde tu web:</p>
        <ul>
            <li><b>ID Mensaje:</b> {db_message.id}</li>
            <li><b>Nombre:</b> {db_message.name}</li>
            <li><b>Email:</b> {db_message.email}</li>
            <li><b>Fecha:</b> {db_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}</li>
        </ul>
        <p><b>Mensaje:</b></p>
        <p>{db_message.message}</p>
        """
        
        background_tasks.add_task(
            send_email_notification,
            email_subject,
            email_recipient,
            email_body
        )

        return ContactResponse(message="Mensaje recibido correctamente.")

    except Exception as e:
        # db.rollback() # El rollback debería manejarse dentro de CRUD si es necesario o aquí si la creación falla
        print(f"Error in contact submission route: {e}")
        # Podríamos loggear el error 'e' completo aquí
        raise HTTPException(
            status_code=500,
            detail="Hubo un error al procesar tu mensaje. Inténtalo de nuevo más tarde."
        )

# Potencialmente añadir validación extra o rate limiting aquí 