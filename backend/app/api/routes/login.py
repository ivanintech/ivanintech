from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.db import models
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
    send_reset_password_email,
)
from app.schemas.token import LoginResponse, Token, SocialToken, SocialCode
from app.crud import crud_user
from app.db.models.user import User

# --- Imports para Social Login ---
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import httpx
import secrets

router = APIRouter()


@router.post("/login/access-token", response_model=LoginResponse)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Crear el token de acceso
    access_token = security.create_access_token(
            user.id, expires_delta=access_token_expires
    )
    
    # Devolver el token y los datos del usuario
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.get("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email:path}", response_model=schemas.msg.Message)
async def recover_password(
    email: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Password Recovery
    """
    user = await crud.user.get_by_email(db, email=email)

    if user:
        password_reset_token = generate_password_reset_token(email=email)
        background_tasks.add_task(
            send_reset_password_email,
            email_to=user.email,
            email=email,
            token=password_reset_token,
        )

    return {"message": "If an account with this email exists, a password recovery email has been sent."}


@router.post("/reset-password/", response_model=schemas.msg.Message)
async def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # La función `crud.user.update` se encargará de hashear la contraseña.
    # Le pasamos la nueva contraseña en texto plano.
    await crud.user.update(db, db_obj=user, obj_in={"password": new_password})
    
    return {"message": "Password updated successfully"}


# --- Endpoint para Google Social Login ---
@router.post("/login/google", response_model=LoginResponse)
async def login_google(
    *,
    social_token: SocialToken,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    OAuth2 flow para Google.
    Verifica el token de ID de Google, crea un usuario si no existe,
    y devuelve un token de acceso de nuestra aplicación.
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500, detail="La configuración de Google Client ID no está disponible."
        )

    try:
        # Verificar el token de ID recibido desde el frontend
        id_info = id_token.verify_oauth2_token(
            social_token.token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )

        # Extraer email del token verificado
        email = id_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="No se pudo obtener el email del token de Google.")

    except ValueError as e:
        # El token es inválido
        raise HTTPException(status_code=403, detail=f"Token de Google inválido: {e}")

    # Buscar si el usuario ya existe en nuestra BD
    user = await crud_user.get_by_email(db, email=email)

    if not user:
        # Si el usuario no existe, lo creamos
        full_name = id_info.get("name")
        user_in = schemas.UserCreate(
            email=email,
            password=security.get_password_hash(secrets.token_urlsafe(16)), # Contraseña aleatoria segura
            full_name=full_name,
            is_active=True,
            is_verified=True, # Lo verificamos porque confiamos en Google
        )
        user = await crud_user.create(db, obj_in=user_in)

    # El usuario ya existe o acaba de ser creado. Generamos un token de nuestro sistema.
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "user": user}


# --- Endpoint para GitHub Social Login ---
@router.post("/login/github", response_model=LoginResponse)
async def login_github(
    *,
    social_code: SocialCode,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    OAuth2 flow para GitHub.
    Verifica el código de autorización, obtiene el token de acceso,
    obtiene la información del usuario, crea un usuario si no existe,
    y devuelve un token de acceso de nuestra aplicación.
    """
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=500, detail="La configuración de GitHub Client ID/Secret no está disponible."
        )

    # 1. Canjear el código por un token de acceso de GitHub
    token_url = "https://github.com/login/oauth/access_token"
    token_data = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": social_code.code,
    }
    headers = {"Accept": "application/json"}
    
    async with httpx.AsyncClient() as client:
        try:
            token_response = await client.post(token_url, json=token_data, headers=headers)
            token_response.raise_for_status()
            token_json = token_response.json()
            github_token = token_json.get("access_token")

            if not github_token:
                raise HTTPException(status_code=400, detail="No se pudo obtener el token de acceso de GitHub.")

            # 2. Usar el token de acceso para obtener la información del usuario
            user_url = "https://api.github.com/user"
            user_headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            user_response = await client.get(user_url, headers=user_headers)
            user_response.raise_for_status()
            user_info = user_response.json()
            
            email = user_info.get("email")

            # Si el email principal no es público, buscar en los emails del usuario
            if not email:
                emails_url = "https://api.github.com/user/emails"
                emails_response = await client.get(emails_url, headers=user_headers)
                emails_response.raise_for_status()
                emails_info = emails_response.json()
                
                primary_email_obj = next((e for e in emails_info if e["primary"] and e["verified"]), None)
                if primary_email_obj:
                    email = primary_email_obj["email"]
                else: # Fallback al primer email verificado si no hay primario
                    verified_email_obj = next((e for e in emails_info if e["verified"]), None)
                    if verified_email_obj:
                        email = verified_email_obj["email"]

            if not email:
                raise HTTPException(status_code=400, detail="No se pudo obtener un email verificado de GitHub.")

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error de comunicación con GitHub: {e.response.text}")

    # 3. Buscar si el usuario ya existe, si no, crearlo
    user = await crud_user.get_by_email(db, email=email)
    if not user:
        full_name = user_info.get("name") or user_info.get("login")
        user_in = schemas.UserCreate(
            email=email,
            password=security.get_password_hash(secrets.token_urlsafe(16)),
            full_name=full_name,
            is_active=True,
            is_verified=True, # Confiamos en GitHub
            github_username=user_info.get("login")
        )
        user = await crud_user.create(db, obj_in=user_in)
    
    # 4. Crear nuestro propio token de acceso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.post("/test-token", response_model=schemas.User)
def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user 