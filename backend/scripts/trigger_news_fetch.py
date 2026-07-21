import asyncio
import logging
import sys
from pathlib import Path

# Add project root to PYTHONPATH
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))

from app.db.session import async_session_maker
from app.services.aggregated_news_service import fetch_and_store_news
from app.core.config import settings
from app import crud

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("news_trigger")

async def trigger_fetch():
    logger.info("Initializing news fetch with NEW sources...")
    print(f"DEBUG: Using database URI: {settings.SQLALCHEMY_DATABASE_URI}")
    print(f"DEBUG: FORCE_SQLITE: {settings.FORCE_SQLITE}")
    async with async_session_maker() as session:
        try:
            # Find superuser
            superuser = await crud.user.get_by_email(db=session, email=settings.FIRST_SUPERUSER)
            if not superuser:
                logger.error(f"Superuser {settings.FIRST_SUPERUSER} not found. Please run initial setup first.")
                return

            logger.info(f"Using superuser: {superuser.email}")
            
            # Run fetch
            # We pass the superuser as the requesting user
            await fetch_and_store_news(user=superuser)
            
            logger.info("✅ News fetch and storage completed successfully.")
            
        except Exception as e:
            logger.error(f"Failed to trigger news fetch: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(trigger_fetch())
