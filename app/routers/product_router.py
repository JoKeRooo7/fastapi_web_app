from typing import Optional
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
from services.distance import DistanceCalculator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    Form,
    HTTPException,
    status,
)
from schemas.tokens import TokenSchema
from schemas.response import (
    UserListDataResponseSchema,
    UserDataResponseSchema,
)
from schemas.users import (
    UserLocationSchema,
    UserCreateSchema,
    UserLoginSchema,
    UserListSchema,
    UserDataSchema,
)


router = APIRouter()
database = DatabaseManager()
avatar_service = AvatarHandler()
user_info_repository = UserInfoRepository()
registration_repository = UserRegistrationRepository()
user_likes_repository = UserLikeRepository()
redis_service = RedisService()
authenticator = TokenAuthenticator()
distance_services = DistanceCalculator()


@router.post("/api/clients/create")
async def register_user(
    username: str = Form(...),
    password: str = Form(...),
    email: EmailStr = Form(...),
    gender: Optional[str] = Form(None),
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    avatar: UploadFile = File(None),
    session: AsyncSession = Depends(database.get_db)
) -> UserDataResponseSchema:

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
    username, email = await registration_repository.register_user(
        user,
        avatar_path,
        session
    )
    return UserDataResponseSchema(
        username=username,
        email=email,
        message="Пользователь успешно зарегистрирован"
    )


@router.post("/api/login")
async def login(
    user: UserLoginSchema,
    session: AsyncSession = Depends(database.get_db)
) -> TokenSchema:

    id, username, password, email = await \
        user_info_repository.get_user_data_by_email(user, session)
    if not await verify_password(user.password, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await authenticator.create_access_token(
        data={"id": id, "username": username, "email": email})
    return TokenSchema(
        access_token=access_token,
        token_type="barrer",
    )


@router.post("/api/clients/{id}/match")
async def match_client(
    id: int,
    token: str = Depends(auth_scheme),
    session: AsyncSession = Depends(database.get_db)
) -> UserDataResponseSchema:

    current_id, current_username, current_email = await \
        TokenAuthenticator().get_current_user(token)
    rating_count = await redis_service.get_rating_count(current_id)
    message = "Лайк!"
    if rating_count > settings.DAILY_RATING_LIMIT:
        raise HTTPException(
            status_code=403,
            detail=f"Лимит оценок на сегодня достигнут"
        )
    else:
        match = await user_likes_repository.add_like(current_id, id, session)
        if match:
            _, first_name, email = await \
                user_info_repository.get_user_names_by_id(id, session)
            message = f"Выпонравились <{first_name}>! \
                Почта участника: <{email}>"
        await redis_service.increment_rating_count(current_id)
    return UserDataResponseSchema(
        username=current_username,
        email=current_email,
        message=message
    )


async def _calculate_distance_and_filter(
        id: int,
        distance, float,
        data: UserDataSchema,
        session: AsyncSession = Depends(database.get_db)
) -> list:

    main_coordinates = await \
        user_info_repository.get_user_coordinates_by_id(
            id,
            session
        )
    filtered_data = []
    for user in data:
        user_coordinates = await \
            user_info_repository.get_user_coordinates_by_id(
                user.id,
                session
            )
        if not user_coordinates:
            continue

        if await distance_services.is_within_distance(
            latitude_first=main_coordinates.latitude,
            longitude_first=main_coordinates.longitude,
            latitude_second=user_coordinates.latitude,
            longitude_second=user_coordinates.longitude,
            max_distance_km=distance
        ):
            filtered_data.append(
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
            )
    return filtered_data


@router.get("/api/list")
async def get_user_list(
    data: UserListSchema,
    token: str = Depends(auth_scheme),
    session: AsyncSession = Depends(database.get_db)
) -> UserListDataResponseSchema:

    id, _, _ = await TokenAuthenticator().get_current_user(token)
    try:
        result = await user_info_repository.get_user_list(data, session)
        if data.distance:
            cashe_key = f"user_id:{id}/distance:{data.distance}"
            cached_result = await redis_service.get_cached_data(cashe_key)
            if cached_result:
                return UserListDataResponseSchema(
                    user_list=[
                        UserDataSchema(**cash) for cash in cached_result
                    ]
                )
            filtered_data = _calculate_distance_and_filter(
                id,
                data.distance,
                result
            )
            await redis_service.set_cached_data(cashe_key, filtered_data)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception:
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка")
    return UserListDataResponseSchema(user_list=result)


@router.post("/api/coordinates/create")
async def add_location(
    coordinates: UserLocationSchema,
    token: str = Depends(auth_scheme),
    session: AsyncSession = Depends(database.get_db)
) -> UserDataResponseSchema:

    id, username, email = await TokenAuthenticator().get_current_user(token)
    coordinates.id = id
    await registration_repository.add_coordinates(
        coordinates=coordinates,
        session=session
    )
    return UserDataResponseSchema(
        username=username,
        email=email,
        message="Координаты успешно добавлены"
    )
