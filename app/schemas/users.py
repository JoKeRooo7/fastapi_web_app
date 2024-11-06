from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal


class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: EmailStr
    gender: str
    first_name: str
    last_name: str


class UserCreateRequest(BaseModel):
    data: UserCreateSchema


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(
        ..., description="Электронная почта пользователя"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Пароль пользователя (не менее 8 символов)"
    )


class UserListSchema(BaseModel):
    gender: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    order: Optional[Literal['asc', 'desc']] = None
    distance: Optional[float] = None


class UserDataSchema(BaseModel):
    id: int
    first_name: str
    last_name: str


class UserLocationSchema(BaseModel):
    id: int = None
    latitude: float
    longitude: float
