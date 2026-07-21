import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.db.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def seed():
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == settings.FIRST_SUPERUSER))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"Creating superuser: {settings.FIRST_SUPERUSER}")
            user = User(
                email=settings.FIRST_SUPERUSER,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_superuser=True,
                is_active=True,
                full_name="Admin"
            )
            session.add(user)
            await session.commit()
            print("Superuser created successfully.")
        else:
            print("Superuser already exists.")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
