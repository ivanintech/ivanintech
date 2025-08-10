from fastapi import APIRouter, Depends, File, UploadFile
from pydantic.networks import EmailStr
import uuid
import os
import logging

from app.api.deps import get_current_active_superuser
from app.schemas import Message
from app.utils import generate_test_email, send_email
from app.core.config import settings

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
def health_check() -> bool:
    return True


@router.post("/upload-hero-media/")
async def upload_hero_media_file(file: UploadFile = File(...)):
    """
    Upload a hero media file (image or video).
    Stores it in the static/hero_media directory.
    """
    # Ensure the upload directory exists
    upload_dir = os.path.join(settings.STATIC_DIR, "hero_media")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate a unique filename
    extension = file.filename.split(".")[-1]
    unique_id = uuid.uuid4()
    filename = f"{unique_id}.{extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    # Return the relative URL
    return {"media_url": f"/static/hero_media/{filename}"}


@router.get("/scheduler/status")
async def get_scheduler_status():
    """
    Get the current status of the APScheduler and its jobs.
    """
    try:
        # Importar el scheduler desde main
        from app.main import scheduler
        
        if not scheduler:
            return {
                "status": "not_initialized",
                "message": "Scheduler not available"
            }
        
        # Obtener información de los jobs
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
                "func_name": job.func.__name__ if hasattr(job.func, '__name__') else str(job.func)
            })
        
        return {
            "status": "running" if scheduler.running else "stopped",
            "job_count": len(jobs),
            "jobs": jobs,
            "scheduler_state": scheduler.state
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error retrieving scheduler status: {str(e)}"
        }
