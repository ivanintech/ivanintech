from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from app.db.models.resource_vote import ResourceVote, VoteType
from app.db.models.resource_link import ResourceLink
from app.db.models.user import User

# Vote limits per day
DAILY_LIKE_LIMIT = 5
DAILY_DISLIKE_LIMIT = 2
AUTODELETE_DISLIKE_THRESHOLD = 3

async def get_vote_by_user_for_resource(db: AsyncSession, *, user_id: int, resource_link_id: str) -> ResourceVote | None:
    """Checks if a user has already voted for a specific resource."""
    stmt = select(ResourceVote).filter(
        ResourceVote.user_id == user_id,
        ResourceVote.resource_link_id == resource_link_id
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_daily_vote_counts(db: AsyncSession, *, user_id: int) -> tuple[int, int]:
    """Counts the likes and dislikes a user has cast in the last 24 hours."""
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    stmt = select(
        func.count(func.nullif(ResourceVote.vote_type != VoteType.like, True)),
        func.count(func.nullif(ResourceVote.vote_type != VoteType.dislike, True))
    ).filter(
        ResourceVote.user_id == user_id,
        ResourceVote.created_at >= twenty_four_hours_ago
    )
    result = await db.execute(stmt)
    return result.one()


async def add_vote(
    db: AsyncSession, *, user: User, resource_link: ResourceLink, vote_type: VoteType
) -> tuple[ResourceLink, str]:
    """
    Adds a vote to a resource, updates counters, and handles auto-delete logic.
    Returns the updated resource and a status message.
    """
    # 1. Check if the user has already voted for this resource
    existing_vote = await get_vote_by_user_for_resource(db, user_id=user.id, resource_link_id=resource_link.id)
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            return resource_link, f"You have already given '{vote_type.name}' to this resource."
        else:
            # Change the vote (e.g., from dislike to like)
            # First, revert the previous counter
            if existing_vote.vote_type == VoteType.like:
                resource_link.likes -= 1
            else:
                resource_link.dislikes -= 1
            
            existing_vote.vote_type = vote_type
            vote = existing_vote
            message = "Your vote has been updated."
    else:
        # 2. Check daily limits if it's a new vote
        likes_today, dislikes_today = await get_daily_vote_counts(db, user_id=user.id)
        if vote_type == VoteType.like and likes_today >= DAILY_LIKE_LIMIT:
            raise PermissionError(f"You have reached the limit of {DAILY_LIKE_LIMIT} 'likes' per day.")
        if vote_type == VoteType.dislike and dislikes_today >= DAILY_DISLIKE_LIMIT:
            raise PermissionError(f"You have reached the limit of {DAILY_DISLIKE_LIMIT} 'dislikes' per day.")
            
        vote = ResourceVote(user_id=user.id, resource_link_id=resource_link.id, vote_type=vote_type)
        message = "Thanks for your vote!"

    # 3. Update the resource's counters
    if vote_type == VoteType.like:
        resource_link.likes += 1
    else:
        resource_link.dislikes += 1

    db.add(vote)
    db.add(resource_link)
    await db.flush()

    # 4. Check auto-delete logic
    if vote_type == VoteType.dislike and \
       resource_link.dislikes >= AUTODELETE_DISLIKE_THRESHOLD and \
       resource_link.dislikes > resource_link.likes:
        
        await db.delete(resource_link)
        await db.commit()
        # Return None to indicate the resource was deleted
        return None, "The resource has been deleted due to a high rate of negative votes."

    await db.commit()
    await db.refresh(resource_link)
    
    return resource_link, message
