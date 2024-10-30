import os
import uuid
import shutil
from datetime import datetime

from fastapi import HTTPException, UploadFile
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from database_model.tables import UserAccounts, UserMails, UserNames, UserAvatars
from security.hashing import hash_password
from serivces.watermark import add_watermark
from models.validation import UserCreate
from settings import settings

async def _check_existing_user(email: str, session: AsyncSession):
    result = await session.execute(select(UserMails).filter_by(email=email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Почта уже зарегистрирована!")


async def _create_user_records(user: UserCreate, hashed_password: str):
    user_account = UserAccounts(username=user.username, hashed_password=hashed_password, created_at=datetime.now())
    user_mail = UserMails(email=user.email, gender=user.gender)
    user_name = UserNames(first_name=user.first_name, last_name=user.last_name)
    return user_account, user_mail, user_name


async def _save_avatar_file(user_avatar_file:UploadFile, username: str):
    file_extension = user_avatar_file.filename.split('.')[-1]
    unique_filename = f"{username}_avatar_{uuid.uuid4()}.{file_extension}"
    avatar_path = settings.avatars_path + unique_filename

    with open(avatar_path, "wb") as wf:
        shutil.copyfileobj(user_avatar_file.file, wf)
        user_avatar_file.file.close()

    return avatar_path


async def _add_records_to_db(session: AsyncSession, user_account, user_mail, user_name, avatar_path):
    session.add(user_account)
    await session.flush()
    user_mail.user_id = user_account.id
    user_name.user_id = user_mail.user_id 
    session.add(user_mail)
    session.add(user_name)
    user_avatar = UserAvatars(user_id=user_mail.user_id, avatar_way=avatar_path)
    session.add(user_avatar)
    
    await session.commit() 


async def create_user(user: UserCreate, avatar:UploadFile, session: AsyncSession):
    await _check_existing_user(user.email, session)

    hashed_password = await hash_password(user.password)
    user_account, user_mail, user_name = await _create_user_records(user, hashed_password)
    
    try:
        avatar_path = await _save_avatar_file(avatar, user.username)
        await add_watermark(avatar_path)

    except Exception as e:
        if os.path.exists(avatar_path):
            os.remove(avatar_path)
        raise HTTPException(status_code=500, detail="Ошибка при сохранении файла: {}".format(e))

    # await _add_records_to_db(session, user_account, user_mail, user_name, avatar_path)
    # await session.commit() 
    try:
        await _add_records_to_db(session, user_account, user_mail, user_name, avatar_path)
    except Exception as e:
        if os.path.exists(avatar_path):
            os.remove(avatar_path)
        await session.rollback()  # Откат при ошибке
        raise HTTPException(status_code=500, detail="Ошибка при создании пользователя: {}".format(e))

    return user.username, user.email
