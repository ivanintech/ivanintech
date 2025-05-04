from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.db.models.user import User
# Assuming you have a UserCreate and UserUpdate schema
# from app.schemas.user import UserCreate, UserUpdate

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
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

# Add other CRUD functions as needed (create_user, update_user, etc.)
# Example:
# async def create_user(db: AsyncSession, *, user_in: UserCreate) -> User:
#     # Remember to hash the password before saving
#     hashed_password = get_password_hash(user_in.password) 
#     db_user = User(
#         email=user_in.email,
#         hashed_password=hashed_password,
#         full_name=user_in.full_name,
#         is_superuser=user_in.is_superuser # Or set default based on logic
#     )
#     db.add(db_user)
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user 