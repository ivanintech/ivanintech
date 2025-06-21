import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

# import emails  # type: ignore <-- Temporarily commented out
# import jwt <-- Removed/Commented (jose is already used)
from jose import jwt, JWTError # <-- Make sure to use jose
from jinja2 import Template
# from jwt.exceptions import InvalidTokenError <-- No longer used

from app.core import security
from app.core.config import settings
from fastapi_mail import FastMail, MessageSchema
import httpx
from PIL import Image
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}


def is_valid_url(url: Optional[str]) -> bool:
    """Check if the URL is valid and uses http or https scheme."""
    if not url:
        return False
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except ValueError:
        return False

def parse_datetime_flexible(date_str: Optional[str]) -> Optional[datetime]:
    """Tries to parse dates in several common ISO formats, returning None if it fails."""
    if not date_str:
        return None
    formats = [
        # ISO 8601 formats
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        # RFC 2822 format (e.g., 'Tue, 25 Jun 2024 10:00:00 GMT')
        "%a, %d %b %Y %H:%M:%S %Z",
        # Another common format
        "%Y-%m-%d %H:%M:%S%z",
    ]
    try:
        # Prefer fromisoformat for speed and standard compliance
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
    logger.warning(f"Could not parse date: {date_str}")
    return None


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        Path(__file__).parent.parent / "email-templates" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    # Temporarily commented out until email sending is implemented
    if not settings.emails_enabled:
         logger.warning("Email sending is disabled in settings.")
         print("--- EMAIL SEND ATTEMPT (disabled) ---")
         print(f"To: {email_to}")
         print(f"Subject: {subject}")
         print(f"HTML: {html_content[:100]}...")
         print("---------------------------------------")
         return
    
    logger.error("Actual email sending functionality is not yet implemented.")
    print("--- EMAIL SEND ATTEMPT (not implemented) ---")
    print(f"To: {email_to}")
    print(f"Subject: {subject}")
    print("---------------------------------------")
    # assert settings.emails_enabled, "no provided configuration for email variables"
    # message = emails.Message(
    #     subject=subject,
    #     html=html_content,
    #     mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    # )
    # smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    # if settings.SMTP_TLS:
    #     smtp_options["tls"] = True
    # elif settings.SMTP_SSL:
    #     smtp_options["ssl"] = True
    # if settings.SMTP_USER:
    #     smtp_options["user"] = settings.SMTP_USER
    # if settings.SMTP_PASSWORD:
    #     smtp_options["password"] = settings.SMTP_PASSWORD
    # response = message.send(to=email_to, smtp=smtp_options)
    # logger.info(f"send email result: {response}")


async def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Recuperación de contraseña para {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": project_name,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html_content,
        subtype="html"
    )

    conf = settings.fm_connection_config
    fm = FastMail(conf)
    
    # This should be run in a background task
    try:
        await fm.send_message(message)
        logger.info(f"Password reset email sent successfully to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email_to}: {e}", exc_info=True)


def generate_test_email(email_to: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.FRONTEND_HOST,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        # Use jose.jwt.decode
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return str(decoded_token["sub"])
    except JWTError: # Use JWTError
        logger.error("Error verifying reset token", exc_info=True)
        return None


async def is_valid_image_url(url: str, min_size: int = 100) -> bool:
    """
    Checks if a URL points to a valid image that meets minimum size requirements.
    """
    if not url or not url.startswith(('http://', 'https://')):
        return False
    
    try:
        async with httpx.AsyncClient(headers=BROWSER_HEADERS, timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                logger.warning(f"Image URL returned status {response.status_code}: {url}")
                return False

            # 2. Check if the content type is an image
            content_type = response.headers.get("content-type", "").lower()
            if not content_type.startswith("image/"):
                logger.debug(f"Image check failed for {url}: Not an image content type ({content_type})")
                return False

            # 3. Check if the content length is reasonable (e.g., > 2KB)
            content_length = int(response.headers.get("content-length", 0))
            if content_length > 0 and content_length < 2048: # Greater than 0, less than 2KB
                logger.debug(f"Image check failed for {url}: Image too small ({content_length} bytes)")
                return False
            
            # If Content-Length is 0 or missing, we can be lenient or strict.
            # For now, we'll allow it if the content-type is correct.

            return True
    except httpx.RequestError as e:
        logger.warning(f"Could not validate image URL {url} due to a request error: {e}")
        return False # Treat network errors as invalid
    except Exception as e:
        logger.error(f"An unexpected error occurred while validating image URL {url}: {e}", exc_info=True)
        return False
