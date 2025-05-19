from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.schemas import Message, NewPassword, User, UserCreate
from app.schemas.token import Token, TokenResponse
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
) -> TokenResponse:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user_db = await crud.user.authenticate_user(
        db=session, email=form_data.username, password=form_data.password
    )
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    if not user_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user_db.id, expires_delta=access_token_expires
    )

    user_schema = User.from_orm(user_db)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_schema
    )


@router.post("/users/open", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    session: SessionDep,
    user_in: UserCreate
) -> Any:
    """
    Create new user without needing authentication.
    Used for signup.
    """
    user = await crud.user.get_user_by_email(db=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    # Si full_name es una cadena vacía en user_in, convertirlo a None antes de crear
    if hasattr(user_in, 'full_name') and user_in.full_name == "":
        user_in.full_name = None
        
    new_user = await crud.user.create_user(db=session, user_in=user_in)
    return new_user


@router.post("/login/test-token", response_model=User)
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
