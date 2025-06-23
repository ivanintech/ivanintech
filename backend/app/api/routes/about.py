from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.api import deps
from app.db import models

router = APIRouter()

@router.get("/", response_model=List[schemas.AboutMedia])
def read_about_media_items(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve active about media items.
    """
    about_media_items = crud.about_media.get_multi(db, skip=skip, limit=limit, sort_by="order")
    return [item for item in about_media_items if item.is_active]

@router.post("/", response_model=schemas.AboutMedia)
def create_about_media_item(
    *,
    db: Session = Depends(deps.get_db),
    item_in: schemas.AboutMediaCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new about media item. Superuser only.
    """
    item = crud.about_media.create(db=db, obj_in=item_in)
    return item

@router.put("/{id}", response_model=schemas.AboutMedia)
def update_about_media_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    item_in: schemas.AboutMediaUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update an about media item. Superuser only.
    """
    item = crud.about_media.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="About media item not found")
    item = crud.about_media.update(db=db, db_obj=item, obj_in=item_in)
    return item

@router.delete("/{id}", response_model=schemas.AboutMedia)
def delete_about_media_item(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete an about media item. Superuser only.
    """
    item = crud.about_media.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="About media item not found")
    item = crud.about_media.remove(db=db, id=id)
    return item 