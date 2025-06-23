import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.crud import about_media as crud_about_media
from app.schemas import AboutMediaCreate

# Add backend to sys.path
# This helps in running the script directly for simple cases.
# However, running with `python -m app.scripts.seed_about_media` is more robust.
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))


def seed_about_media(db: Session) -> None:
    """
    Populates the about_media table with images from the specified directory.
    """
    image_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "img"
    
    if not image_dir.is_dir():
        print(f"Directory not found: {image_dir}")
        return

    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    
    existing_media = crud_about_media.get_multi(db, limit=1000)
    existing_urls = {item.media_url for item in existing_media}
    
    print(f"Found {len(existing_urls)} existing media items in the database.")
    
    order_start = len(existing_urls)
    
    files_to_add = [
        f for f in sorted(image_dir.iterdir()) 
        if f.is_file() and f.suffix.lower() in allowed_extensions
    ]
    
    print(f"Found {len(files_to_add)} image files in the directory.")

    for i, file_path in enumerate(files_to_add):
        media_url = f"/img/{file_path.name}"
        
        if media_url not in existing_urls:
            print(f"Preparing to add: {file_path.name}")
            item_in = AboutMediaCreate(
                name=file_path.stem.replace("-", " ").title(),
                media_url=media_url,
                order=order_start + i,
                is_active=True
            )
            crud_about_media.create(db, obj_in=item_in)
            print(f"Successfully added: {file_path.name}")
        else:
            print(f"Skipping, already exists: {file_path.name}")

if __name__ == "__main__":
    print("Starting about media seeding...")
    db = SessionLocal()
    try:
        seed_about_media(db)
        print("Committing changes to the database.")
        db.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        print("Closing database session.")
        db.close()
    print("About media seeding finished.") 