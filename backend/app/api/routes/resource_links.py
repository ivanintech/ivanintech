from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging
from datetime import datetime, timedelta, timezone

from app import crud, schemas
from app.api import deps  # Standardized dependency import
from app.db.models.user import User # For current_user type
from app.services import gemini_service
from app.db.models.resource_link import ResourceLink
from app.db.models.resource_vote import VoteType
import google.generativeai as genai
from app.crud.crud_resource_link import count_resources_by_author_since
from app.schemas.resource_link import ResourceLinkRead, ResourceLinkCreate, ResourceLinkUpdate, ResourceLinkVoteResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=ResourceLinkRead, status_code=status.HTTP_201_CREATED)
async def create_resource_link_route(
    *,
    db: AsyncSession = Depends(deps.get_db),
    resource_link_in: ResourceLinkCreate,
    current_user: User = Depends(deps.get_current_user)
):
    """Create a new resource link after performing validations."""
    logger.info(f"[API ResourceLink] User {current_user.email} creating resource link for URL: {resource_link_in.url}")

    # --- 1. Check for duplicates ---
    existing_resource = await crud.resource_link.get_by_url(db, url=str(resource_link_in.url))
    if existing_resource:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This resource has already been added. Thank you for your contribution.",
        )

    # --- 2. Submission limit for non-admin users ---
    if not current_user.is_superuser:
        submission_limit = 3
        twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_submissions = await count_resources_by_author_since(
            db=db, author_id=current_user.id, since=twenty_four_hours_ago
        )
        if recent_submissions >= submission_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"You have reached the limit of {submission_limit} submissions per day. Please try again tomorrow!",
            )

    # --- 3. Validation and enrichment with Gemini ---
    generated_details = None
    try:
        logger.debug(f"Calling gemini_service for URL: {resource_link_in.url}")
        generated_details = await gemini_service.generate_resource_details(
            url=str(resource_link_in.url), # Ensure it's a string
            user_title=resource_link_in.title,
            user_personal_note=resource_link_in.personal_note
        )
        logger.debug(f"Received Gemini details: {generated_details}")
    except ValueError as e:
        # Catches the specific error if the content is not relevant or the JSON is invalid
        logger.warning(f"Gemini validation failed for {resource_link_in.url}: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error calling gemini_service.generate_resource_details for {resource_link_in.url}: {e}", exc_info=True)
        # Generic error if the Gemini service fails for another reason (API down, etc.)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="The AI analysis service is currently unavailable.")

    if not generated_details:
        # This shouldn't happen if the service works and doesn't raise an exception, but it's a safeguard.
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate resource details.")

    # Create a new object to avoid mutating the input, combining original and generated data
    db_obj_data = resource_link_in.model_dump(exclude_unset=True)
    db_obj_data.update(generated_details)

    if not db_obj_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not extract data from the provided URL.")

    # Convert tags to string if it's a list
    if isinstance(db_obj_data.get("tags"), list):
        db_obj_data["tags"] = ", ".join(db_obj_data["tags"])
    
    # --- 4. Add creation timestamp ---
    db_obj_data["created_at"] = datetime.now(timezone.utc)
    
    # Validate and assign thumbnail_url
    thumbnail_url_suggestion = db_obj_data.get("thumbnail_url_suggestion")
    if thumbnail_url_suggestion:
        try:
            from pydantic import HttpUrl
            HttpUrl(thumbnail_url_suggestion) # Validate
            db_obj_data["thumbnail_url"] = thumbnail_url_suggestion
        except Exception:
            logger.warning(f"AI suggested thumbnail URL is not valid: {thumbnail_url_suggestion}.")
            db_obj_data["thumbnail_url"] = None
    
    # Create the final schema instance for the DB
    db_obj_in = ResourceLinkCreate(**db_obj_data)

    logger.info(f"Final data to create ResourceLink (after Gemini): Title: '{db_obj_in.title}', Type: {db_obj_in.resource_type}")

    try:
        resource_link = await crud.resource_link.create_with_author(
            db=db, 
            obj_in=db_obj_in, 
            author_id=current_user.id
        )
        return resource_link
    except Exception as e:
        logger.error(f"[API ResourceLink] Error creating resource link '{resource_link_in.title}': {e}", exc_info=True)
        # We might want to return a more specific error if the insertion fails due to incorrect data from Gemini
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error creating resource link: {str(e)}")

