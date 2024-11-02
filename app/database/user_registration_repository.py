from datetime import datetime
from fastapi import HTTPException, UploadFile
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from security.hashing import hash_password
from services.watermark import AvatarHandler

from model.tables import (
    UserAccounts, 
    UserMails, 
    UserNames, 
    UserAvatars, 
)
from schemas.users import ( 
    UserCreateSchema, 
    UserLogin,
)

class UserRegistrationRepository:
    # убрать и разделить
    def __init__(self, avatar_service: AvatarHandler):
        self._avatar_service = avatar_service

    async def _check_existing_user(self, email: str, session: AsyncSession):
        result = await session.execute(select(UserMails).filter_by(email=email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Почта уже зарегистрирована!")

    async def _create_user_records(self, user: UserCreateSchema):
        hashed_password = await hash_password(user.password)
        user_account = UserAccounts(username=user.username, hashed_password=hashed_password, created_at=datetime.now())
        user_mail = UserMails(email=user.email, gender=user.gender)
        user_name = UserNames(first_name=user.first_name, last_name=user.last_name)
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


    async def get_user_data_by_email(self, user: UserLogin, session: AsyncSession):
        results = await session.execute(
                select(UserAccounts.id, UserAccounts.username, UserAccounts.hashed_password, UserMails.email)
                .join(UserMails, UserAccounts.id == UserMails.user_id)
                .filter(UserMails.email == user.email)
            )
        user_data = results.first() 

        if not user_data:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        return user_data.id, user_data.username, user_data.hashed_password, user_data.email

    async def get_user_names_by_id(self, id: int, session: AsyncSession):
        results = await session.execute(
                select(UserNames.user_id, UserNames.first_name, UserMails.email)
                .join(UserMails, UserNames.user_id == UserMails.user_id)
                .filter(UserMails.user_id == id)
            )
        user_data = results.first() 
        if not user_data:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        return user_data.user_id, user_data.first_name, user_data.email

    async def register_user(self, user: UserCreateSchema, avatar: UploadFile, session: AsyncSession):
        await self._check_existing_user(user.email, session)
        try:
            user_account, user_mail, user_name = await self._create_user_records(user)
        except:
            raise HTTPException(status_code=500, detail="Ошибка при создании записи")

        try:
            # убрать в запрос и сюда только путь
            avatar_path = await self._avatar_service.save_avatar_file(avatar)
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=400, detail="Ошибка: {e}")

        try:
            await self._add_records_to_db(session, user_account, user_mail, user_name, avatar_path)
        except Exception as e:
            await session.rollback()  # Откат при ошибке
            self._avatar_service.delete_avatar(avatar_path)
            raise HTTPException(status_code=500, detail="Ошибка при сохранении данных")

        return user.username, user.email