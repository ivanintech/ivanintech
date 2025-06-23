import os
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.crud import hero_media as crud_hero_media
from app.schemas import HeroMediaCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# La ruta a la carpeta de medios, relativa a la ubicación del script en `backend/`
MEDIA_DIR = os.path.join(os.path.dirname(__file__), '../../../frontend/public/Heromedia')
BASE_URL = "/Heromedia"

async def seed_hero_media():
    db: AsyncSession = AsyncSessionLocal()
    
    logger.info(f"Checking for media files in: {os.path.abspath(MEDIA_DIR)}")

    if not os.path.isdir(MEDIA_DIR):
        logger.error(f"Media directory not found: {os.path.abspath(MEDIA_DIR)}")
        await db.close()
        return

    existing_items_result = await crud_hero_media.get_multi(db)
    existing_items = {item.media_url for item in existing_items_result}
    
    order_counter = len(existing_items)

    for filename in os.listdir(MEDIA_DIR):
        media_url = f"{BASE_URL}/{filename}"
        
        if media_url in existing_items:
            logger.info(f"Skipping existing media item: {filename}")
            continue

        name = os.path.splitext(filename)[0].replace('-', ' ').replace('_', ' ').title()
        extension = os.path.splitext(filename)[1].lower()
        
        media_type = 'video' if extension in ['.mp4', '.webm', '.mov'] else 'image'

        media_item_in = HeroMediaCreate(
            name=name,
            media_type=media_type,
            media_url=media_url,
            order=order_counter,
            is_active=True
        )
        
        await crud_hero_media.create(db, obj_in=media_item_in)
        logger.info(f"Added new hero media: {name}")
        order_counter += 1

    await db.close()

if __name__ == "__main__":
    logger.info("Starting hero media seeding...")
    asyncio.run(seed_hero_media())
    logger.info("Hero media seeding finished.") 