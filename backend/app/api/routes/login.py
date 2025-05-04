from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.schemas import Message, NewPassword, Token, User
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
async def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # TODO: Implementar crud.authenticate y lógica de usuario real
    # user = await crud.user.authenticate( # Necesitaremos crud.user
    #     db=session, email=form_data.username, password=form_data.password
    # )
    # Placeholder - Simular éxito temporalmente para arrancar
    user_id_placeholder = 1 
    print(f"LOGIN ATTEMPT: User={form_data.username} Pass={form_data.password[:3]}... ")
    # if not user:
    #     raise HTTPException(status_code=400, detail="Incorrect email or password")
    # elif not user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user_id_placeholder, expires_delta=access_token_expires # Usar placeholder ID
        )
    )


@router.post("/login/test-token", response_model=User) # Usar schema User
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    # Esto fallará hasta que get_current_user en deps.py pueda obtener un usuario real
    return current_user


@router.post("/password-recovery/{email}")
async def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery - REQUIRES IMPLEMENTATION
    """
    # user = await crud.user.get_by_email(db=session, email=email)
    raise HTTPException(status_code=501, detail="Not implemented yet") # Temporal
    # ... (resto de la lógica original comentada o eliminada) ...
    # return Message(message="Password recovery email sent")


@router.post("/reset-password/")
async def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password - REQUIRES IMPLEMENTATION
    """
    raise HTTPException(status_code=501, detail="Not implemented yet") # Temporal
    # ... (resto de la lógica original comentada o eliminada) ...
    # return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
async def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery - REQUIRES IMPLEMENTATION
    """
    raise HTTPException(status_code=501, detail="Not implemented yet") # Temporal
    # ... (resto de la lógica original comentada o eliminada) ...
    # return HTMLResponse(...) 
