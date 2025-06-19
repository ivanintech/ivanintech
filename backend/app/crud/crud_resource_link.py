from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, func, case as sa_case
from sqlalchemy.orm import selectinload
from typing import List, Optional, Any
import logging
import uuid # To generate IDs if they don't come from the model, although our model does it by default
from datetime import datetime, timezone, timedelta
import sqlalchemy as sa

from app.db.models.resource_link import ResourceLink
from app.schemas.resource_link import ResourceLinkCreate, ResourceLinkUpdate
from app.crud.base import CRUDBase

logger = logging.getLogger(__name__)


class CRUDResourceLink(CRUDBase[ResourceLink, ResourceLinkCreate, ResourceLinkUpdate]):
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        resource_type: Optional[str] = None,
        tags_contain: Optional[List[str]] = None
    ) -> List[ResourceLink]:
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        is_new_case = sa_case((self.model.created_at >= seven_days_ago, 1), else_=0)
        interest_score = (
            func.coalesce(self.model.likes, 0) - func.coalesce(self.model.dislikes, 0)
        ).label("interest_score")

        stmt = (
            select(self.model)
            .options(selectinload(self.model.author))
            .order_by(
                desc(self.model.is_pinned),
                desc(is_new_case),
                desc(interest_score),
                desc(self.model.created_at)
            )
            .offset(skip)
            .limit(limit)
        )

        if resource_type:
            stmt = stmt.filter(self.model.resource_type == resource_type)

        if tags_contain:
            for tag in tags_contain:
                stmt = stmt.filter(self.model.tags.ilike(f'%{tag.strip()}%'))

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_url(self, db: AsyncSession, *, url: str) -> Optional[ResourceLink]:
        result = await db.execute(select(self.model).filter(self.model.url == url))
        return result.scalars().first()
    
    async def create_with_author(
        self, db: AsyncSession, *, obj_in: ResourceLinkCreate, author_id: Optional[int]
    ) -> ResourceLink:
        obj_in_data = obj_in.model_dump()
        # Convert Pydantic HttpUrl types to strings for DB compatibility
        if obj_in_data.get("url"):
            obj_in_data["url"] = str(obj_in_data["url"])
        if obj_in_data.get("thumbnail_url"):
            obj_in_data["thumbnail_url"] = str(obj_in_data["thumbnail_url"])

        db_obj = self.model(**obj_in_data, author_id=author_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def pin(self, db: AsyncSession, *, db_obj: ResourceLink) -> ResourceLink:
        if not db_obj.is_pinned:
            db_obj.is_pinned = True
            await self.update(db, db_obj=db_obj, obj_in={})
        return db_obj

    async def unpin(self, db: AsyncSession, *, db_obj: ResourceLink) -> ResourceLink:
        if db_obj.is_pinned:
            db_obj.is_pinned = False
            await self.update(db, db_obj=db_obj, obj_in={})
        return db_obj


resource_link = CRUDResourceLink(ResourceLink)

async def count_resources_by_author_since(db: AsyncSession, *, author_id: int, since: datetime) -> int:
    """Counts the number of resources submitted by a user since a specific datetime."""
    logger.debug(f"[CRUD ResourceLink] Counting resources for author_id:{author_id} since {since}")
    stmt = select(func.count(ResourceLink.id)).filter(
        ResourceLink.author_id == author_id,
        ResourceLink.created_at >= since
    )
    result = await db.execute(stmt)
    return result.scalar_one()

async def update_resource_link(
    db: AsyncSession,
    *, 
    db_obj: ResourceLink, 
    obj_in: ResourceLinkUpdate
) -> ResourceLink:
    """Update an existing resource link."""
    update_data = obj_in.dict(exclude_unset=True)
    
    # Convert HttpUrl to string for DB storage
    if 'url' in update_data and update_data['url'] is not None:
        update_data['url'] = str(update_data['url'])
    if 'thumbnail_url' in update_data and update_data['thumbnail_url'] is not None:
        update_data['thumbnail_url'] = str(update_data['thumbnail_url'])

    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    # We might want to update a `last_modified_at` field here if we had one
    # db_obj.last_modified_at = datetime.utcnow() 

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    logger.info(f"[CRUD ResourceLink] Resource link '{db_obj.title}' (ID: {db_obj.id}) updated.")
    return db_obj

async def delete_resource_link(db: AsyncSession, *, db_obj: ResourceLink) -> ResourceLink:
    """Delete a resource link."""
    resource_id = db_obj.id
    resource_title = db_obj.title
    await db.delete(db_obj)
    await db.commit()
    logger.info(f"[CRUD ResourceLink] Resource link '{resource_title}' (ID: {resource_id}) deleted.")
    # Common practice is to return the deleted object, None, or a success message.
    # Returning the object can be useful to show info about what was deleted.
    return db_obj # Or simply return None or True 