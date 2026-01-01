from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import User
from core.exceptions import EntityNotFoundException


class UserResolver:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_id(self, firebase_uid: str) -> int:
        stmt = select(User).where(User.firebase_uid == firebase_uid)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise EntityNotFoundException(f"User {firebase_uid} not found")

        return user.id
