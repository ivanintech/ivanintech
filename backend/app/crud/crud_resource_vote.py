from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.db.models.resource_vote import ResourceVote, VoteType
from app.db.models.resource_link import ResourceLink
from app.db.models.user import User
from app.schemas.resource_link import ResourceLinkVoteResponse
from app.crud.base import CRUDBase
from app.schemas.resource_link import ResourceLinkUpdate  # Assuming this exists

# Vote limits per day
DAILY_LIKE_LIMIT = 5
DAILY_DISLIKE_LIMIT = 2
AUTODELETE_DISLIKE_THRESHOLD = 3


class CRUDResourceVote(CRUDBase[ResourceVote, None, None]):  # No standard schemas
    async def get_vote_by_user_for_resource(
        self, db: AsyncSession, *, user_id: int, resource_link_id: str
    ) -> ResourceVote | None:
        stmt = select(self.model).filter(
            self.model.user_id == user_id,
            self.model.resource_link_id == resource_link_id,
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_daily_vote_counts(
        self, db: AsyncSession, *, user_id: int
    ) -> tuple[int, int]:
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        stmt = select(
            func.count(func.nullif(self.model.vote_type != VoteType.like, True)),
            func.count(func.nullif(self.model.vote_type != VoteType.dislike, True)),
        ).filter(
            self.model.user_id == user_id,
            self.model.created_at >= twenty_four_hours_ago,
        )
        result = await db.execute(stmt)
        return result.one()

    async def vote_on_resource(
        self, db: AsyncSession, *, user: User, resource: ResourceLink, vote_type: VoteType
    ) -> ResourceLinkVoteResponse:
        existing_vote = await self.get_vote_by_user_for_resource(
            db, user_id=user.id, resource_link_id=resource.id
        )
        message = ""

        if existing_vote:
            if existing_vote.vote_type == vote_type:
                raise PermissionError(f"You have already voted '{vote_type.name}'.")
            
            if existing_vote.vote_type == VoteType.like:
                resource.likes = max(0, resource.likes - 1)
            else:
                resource.dislikes = max(0, resource.dislikes - 1)
            existing_vote.vote_type = vote_type
            db.add(existing_vote)
            message = "Your vote has been updated."
        else:
            likes, dislikes = await self.get_daily_vote_counts(db, user_id=user.id)
            if vote_type == VoteType.like and likes >= DAILY_LIKE_LIMIT:
                raise PermissionError(f"Daily limit of {DAILY_LIKE_LIMIT} 'likes' reached.")
            if vote_type == VoteType.dislike and dislikes >= DAILY_DISLIKE_LIMIT:
                raise PermissionError(f"Daily limit of {DAILY_DISLIKE_LIMIT} 'dislikes' reached.")
            
            new_vote = self.model(
                user_id=user.id, resource_link_id=resource.id, vote_type=vote_type
            )
            db.add(new_vote)
            message = "Thank you for your vote!"

        if vote_type == VoteType.like:
            resource.likes += 1
        else:
            resource.dislikes += 1
        db.add(resource)
        
        if (
            resource.dislikes >= AUTODELETE_DISLIKE_THRESHOLD
            and resource.dislikes > resource.likes
        ):
            await db.delete(resource)
            await db.commit()
            raise PermissionError("This resource has been removed due to negative feedback.")

        await db.commit()
        await db.refresh(resource)

        return ResourceLinkVoteResponse(
            message=message,
            likes=resource.likes,
            dislikes=resource.dislikes,
            user_vote=vote_type,
        )


resource_vote = CRUDResourceVote(ResourceVote)
