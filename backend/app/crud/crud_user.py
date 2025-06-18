from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, Any

from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(select(self.model).filter(self.model.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = self.model(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not user.is_active:
            # Allowing inactive users to authenticate could be a security risk
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_by_id(self, db: AsyncSession, *, user_id: int | str) -> Optional[User]:
        if isinstance(user_id, str):
            try:
                user_id = int(user_id)
            except ValueError:
                return None
        return await db.get(User, user_id)

    async def get_first_superuser(self, db: AsyncSession) -> Optional[User]:
        """Retrievels the first active superuser found."""
        stmt = select(self.model).filter(self.model.is_superuser == True, self.model.is_active == True).limit(1)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def update(self, db: AsyncSession, *, db_obj: User, obj_in: UserUpdate | dict[str, Any]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
            
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

user = CRUDUser(User)

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