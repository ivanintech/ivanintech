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

logger = logging.getLogger(__name__)

async def create_resource_link(db: AsyncSession, *, resource_link_in: ResourceLinkCreate, author_id: Optional[int]) -> ResourceLink:
    """Create a new resource link."""
    
    db_obj_data = resource_link_in.dict(exclude_unset=True) # Use exclude_unset to only get provided fields
    
    if 'url' in db_obj_data and db_obj_data['url'] is not None:
        db_obj_data['url'] = str(db_obj_data['url'])
    if 'thumbnail_url' in db_obj_data and db_obj_data['thumbnail_url'] is not None:
        db_obj_data['thumbnail_url'] = str(db_obj_data['thumbnail_url'])

    # Explicitly set created_at and updated_at (if you add it to your model later)
    # This overrides any potential issues with func.now() in SQLite async or model defaults not firing as expected.
    current_time = datetime.now(timezone.utc)

    db_obj = ResourceLink(
        **db_obj_data,
        id=str(uuid.uuid4().hex), # Ensure ID is always generated if not part of model default effectively
        created_at=current_time,
        author_id=author_id
        # If you add an updated_at field to your ResourceLink model, set it here too:
        # updated_at=current_time 
    )
    
    db.add(db_obj)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"[CRUD ResourceLink] Error committing new resource link (title: {resource_link_in.title}): {e}", exc_info=True)
        raise
    await db.refresh(db_obj)
    logger.info(f"[CRUD ResourceLink] Resource link '{db_obj.title}' (ID: {db_obj.id}) created.")
    return db_obj

async def get_resource_link(db: AsyncSession, resource_link_id: str) -> Optional[ResourceLink]:
    """Get a single resource link by ID."""
    logger.debug(f"[CRUD ResourceLink] Getting resource link by ID: {resource_link_id}")
    return await db.get(ResourceLink, resource_link_id, options=[selectinload(ResourceLink.author)])

async def get_resource_link_by_url(db: AsyncSession, *, url: str) -> Optional[ResourceLink]:
    """Get a single resource link by URL."""
    logger.debug(f"[CRUD ResourceLink] Getting resource link by URL: {url}")
    stmt = select(ResourceLink).filter(ResourceLink.url == url)
    result = await db.execute(stmt)
    return result.scalars().first()

async def count_resources_by_author_since(db: AsyncSession, *, author_id: int, since: datetime) -> int:
    """Counts the number of resources submitted by a user since a specific datetime."""
    logger.debug(f"[CRUD ResourceLink] Counting resources for author_id:{author_id} since {since}")
    stmt = select(func.count(ResourceLink.id)).filter(
        ResourceLink.author_id == author_id,
        ResourceLink.created_at >= since
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_resource_links(
    db: AsyncSession, skip: int = 0, limit: int = 100, resource_type: Optional[str] = None, tags_contain: Optional[List[str]] = None
) -> List[ResourceLink]:
    """
    Retrieve a list of resource links with advanced sorting:
    1. Pinned resources first.
    2. New resources (last 7 days) next.
    3. The rest, sorted by an interest score (likes - dislikes).
    """
    logger.debug(f"[CRUD ResourceLink] Getting list of resource links with advanced sorting.")
    
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    
    # CASE expression to determine if a resource is "new"
    is_new_case = sa_case((ResourceLink.created_at >= seven_days_ago, 1), else_=0)
    
    # Interest score
    interest_score = (ResourceLink.likes - ResourceLink.dislikes).label("interest_score")

    stmt = (
        select(ResourceLink)
        .options(selectinload(ResourceLink.author))
        .order_by(
            desc(ResourceLink.is_pinned), # 1. Pinned first
            desc(is_new_case),             # 2. New ones next
            desc(interest_score),          # 3. Rest by interest
            desc(ResourceLink.created_at)  # Tie-breaker by date
        )
        .offset(skip)
        .limit(limit)
    )
    
    if resource_type:
        stmt = stmt.filter(ResourceLink.resource_type == resource_type)
    
    if tags_contain:
        for tag in tags_contain:
            stmt = stmt.filter(ResourceLink.tags.ilike(f'%{tag.strip()}%')) 
            
    result = await db.execute(stmt)
    resources = result.scalars().all()
    logger.debug(f"[CRUD ResourceLink] Found {len(resources)} resource links.")
    return resources

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

# --- Pinning Functions ---
async def pin_resource(db: AsyncSession, db_obj: ResourceLink) -> ResourceLink:
    """Marks a resource link as pinned."""
    if not db_obj.is_pinned:
        db_obj.is_pinned = True
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"[CRUD ResourceLink] Resource '{db_obj.title}' (ID: {db_obj.id}) pinned.")
    return db_obj

async def unpin_resource(db: AsyncSession, db_obj: ResourceLink) -> ResourceLink:
    """Unmarks a resource link as pinned."""
    if db_obj.is_pinned:
        db_obj.is_pinned = False
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"[CRUD ResourceLink] Resource '{db_obj.title}' (ID: {db_obj.id}) unpinned.")
    return db_obj