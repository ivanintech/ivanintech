from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.api import deps
from app.db import models
from fastapi import status

router = APIRouter()

@router.get("/", response_model=List[schemas.AboutMedia])
def read_about_media_entries(
    db: deps.SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve active about media items.
    """
    about_media_items = crud.about_media.get_multi(db, skip=skip, limit=limit, sort_by="order")
    return [item for item in about_media_items if item.is_active]

@router.post("/", response_model=schemas.AboutMedia, status_code=status.HTTP_201_CREATED)
def create_about_media_entry(
    *,
    db: deps.SessionDep,
    about_media_in: schemas.AboutMediaCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new about media item. Superuser only.
    """
    item = crud.about_media.create(db=db, obj_in=about_media_in)
    return item

@router.put("/{media_id}", response_model=schemas.AboutMedia)
def update_about_media_entry(
    *,
    db: deps.SessionDep,
    media_id: int,
    about_media_in: schemas.AboutMediaUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update an about media item. Superuser only.
    """
    item = crud.about_media.get(db=db, id=media_id)
    if not item:
        raise HTTPException(status_code=404, detail="About media item not found")
    item = crud.about_media.update(db=db, db_obj=item, obj_in=about_media_in)
    return item

@router.delete("/{media_id}", response_model=schemas.AboutMedia)
def delete_about_media_entry(
    *,
    db: deps.SessionDep,
    media_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete an about media item. Superuser only.
    """
    item = crud.about_media.get(db=db, id=media_id)
    if not item:
        raise HTTPException(status_code=404, detail="About media item not found")
    item = crud.about_media.remove(db=db, id=media_id)
    return item 