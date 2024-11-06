from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.future import select
from model.tables import UserLikes


class UserLikeRepository:
    async def _check_correct_db_request(
        self,
        user_id: int,
        other_user_id: int,
        session
    ):
        if user_id == other_user_id:
            raise HTTPException(status_code=400, detail="Лайкнул себя")
        existing_like = await session.execute(
            select(
                UserLikes
            ).where(
                UserLikes.user_id == user_id,
                UserLikes.other_user_id == other_user_id
            )
        )
        if existing_like.scalars().first():
            raise HTTPException(status_code=400, detail="Лайк уже существует")

    async def add_like(
        self,
        user_id: int,
        other_user_id: int,
        session
    ):
        await self._check_correct_db_request(user_id, other_user_id, session)
        new_like = UserLikes(
            user_id=user_id,
            other_user_id=other_user_id,
            liked_at=datetime.now()
        )
        session.add(new_like)

        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(
                status_code=500,
                detail="Не удалось добавить лайк"
            )

        mutual_like_exists = await self._check_mutual_like(
            user_id,
            other_user_id,
            session
        )

        if mutual_like_exists:
            await self._remove_mutual_likes(user_id, other_user_id, session)
            return True
        return False

    async def _check_mutual_like(
        self,
        user_id: int,
        other_user_id: int,
        session
    ) -> bool:
        result = await session.execute(
            select(
                UserLikes
            ).where(
                UserLikes.user_id == other_user_id,
                UserLikes.other_user_id == user_id
            )
        )
        return result.scalars().first() is not None

    async def _remove_mutual_likes(
        self,
        user_id: int,
        other_user_id: int,
        session
    ):
        await session.execute(
            select(
                UserLikes
            ).where(
                UserLikes.user_id == other_user_id,
                UserLikes.other_user_id == user_id
            )
        )
        await session.commit()
