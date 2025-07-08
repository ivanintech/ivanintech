from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
import datetime

from app import crud
from app.api import deps
from app.db.models.user import User
from app.schemas.blog_suggestion import BlogSuggestionRead
from app.schemas.blog import BlogPostCreate, BlogPostRead

router = APIRouter()

@router.get("/", response_model=List[BlogSuggestionRead])
async def read_suggestions(
    db: deps.SessionDep,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Retrieve all pending blog suggestions. Superuser only.
    """
    suggestions = await crud.blog_suggestion.get_multi(db, skip=skip, limit=limit, criteria={"status": "pending"})
    return suggestions

@router.post("/{suggestion_id}/publish", response_model=BlogPostRead)
async def publish_suggestion(
    suggestion_id: str,
    db: deps.SessionDep,
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Publish a blog suggestion. This creates a new blog post from the suggestion
    and updates the suggestion's status. Superuser only.
    """
    suggestion = await crud.blog_suggestion.get(db, id=suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    if suggestion.status != 'pending':
        raise HTTPException(status_code=400, detail=f"Suggestion is already {suggestion.status}")

    # Create a blog post from the suggestion
    blog_post_in = BlogPostCreate(
        title=suggestion.title,
        content=suggestion.content,
        excerpt=suggestion.excerpt,
        author_id=current_user.id,
        published_date=datetime.date.today(),
        tags=suggestion.tags,
        image_url=str(suggestion.image_url) if suggestion.image_url else None,
        status='published',
        # Generate a slug from the title
        slug=suggestion.title.lower().replace(' ', '-').replace(':', '').replace('?', '')[:50]
    )
    
    new_post = await crud.blog_post.create_with_author(db, obj_in=blog_post_in, author_id=current_user.id)

    # Update the suggestion status
    suggestion.status = 'published'
    suggestion.processed_at = datetime.datetime.now(datetime.timezone.utc)
    suggestion.published_post_id = new_post.id
    db.add(suggestion)
    await db.commit()
    
    return new_post

@router.delete("/{suggestion_id}", response_model=BlogSuggestionRead)
async def reject_suggestion(
    suggestion_id: str,
    db: deps.SessionDep,
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Reject (delete) a blog suggestion. Superuser only.
    """
    suggestion = await crud.blog_suggestion.get(db, id=suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    # Instead of deleting, we can also just update the status to 'rejected'
    suggestion.status = 'rejected'
    suggestion.processed_at = datetime.datetime.now(datetime.timezone.utc)
    db.add(suggestion)
    await db.commit()
    await db.refresh(suggestion)

    return suggestion 