from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError # To catch unique constraint violations

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.schemas.user import User, UserCreate

router = APIRouter()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    *, 
    session: SessionDep, 
    user_in: UserCreate
) -> Any:
    """
    Create new user.
    """
    existing_user = await crud.user.get_user_by_email(db=session, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    try:
        user = await crud.user.create_user(db=session, user_in=user_in)
    except IntegrityError: # Should be redundant if email check above works, but good for other constraints
        await session.rollback() # Rollback the session in case of other integrity errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error. Perhaps the email was registered concurrently.",
        )
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