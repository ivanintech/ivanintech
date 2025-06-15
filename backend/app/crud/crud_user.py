from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.db.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password

async def get_user(db: AsyncSession, user_id: int | str) -> Optional[User]:
    if isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except ValueError:
            return None
    return await db.get(User, user_id)

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).filter(User.email == email)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_first_superuser(db: AsyncSession) -> Optional[User]:
    """Retrieves the first active superuser found."""
    stmt = select(User).filter(User.is_superuser == True, User.is_active == True).limit(1)
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_user(db: AsyncSession, *, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=getattr(user_in, 'full_name', None),
        is_active=getattr(user_in, 'is_active', True),
        is_superuser=getattr(user_in, 'is_superuser', False)
    )
    db.add(db_user)
    return db_user

async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> Optional[User]:
    user = await get_user_by_email(db, email=email)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# Add other CRUD functions as needed (e.g., update_user)
# Consider adding update_user for changing password or other attributes
# async def update_user(db: AsyncSession, *, db_user: User, user_in: UserUpdate) -> User:
#     user_data = user_in.model_dump(exclude_unset=True)
#     if "password" in user_data and user_data["password"]:
#         hashed_password = get_password_hash(user_data["password"])
#         del user_data["password"] # remove plain password
#         db_user.hashed_password = hashed_password
#     for field, value in user_data.items():
#         setattr(db_user, field, value)
#     db.add(db_user)
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user 