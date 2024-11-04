from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.users import (
    UserLocationSchema,
    UserLoginSchema,
    UserDataSchema,
    UserListSchema, 
)

from model.tables import (
    UserAccounts, 
    UserMails, 
    UserNames,
    UserLocations
)

class UserInfoRepository:
    async def get_user_data_by_email(self, user: UserLoginSchema, session: AsyncSession):
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

    async def get_user_list(self, data: UserListSchema, session):
        query = select(UserAccounts.id, 
            UserNames.first_name, 
            UserNames.last_name, 
            UserAccounts.created_at).join(
                UserNames, UserNames.user_id == UserAccounts.id)

        filters = []
        if data.gender:
            filters.append(UserNames.gender==data.gender)
        if data.first_name:
            filters.append(UserNames.first_name==data.first_name)
        if data.first_name:
            filters.append(UserNames.last_name==data.last_name)
        if filters:
            query = query.where(and_(*filters))

        if data.order:
            if data.order == 'asc':
                query = query.order_by(UserAccounts.created_at.asc())
            elif data.order == "desc":
                query = query.order_by(UserAccounts.created_at.desc())
        result = await session.execute(query)
        users = result.fetchall()  # Получаем список пользователей
        if not users:
            raise HTTPException(status_code=404, detail="Пользователи не найдены")


        return [
            UserDataSchema(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                registration_date=user.created_at
            ) for user in users]

    async def get_user_coordinates_by_id(self, id: int, session: AsyncSession):
        query = select(
                UserLocations.user_id, 
                UserLocations.longitude, 
                UserLocations.latitude
            ).filter(
                UserLocations.user_id==id
            ).order_by(
                UserLocations.created_at.desc()
            ).limit(1)
    
        result = await session.execute(query)
        locations = result.fetchall()

        if not locations: 
           return None
    
        location = locations[0]
        return UserLocationSchema(
            id=location.user_id,
            latitude=location.latitude,
            longitude=location.longitude
        )