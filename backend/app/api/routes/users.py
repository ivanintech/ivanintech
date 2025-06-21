from typing import Any, List
import uuid
import os
from pathlib import Path

from fastapi import APIRouter, Body, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError # To catch unique constraint violations

from app import crud, schemas
from app.api import deps
from app.core.config import settings
from app.db import models
from app.utils import send_email, generate_new_account_email
from app.core import security

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", dependencies=[Depends(deps.get_current_active_superuser)], response_model=schemas.User)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = await crud.user.create(db, obj_in=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user

@router.post("/open", response_model=schemas.User)
async def create_user_open(
    *,
    db: AsyncSession = Depends(deps.get_db),
    password: str = Body(...),
    email: str = Body(...),
    full_name: str = Body(None),
    avatar_url: str = Body(None),
    website_url: str = Body(None),
) -> Any:
    """
    Create new user without needing authentication.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = await crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user_in = schemas.UserCreate(
        password=password, 
        email=email, 
        full_name=full_name, 
        avatar_url=avatar_url,
        website_url=website_url,
    )
    user = await crud.user.create(db, obj_in=user_in)
    return user

@router.post("/upload-avatar", response_model=schemas.UserWithAvatar)
async def upload_avatar(
    file: UploadFile = File(...),
    # TODO: Proteger este endpoint y requerir un usuario autenticado.
    # current_user: models.User = Depends(deps.get_current_active_user),
):
    """
    Upload an avatar image.
    This endpoint saves the file to the server and returns the URL.
    The database update should be handled separately.
    """
    # Verificamos que sea una imagen
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo subido no es una imagen.")

    # Define el directorio de subida
    upload_dir = Path("app/static/avatars")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Genera un nombre de archivo único para evitar colisiones
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Guarda el archivo nuevo de forma asíncrona
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        # Si algo sale mal, devuelve un error 500.
        raise HTTPException(status_code=500, detail=f"No se pudo guardar el archivo: {e}")
        
    # Devuelve la URL pública para acceder al archivo
    avatar_url = f"/static/avatars/{unique_filename}"
    
    return schemas.UserWithAvatar(avatar_url=avatar_url)

@router.patch("/me/avatar", response_model=schemas.User)
async def update_user_avatar(
    *,
    db: AsyncSession = Depends(deps.get_db),
    avatar_in: schemas.UserWithAvatar,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current user's avatar.
    """
    user = await crud.user.update(db, db_obj=current_user, obj_in={"avatar_url": str(avatar_in.avatar_url)})
    return user

@router.patch("/me", response_model=schemas.User)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    # Filtramos los valores nulos para no sobreescribir campos existentes con nada
    update_data = user_in.model_dump(exclude_unset=True)
    
    # Convertir HttpUrl a string para compatibilidad con la DB
    if "website_url" in update_data and update_data["website_url"]:
        update_data["website_url"] = str(update_data["website_url"])
    if "avatar_url" in update_data and update_data["avatar_url"]:
        update_data["avatar_url"] = str(update_data["avatar_url"])

    # Si se está actualizando la contraseña, hay que hashearla
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = security.get_password_hash(update_data["password"])
        del update_data["password"] # No queremos guardar la contraseña en texto plano

    user = await crud.user.update(db, db_obj=current_user, obj_in=update_data)
    return user

# You might want to add other user-related endpoints here later, e.g.:
# - Get current user (already in login.py as test-token, but could be /users/me)
# - Get user by ID (for admins)
# - Update user
# - Delete user (for admins)

# Example of a protected route to get current user details
# @router.get("/me", response_model=User)
# async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]) -> Any:
#     """
#     Get current user.
#     """
#     return current_user 