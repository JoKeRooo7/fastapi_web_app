from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

class UserCreateSchema(BaseModel):
    username: str = Field(..., description="Уникальное имя пользователя")
    password: str = Field(..., min_length=8, description="Пароль пользователя (не менее 8 символов)")
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    gender: str = Field(..., description="Пол пользователя")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    password: str = Field(..., min_length=8, description="Пароль пользователя (не менее 8 символов)")


class UserMatchSchema(BaseModel):
    current_id: int = Field(..., description="id текущего пользователя")
    other_id: int  = Field(..., description="id другого пользователя")


class UserListSchema(BaseModel):
    gender: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    order: Optional[Literal['asc', 'desc']] = None


class UserDataSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    registration_date: datetime 