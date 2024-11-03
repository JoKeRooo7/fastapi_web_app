from typing import Optional, Literal
from pydantic import EmailStr
from security.auth import TokenAuthenticator, auth_scheme
from security.hashing import verify_password
from settings import settings
from database.database_handler import DatabaseManager
from database.user_like_repository import UserLikeRepository
from database.user_info_repository import UserInfoRepository
from database.user_registration_repository import UserRegistrationRepository
from services.watermark import AvatarHandler, AvatarError
from services.redis_services import RedisService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    APIRouter, 
    Depends, 
    File, 
    UploadFile, 
    Form, 
    HTTPException, 
    status,
    Query,
)
from schemas.tokens import TokenSchema
from schemas.response import (
    UserListDataResponseSchema,
    UserDataResponseSchema,
)

from schemas.users import (
    UserCreateSchema,
    UserLoginSchema,
    UserListSchema,
)


router = APIRouter()
database = DatabaseManager()
avatar_service = AvatarHandler()
user_info_repository = UserInfoRepository()
registration_repository = UserRegistrationRepository()
user_likes_repository = UserLikeRepository()
redis_service = RedisService()
authenticator = TokenAuthenticator()



@router.post("/api/clients/create")
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    email: EmailStr = Form(...),
    gender: Optional[str] = Form(None),
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    avatar: UploadFile = File(None), session: AsyncSession=Depends(database.get_db)):

    user = UserCreateSchema(
        username=username,
        password=password,
        email=email,
        gender=gender,
        first_name=first_name,
        last_name=last_name
    )
    try:
        avatar_path = await avatar_service.save_avatar_file(avatar)
    except AvatarError as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")
    username, email = await registration_repository.register_user(user, avatar_path, session)
    return UserDataResponseSchema(
        username=username,
        email=email,
        message="Пользователь успешно зарегистрирован"
    )


@router.post("/api/login")
async def login(
    email: EmailStr = Form(...),
    password: str = Form(...),
    session: AsyncSession=Depends(database.get_db)):
    # print(f"\n{email}, {password}\n")
    user = UserLoginSchema(email=email, password=password)
    id, username, password, email = await user_info_repository.get_user_data_by_email(user, session)
    if not await verify_password(user.password, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await authenticator.create_access_token(data={"id": id, "username": username, "email": email})
    return TokenSchema(
        access_token=access_token,
        token_type="barrer",
    )


@router.post("/api/clients/{id}/match")
async def match_client(
    id: int,
    token: str = Depends(auth_scheme),
    session: AsyncSession=Depends(database.get_db)):

    current_id, current_username, current_email = await TokenAuthenticator().get_current_user(token)
    rating_count = await redis_service.get_rating_count(current_id)
    message="Лайк!"
    if rating_count > settings.DAILY_RATING_LIMIT:
        message="Лимит оценок на сегодня достигнут"
    else:
        match = await user_likes_repository.add_like(current_id, id, session)
        if match:
            _, first_name, email = await user_info_repository.get_user_names_by_id(id, session)  
            message=f"Выпонравились <{first_name}>! Почта участника: <{email}>"
        await redis_service.increment_rating_count(current_id)
    return UserDataResponseSchema(
        username=current_username,
        email=current_email,
        message=message
    )

@router.post("/api/clients/create")
async def match_client(
    token: str = Depends(auth_scheme),
    session: AsyncSession=Depends(database.get_db)):

    current_id, current_username, current_email = await TokenAuthenticator().get_current_user(token)
    rating_count = await redis_service.get_rating_count(current_id)
    message="Лайк!"
    if rating_count > settings.DAILY_RATING_LIMIT:
        message="Лимит оценок на сегодня достигнут"
    else:
        match = await user_likes_repository.add_like(current_id, id, session)
        if match:
            _, first_name, email = await registration_repository.get_user_names_by_id(id, session)  
            message=f"Выпонравились <{first_name}>! Почта участника: <{email}>"
        await redis_service.increment_rating_count(current_id)
    return UserDataResponseSchema(
        username=current_username,
        email=current_email,
        message=message
    )


@router.get("/api/list")
async def get_user_list(
    gender: Optional[str] = Query(None),
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    order: Optional[Literal['asc', 'desc']] = Query(None),
    token: str = Depends(auth_scheme),
    session: AsyncSession=Depends(database.get_db)):
    
    data = UserListSchema(
        gender=gender,
        first_name=first_name,
        last_name=last_name,
        order=order
    )
    
    await TokenAuthenticator().get_current_user(token)
    try:
        result = await user_info_repository.get_user_list(data, session)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except:
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка")
    return UserListDataResponseSchema(user_list=result)
