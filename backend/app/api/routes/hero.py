from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.db import models
from app import schemas
from fastapi import status

router = APIRouter()

@router.get("/", response_model=List[schemas.HeroMedia])
def read_hero_media_entries(
    db: deps.SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve active hero media items.
    """
    hero_media_items = crud.hero_media.get_multi(db, skip=skip, limit=limit, sort_by="order")
    return [item for item in hero_media_items if item.is_active]

@router.post("/", response_model=schemas.HeroMedia, status_code=status.HTTP_201_CREATED)
def create_hero_media_entry(
    *,
    db: deps.SessionDep,
    hero_media_in: schemas.HeroMediaCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new hero media item. Superuser only.
    """
    item = crud.hero_media.create(db=db, obj_in=hero_media_in)
    return item

@router.put("/{media_id}", response_model=schemas.HeroMedia)
def update_hero_media_entry(
    *,
    db: deps.SessionDep,
    media_id: int,
    hero_media_in: schemas.HeroMediaUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a hero media item. Superuser only.
    """
    item = crud.hero_media.get(db=db, id=media_id)
    if not item:
        raise HTTPException(status_code=404, detail="Hero media item not found")
    item = crud.hero_media.update(db=db, db_obj=item, obj_in=hero_media_in)
    return item

@router.delete("/{media_id}", response_model=schemas.HeroMedia)
def delete_hero_media_entry(
    *,
    db: deps.SessionDep,
    media_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a hero media item. Superuser only.
    """
    item = crud.hero_media.get(db=db, id=media_id)
    if not item:
        raise HTTPException(status_code=404, detail="Hero media item not found")
    item = crud.hero_media.remove(db=db, id=media_id)
    return item 