@router.get("/", response_model=List[ResourceLinkRead])
async def read_resource_links_route(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    resource_type: Optional[str] = Query(None, description="Filter by resource type (e.g., Video, GitHub, Article)"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by (e.g., python,fastapi)")
):
    """Retrieve a list of resource links."""
    logger.info(f"[API ResourceLink] Reading resource links: skip={skip}, limit={limit}, type={resource_type}, tags={tags}")
    tags_list = tags.split(',') if tags else None
    db_resource_links = await crud.resource_link.get_multi(
        db=db, skip=skip, limit=limit, resource_type=resource_type, tags_contain=tags_list
    )
    return db_resource_links

@router.get("/{resource_id}", response_model=ResourceLinkRead)
async def read_resource_link_route(resource_id: str, db: AsyncSession = Depends(deps.get_db)):
    """Retrieve a specific resource link by ID."""
    logger.info(f"[API ResourceLink] Reading resource link by ID: {resource_id}")
    db_resource_link = await crud.resource_link.get(db=db, id=resource_id)
    if db_resource_link is None:
        logger.warning(f"[API ResourceLink] Resource link with ID '{resource_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource link not found")
    
    return ResourceLinkRead.model_validate(db_resource_link)

@router.put("/{resource_id}", response_model=ResourceLinkRead)
async def update_resource_link_route(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    resource_id: str,
    resource_link_in: ResourceLinkUpdate,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Update an existing resource link. Requires superuser privileges."""
    logger.info(f"[API ResourceLink] User {current_user.email} updating resource link ID: {resource_id}")
    db_resource_link = await crud.resource_link.get(db=db, id=resource_id)
    if not db_resource_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource link not found")
    
    updated_resource_link = await crud.resource_link.update(
        db=db, db_obj=db_resource_link, obj_in=resource_link_in
    )
    return updated_resource_link

@router.delete("/{resource_id}", response_model=ResourceLinkRead)
async def delete_resource_link_route(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    resource_id: str,
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Delete a resource link. Requires superuser privileges."""
    logger.info(f"[API ResourceLink] User {current_user.email} deleting resource link ID: {resource_id}")
    db_resource_link = await crud.resource_link.get(db=db, id=resource_id)
    if not db_resource_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource link not found")
    
    # The CRUDBase remove method returns the deleted object.
    deleted_resource_link = await crud.resource_link.remove(db=db, id=resource_id)
    return deleted_resource_link

@router.post("/{resource_id}/pin", response_model=ResourceLinkRead)
async def pin_resource_link_route(
    resource_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser) # Only superusers can pin
):
    """Pin a resource link. Requires superuser privileges."""
    logger.info(f"[API ResourceLink] User {current_user.email} pinning resource link ID: {resource_id}")
    db_resource_link = await crud.resource_link.get(db=db, id=resource_id)
    if not db_resource_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource link not found")
    
    pinned_link = await crud.resource_link.pin(db=db, db_obj=db_resource_link)
    logger.info(f"[API ResourceLink] Resource link {resource_id} has been pinned.")

    return pinned_link

@router.post("/{resource_id}/unpin", response_model=ResourceLinkRead)
async def unpin_resource_link_route(
    resource_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser) # Only superusers can unpin
):
    """Unpin a resource link. Requires superuser privileges."""
    logger.info(f"[API ResourceLink] User {current_user.email} unpinning resource link ID: {resource_id}")
    db_resource_link = await crud.resource_link.get(db=db, id=resource_id)
    if not db_resource_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource link not found")

    unpinned_link = await crud.resource_link.unpin(db=db, db_obj=db_resource_link)
    logger.info(f"[API ResourceLink] Resource link {resource_id} has been unpinned.")
    
    return unpinned_link

@router.post(
    "/{resource_id}/like",
    response_model=ResourceLinkVoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Like a resource link"
)
async def like_resource_link_route(
    resource_id: str = Path(..., description="The ID of the resource link to like"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Adds a 'like' vote to a resource link. If the user has already disliked it, the dislike is removed.
    """
    db_resource_link = await crud.resource_link.get(db=db, id=resource_id)
    if not db_resource_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource link not found")
    
    updated_link = await crud.resource_vote.add_vote(
        db, 
        resource_id=db_resource_link.id, 
        user_id=current_user.id, 
        vote_type=VoteType.LIKE
    )
    return {
        "message": "Like vote added successfully.",
        "likes": updated_link.likes,
        "dislikes": updated_link.dislikes,
    }

@router.post(
    "/{resource_id}/dislike",
    response_model=ResourceLinkVoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Dislike a resource link"
)
async def dislike_resource_link_route(
    resource_id: str = Path(..., description="The ID of the resource link to dislike"),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Adds a 'dislike' vote to a resource link. If the user has already liked it, the like is removed.
    """
    db_resource_link = await crud.resource_link.get(db=db, id=resource_id)
    if not db_resource_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource link not found")
    
    updated_link = await crud.resource_vote.add_vote(
        db, 
        resource_id=db_resource_link.id, 
        user_id=current_user.id, 
        vote_type=VoteType.DISLIKE
    )
    return {
        "message": "Dislike vote added successfully.",
        "likes": updated_link.likes,
        "dislikes": updated_link.dislikes,
    }