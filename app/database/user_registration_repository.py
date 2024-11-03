from datetime import datetime
from fastapi import HTTPException, UploadFile
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from security.hashing import hash_password

from model.tables import (
    UserAccounts, 
    UserMails, 
    UserNames, 
    UserAvatars, 
)
from schemas.users import ( 
    UserCreateSchema
)

class UserRegistrationRepository:
    async def _check_existing_user(self, email: str, session: AsyncSession):
        result = await session.execute(select(UserMails).filter_by(email=email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Почта уже зарегистрирована!")

    async def _create_user_records(self, user: UserCreateSchema):
        hashed_password = await hash_password(user.password)
        user_account = UserAccounts(username=user.username, hashed_password=hashed_password, created_at=datetime.now())
        user_mail = UserMails(email=user.email)
        user_name = UserNames(first_name=user.first_name, last_name=user.last_name, gender=user.gender)
        return user_account, user_mail, user_name
    
    async def _add_records_to_db(self, session: AsyncSession, user_account, user_mail, user_name, avatar_path):
        session.add(user_account)
        await session.flush()
        user_mail.user_id = user_account.id
        user_name.user_id = user_mail.user_id
        session.add(user_mail)
        session.add(user_name)
        user_avatar = UserAvatars(user_id=user_mail.user_id, avatar_way=avatar_path)
        session.add(user_avatar)
        await session.commit()


    async def register_user(self, user: UserCreateSchema, avatar_path: UploadFile, session: AsyncSession):
        try:
            await self._check_existing_user(user.email, session)
            user_account, user_mail, user_name = await self._create_user_records(user)
            await self._add_records_to_db(session, user_account, user_mail, user_name, avatar_path)        
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except Exception as e:
            await session.rollback()  # Откат при ошибке
            raise HTTPException(status_code=500, detail="Ошибка при сохранении данных")

        return user.username, user.email